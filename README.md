# Autonomous AI SEO Blogging Agent

A fully autonomous Python-based SEO blogging agent that researches topics, writes comprehensive SEO-optimized articles using Google's latest Gemini 2.5 Flash model, and publishes them directly to Blogger via the Google Blogger API.

## Features
- **Streamlit Web UI:** Easy to use dashboard to enter blog topics and monitor progress.
- **Autonomous SEO Research:** Analyzes search intent, ranking keywords, and FAQs.
- **High-Quality Long-Form Content:** Generates 2500+ word articles formatted in clean HTML.
- **Automatic Feature Image Generation:** Automatically creates an AI-generated thumbnail image via `pollinations.ai` and injects it into the post.
- **Zero-Touch Publishing:** Authenticates with Google Blogger API and publishes directly (or saves as draft).
- **Environment Management:** Automatically creates and manages Python virtual environments and dependencies.

## Prerequisites
1. Python 3.10+
2. A **Google Gemini API Key** (from Google AI Studio).
3. A **Blogger API `credentials.json`** file configured as a "Desktop App" (or a "Web App" with `http://localhost:8080/` authorized redirect URI).

## Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kumarsharmaatul/googleblogger.git
   cd googleblogger
   ```

2. **Setup your environment variables:**
   Create a `.env` file in the root directory (you can copy `.env.example` if available) and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Add Google Credentials:**
   Place your `credentials.json` file in the root directory.

4. **Run the Application:**
   ```bash
   python3 run.py
   ```
   The `run.py` script will automatically:
   - Create a virtual environment (`.venv`) if one doesn't exist.
   - Install all required packages from `requirements.txt`.
   - Launch the Streamlit Web UI.

5. **Publish!**
   Open the Local URL provided in your terminal (usually `http://localhost:8501`), enter your topic, and click **Generate & Publish**. The first time you publish, a browser window will open asking you to grant Blogger permissions.

## Technologies Used
- **Google GenAI SDK (`google.genai`)**: For generating the articles with `gemini-2.5-flash`.
- **Google API Python Client**: For interacting with the Blogger API v3.
- **Streamlit**: For the web application interface.