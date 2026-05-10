"""
MCP Server for Autonomous SEO Blogging Agent
Exposes three tools to the Gemini LLM:
  1. search_web       - Fetch latest info from the web (DuckDuckGo)
  2. get_recent_posts - List recent Blogger posts for internal linking
  3. publish_blog     - Publish the final blog post to Blogger
"""

import os
import json
import requests
from dotenv import load_dotenv
from fastmcp import FastMCP

# blogger_api is our existing module
from blogger_api import get_blogger_service, get_blog_id, publish_post

load_dotenv()

mcp = FastMCP("seo-blogging-agent")


# ─────────────────────────────────────────
# TOOL 1: Web Search (DuckDuckGo Instant Answer API)
# ─────────────────────────────────────────
@mcp.tool()
def search_web(query: str) -> str:
    """
    Search the web for latest information on a given query.
    Returns a summary of top results including titles, snippets, and URLs.
    Use this to find latest news, statistics, and facts for blog articles.

    Args:
        query: The search query string.

    Returns:
        A formatted string with search results.
    """
    try:
        # DuckDuckGo Instant Answer API (free, no key required)
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1,
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = []

        # Abstract (featured snippet-style answer)
        if data.get("AbstractText"):
            results.append(f"📌 Summary: {data['AbstractText']}")
            if data.get("AbstractURL"):
                results.append(f"   Source: {data['AbstractURL']}")

        # Related topics
        related = data.get("RelatedTopics", [])
        count = 0
        for topic in related:
            if count >= 5:
                break
            if isinstance(topic, dict) and topic.get("Text"):
                results.append(f"• {topic['Text']}")
                if topic.get("FirstURL"):
                    results.append(f"  🔗 {topic['FirstURL']}")
                count += 1

        if not results:
            # Fallback: return a note so AI can still proceed
            return (
                f"No instant results found for: '{query}'. "
                "Please use your training knowledge to write the article."
            )

        return "\n".join(results)

    except Exception as e:
        return f"Web search failed: {str(e)}. Proceed with training knowledge."


# ─────────────────────────────────────────
# TOOL 2: Get Recent Blogger Posts (for Internal Linking)
# ─────────────────────────────────────────
@mcp.tool()
def get_recent_posts(blog_url: str, max_results: int = 10) -> str:
    """
    Fetches the most recent posts from the Blogger blog.
    Use this to find relevant posts to link internally in the new article.

    Args:
        blog_url: The full URL of the Blogger blog (e.g., https://example.blogspot.com/).
        max_results: Number of recent posts to fetch (default: 10, max: 20).

    Returns:
        A JSON-formatted list of posts with title and URL.
    """
    try:
        service = get_blogger_service()
        blog_id = get_blog_id(service, url=blog_url)

        max_results = min(int(max_results), 20)

        response = (
            service.posts()
            .list(
                blogId=blog_id,
                maxResults=max_results,
                fields="items(title,url)",
                status="live",
            )
            .execute()
        )

        posts = response.get("items", [])
        if not posts:
            return "No existing posts found on this blog yet."

        formatted = []
        for post in posts:
            formatted.append(
                {"title": post.get("title", "Untitled"), "url": post.get("url", "")}
            )

        return json.dumps(formatted, ensure_ascii=False, indent=2)

    except Exception as e:
        return f"Could not fetch recent posts: {str(e)}"


# ─────────────────────────────────────────
# TOOL 3: Publish Blog Post
# ─────────────────────────────────────────
@mcp.tool()
def publish_blog(
    title: str,
    content_html: str,
    labels: list,
    blog_url: str,
    is_draft: bool = False,
) -> str:
    """
    Publishes the final SEO-optimized blog post to Blogger.
    Call this ONLY after the complete article HTML is ready.

    Args:
        title:        The SEO-optimized post title.
        content_html: The complete Blogger-compatible HTML content.
        labels:       List of tags/labels for the post (e.g. ["SEO", "AI"]).
        blog_url:     The full URL of the Blogger blog.
        is_draft:     If True, saves as draft instead of publishing live.

    Returns:
        A success message with the published post URL, or an error message.
    """
    try:
        response = publish_post(
            title=title,
            content_html=content_html,
            labels=labels,
            blog_url=blog_url,
            is_draft=is_draft,
        )
        post_url = response.get("url", "Draft saved — no public URL yet.")
        status = "Draft saved" if is_draft else "Published"
        return f"✅ {status} successfully! Post URL: {post_url}"
    except Exception as e:
        return f"❌ Failed to publish: {str(e)}"


# ─────────────────────────────────────────
# Entry point (for running as standalone server if needed)
# ─────────────────────────────────────────
if __name__ == "__main__":
    mcp.run()
