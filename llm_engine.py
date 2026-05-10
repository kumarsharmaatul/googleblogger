"""
LLM Engine — Gemini + MCP Agentic Loop
Uses FastMCP in-process tools so Gemini can:
  • search_web        — Fetch latest info from DuckDuckGo
  • get_recent_posts  — Fetch recent blog posts for internal linking
  • publish_blog      — (available but not called; app.py handles publishing)
"""

import os
import json
import asyncio
from google import genai
from google.genai import types
from dotenv import load_dotenv

from mcp_server import mcp as mcp_instance

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def load_system_prompt() -> str:
    prompt_path = "AGENTS.md"
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    return "You are an SEO Blogging Agent."


def _json_type_to_gemini(json_type: str) -> str:
    return {
        "string": "STRING",
        "integer": "INTEGER",
        "number": "NUMBER",
        "boolean": "BOOLEAN",
        "array": "ARRAY",
        "object": "OBJECT",
    }.get(json_type, "STRING")


async def _build_gemini_tools() -> list[types.FunctionDeclaration]:
    """Convert FastMCP tool definitions → Gemini FunctionDeclaration list."""
    mcp_tools = await mcp_instance.list_tools()
    declarations = []

    for tool in mcp_tools:
        schema = tool.parameters  # dict: JSON Schema object
        props_raw = schema.get("properties", {})
        required = schema.get("required", [])

        gemini_props = {}
        for prop_name, prop_def in props_raw.items():
            prop_type = prop_def.get("type", "string")
            gemini_prop = types.Schema(
                type=_json_type_to_gemini(prop_type),
                description=prop_def.get("description", ""),
            )
            # Handle array items
            if prop_type == "array" and "items" in prop_def:
                item_type = prop_def["items"].get("type", "string")
                gemini_prop = types.Schema(
                    type="ARRAY",
                    description=prop_def.get("description", ""),
                    items=types.Schema(type=_json_type_to_gemini(item_type)),
                )
            gemini_props[prop_name] = gemini_prop

        declarations.append(
            types.FunctionDeclaration(
                name=tool.name,
                description=tool.description or tool.name,
                parameters=types.Schema(
                    type="OBJECT",
                    properties=gemini_props,
                    required=required if required else None,
                ),
            )
        )

    return declarations


async def _call_tool(tool_name: str, tool_args: dict) -> str:
    """Call an MCP tool by name and return its result as a string."""
    try:
        result = await mcp_instance.call_tool(tool_name, tool_args)
        # FastMCP returns a list that may contain:
        #   - tuple pairs like ('content', [TextContent(...)])
        #   - dicts with metadata (fastmcp internal) — skip these
        #   - raw TextContent objects
        parts = []
        for item in result:
            if isinstance(item, dict):
                # Skip FastMCP internal metadata dicts
                continue
            elif isinstance(item, tuple) and len(item) == 2:
                key, value = item
                if key == "content" and isinstance(value, list):
                    for v in value:
                        if hasattr(v, "text") and v.text:
                            parts.append(v.text)
            elif hasattr(item, "text") and item.text:
                parts.append(item.text)
            elif isinstance(item, str):
                parts.append(item)

        return "\n".join(parts) if parts else "Tool returned no output."
    except Exception as e:
        return f"Tool error ({tool_name}): {str(e)}"


async def _agentic_generate(topic: str, blog_url: str) -> str:
    """
    Core async agentic loop:
      1. Gemini calls search_web / get_recent_posts as needed.
      2. We execute the tools and feed results back.
      3. Loop until Gemini produces final text (no more tool calls).
    """
    system_prompt = load_system_prompt().replace("{BLOG_URL}", blog_url)

    user_message = (
        f"The topic is: {topic}\n\n"
        f"Blog URL: {blog_url}\n\n"
        "Execute the complete autonomous SEO blogging pipeline.\n\n"
        "TOOL USAGE INSTRUCTIONS:\n"
        "1. Call `search_web` 2–3 times with targeted queries to gather the latest "
        "facts, stats, and news about the topic.\n"
        "2. Call `get_recent_posts` once to fetch existing blog posts for internal "
        "linking suggestions.\n"
        "3. Write the full article following ALL output format rules in your system prompt.\n"
        "4. Do NOT call `publish_blog` — the app handles publishing separately.\n\n"
        "Output the complete structured result in the exact specified format."
    )

    gemini_tools = await _build_gemini_tools()
    messages = [{"role": "user", "parts": [{"text": user_message}]}]
    full_output_parts = []

    # Agentic loop (max 10 rounds to prevent runaway loops)
    for _round in range(10):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools=[types.Tool(function_declarations=gemini_tools)],
            ),
        )

        candidate = response.candidates[0]
        response_parts = candidate.content.parts

        text_this_round = ""
        tool_calls_this_round = []

        for part in response_parts:
            if hasattr(part, "text") and part.text:
                text_this_round += part.text
            if hasattr(part, "function_call") and part.function_call:
                tool_calls_this_round.append(part.function_call)

        if text_this_round:
            full_output_parts.append(text_this_round)

        # No tool calls → agent is finished
        if not tool_calls_this_round:
            break

        # Execute each tool call
        tool_response_parts = []
        for fc in tool_calls_this_round:
            tool_name = fc.name
            tool_args = dict(fc.args) if fc.args else {}
            tool_result = await _call_tool(tool_name, tool_args)

            tool_response_parts.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=tool_name,
                        response={"result": tool_result},
                    )
                )
            )

        # Extend conversation with model response + tool results
        messages.append({"role": "model", "parts": response_parts})
        messages.append({"role": "user", "parts": tool_response_parts})

    return "\n".join(full_output_parts)


# ─────────────────────────────────────────────────────────────
# Public API (called by app.py)
# ─────────────────────────────────────────────────────────────

def generate_blog_post(topic: str, blog_url: str) -> str:
    """
    Synchronous wrapper around the async agentic loop.
    Called by app.py — no async changes needed there.
    """
    if not client:
        raise ValueError(
            "GEMINI_API_KEY is not set in .env. Please add it."
        )
    if not blog_url:
        raise ValueError("BLOG_URL is not set. Please provide your Blogger URL.")

    return asyncio.run(_agentic_generate(topic, blog_url))


def parse_llm_output(full_text: str) -> dict:
    """
    Parse LLM output into sections keyed by # HEADINGS.
    """
    sections = {}
    current_section = "GENERAL"
    current_content = []

    for line in full_text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("# ") and stripped[2:].isupper():
            sections[current_section] = "\n".join(current_content).strip()
            current_section = stripped[2:].strip()
            current_content = []
        else:
            current_content.append(line)

    sections[current_section] = "\n".join(current_content).strip()
    return sections
