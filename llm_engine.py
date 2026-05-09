import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None

def load_system_prompt():
    prompt_path = "AGENTS.md"
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    return "You are an SEO Blogging Agent."

def generate_blog_post(topic: str, blog_url: str) -> str:
    """
    Generates the entire SEO blog post output using Google Gemini.
    """
    if not client:
        raise ValueError("GEMINI_API_KEY is not set in the .env file. Please add it.")

    if not blog_url:
        raise ValueError("BLOG_URL is not set. Please provide your Blogger URL.")

    system_prompt = load_system_prompt()
    system_prompt = system_prompt.replace("{BLOG_URL}", blog_url)
    
    prompt = f"The topic is: {topic}\n\nExecute the complete autonomous SEO blogging pipeline."
    
    try:
        # We use gemini-2.5-flash because it supports the free tier quota
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
            ),
        )
        return response.text
    except Exception as e:
        raise Exception(f"Failed to generate content via LLM: {str(e)}")

def parse_llm_output(full_text: str) -> dict:
    """
    Parses the massive LLM output into dictionary sections based on the headings.
    """
    sections = {}
    current_section = "GENERAL"
    current_content = []
    
    for line in full_text.split('\n'):
        if line.startswith('# ') and line.isupper():
            # Save previous section
            sections[current_section] = '\n'.join(current_content).strip()
            # Start new section
            current_section = line.replace('# ', '').strip()
            current_content = []
        else:
            current_content.append(line)
            
    # Save the last section
    sections[current_section] = '\n'.join(current_content).strip()
    
    return sections
