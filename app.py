import streamlit as st
import json
import os
from llm_engine import generate_blog_post, parse_llm_output
from blogger_api import publish_post

st.set_page_config(page_title="Autonomous SEO Blogger", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
        .stDeployButton {display:none !important;}
        #MainMenu {visibility: hidden !important;}
        header {visibility: hidden !important;}
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Autonomous SEO Blogging Agent")
st.markdown("Enter a topic below, and I will research, write, and publish an SEO-optimized blog post directly to your Blogger site.")

col_url, col_topic = st.columns([1, 2])
with col_url:
    blog_url = st.text_input("Blogger URL:", value=os.getenv("BLOG_URL", ""), placeholder="https://your-blog.blogspot.com/")
with col_topic:
    topic = st.text_input("Enter your Blog Topic:", placeholder="e.g., The Future of Agentic AI in 2026")

col1, col2 = st.columns([1, 4])
with col1:
    is_draft = st.checkbox("Save as Draft (Do not publish live)", value=True)

if st.button("Generate & Publish", type="primary"):
    if not blog_url.strip():
        st.error("Please enter your Blogger URL.")
    elif not topic.strip():
        st.error("Please enter a valid topic.")
    else:
        with st.status("Initializing Autonomous Agent...") as status:
            try:
                # Step 1: Generate Content
                status.update(label="Step 1: Researching and Generating SEO Content (This takes 1-2 minutes)...", state="running")
                raw_output = generate_blog_post(topic, blog_url=blog_url.strip())
                st.session_state['raw_output'] = raw_output
                
                # Step 2: Parse Output
                status.update(label="Step 2: Parsing LLM Output...", state="running")
                sections = parse_llm_output(raw_output)
                
                blogger_json_str = sections.get("BLOGGER API JSON", "{}")
                # Clean markdown JSON block formatting if present
                if blogger_json_str.startswith("```json"):
                    blogger_json_str = blogger_json_str[7:]
                if blogger_json_str.endswith("```"):
                    blogger_json_str = blogger_json_str[:-3]
                    
                blogger_data = json.loads(blogger_json_str.strip())
                
                # Default to fallback values if JSON parsing misses something
                title = blogger_data.get("title", sections.get("SEO TITLE", "Untitled Post"))
                content_html = sections.get("BLOGGER HTML", sections.get("BLOG ARTICLE (MARKDOWN)", "<p>No content generated.</p>"))
                # Clean markdown HTML block formatting if present
                if content_html.startswith("```html"):
                    content_html = content_html[7:]
                if content_html.endswith("```"):
                    content_html = content_html[:-3]
                    
                labels = blogger_data.get("labels", ["SEO", "AI"])
                
                # Step 3: Publish to Blogger
                status.update(label="Step 3: Publishing to Blogger API...", state="running")
                response = publish_post(title=title, content_html=content_html.strip(), labels=labels, blog_url=blog_url.strip(), is_draft=is_draft)
                
                status.update(label="Complete!", state="complete")
                
                post_url = response.get('url', 'Draft saved (No public URL yet)')
                st.success(f"Successfully published! [View Post]({post_url})" if not is_draft else "Successfully saved as Draft!")
                
            except Exception as e:
                import traceback
                with open("error_log.txt", "w") as f:
                    f.write(traceback.format_exc())
                status.update(label="Error Occurred", state="error")
                st.error(f"An error occurred: {str(e)}\n\n(Detailed error saved to error_log.txt)")

# Display raw output if it exists in session state
if 'raw_output' in st.session_state:
    with st.expander("View Full Agent Output (Metadata, Social Posts, Images)"):
        st.markdown(st.session_state['raw_output'])
