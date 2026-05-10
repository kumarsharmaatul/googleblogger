# Autonomous AI SEO Blogging Agent (v1.0 - MCP Powered) 🤖

A fully autonomous Python-based SEO blogging agent that researches topics, writes comprehensive SEO-optimized articles using Google's latest Gemini 2.5 Flash model, and publishes them directly to Blogger.

**Now powered by Model Context Protocol (MCP) for true agentic autonomy.**

## Key Features
- **MCP-Powered Agentic Workflow:** Uses an autonomous tool-calling loop to research, link, and publish.
- **Deep Web Research:** Automatically calls the `search_web` tool (via DuckDuckGo) to gather real-time facts and latest news.
- **Internal Linking Engine:** Automatically calls `get_recent_posts` to find and suggest internal links from your own blog.
- **High-Quality Long-Form Content:** Generates 2500+ word human-like articles formatted in clean HTML.
- **Streamlit Web UI:** Premium dashboard to monitor the agent's research and writing steps in real-time.
- **Automatic Feature Image Generation:** Creates AI-generated thumbnails via `pollinations.ai`.
- **Zero-Touch Publishing:** Authenticates with Google Blogger API and publishes directly.

## Prerequisites
1. Python 3.10+
2. A **Google Gemini API Key** (from [Google AI Studio](https://aistudio.google.com/)).
3. A **Blogger API `credentials.json`** file (from [Google Cloud Console](https://console.cloud.google.com/)).

## Installation & Usage

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/kumarsharmaatul/googleblogger.git
   cd googleblogger
   ```

2. **Configure Environment:**
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   BLOG_URL=https://your-blog.blogspot.com/
   ```

3. **Add Google Credentials:**
   Place your `credentials.json` file in the root directory.

4. **Launch the Agent:**
   ```bash
   python3 run.py
   ```
   The `run.py` script will automatically handle virtual environment setup and dependency installation.

5. **Start Blogging:**
   Open the Local URL provided (usually `http://localhost:8501`), enter a topic, and click **Generate & Publish**. 
   *Note: The first time you run it, a browser tab will open for Google OAuth authorization.*

## System Architecture
The agent uses a modular MCP-based architecture:
- **`mcp_server.py`**: Exposes tools for web search, blog fetching, and publishing.
- **`llm_engine.py`**: Orchestrates the Gemini agentic loop, deciding when to call tools.
- **`app.py`**: Provides the Streamlit interface for user interaction.

## Technologies Used
- **Google GenAI SDK**: Powering the `gemini-2.5-flash` model.
- **FastMCP**: Standardized Model Context Protocol for tool execution.
- **Google Blogger API v3**: For seamless publishing.
- **Streamlit**: For the interactive dashboard.