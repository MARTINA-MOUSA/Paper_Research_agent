import streamlit as st
import requests
import os
from pathlib import Path
import time
import json

# Page configuration
st.set_page_config(
    page_title="Paper2Video",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def upload_paper(file):
    """Upload paper to API"""
    try:
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        with st.spinner("Processing paper... This may take a few minutes."):
            response = requests.post(
                f"{API_BASE_URL}/papers/upload",
                files=files,
                timeout=300
            )
        return response
    except requests.exceptions.Timeout:
        st.error("Request timed out. The paper might be too large or processing is taking longer than expected.")
        return None
    except Exception as e:
        st.error(f"Error uploading paper: {str(e)}")
        return None

def classify_text(text):
    """Classify text using API"""
    try:
        # FastAPI Body expects the text as a JSON-encoded string
        response = requests.post(
            f"{API_BASE_URL}/classify/field",
            data=json.dumps(text),  # Send as JSON-encoded string
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        return response
    except Exception as e:
        st.error(f"Error classifying text: {str(e)}")
        return None

def fetch_trending(category="cs.LG", limit=10):
    """Fetch trending papers from API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/trends/trending",
            params={"category": category, "limit": limit},
            timeout=30
        )
        return response
    except Exception as e:
        st.error(f"Error fetching trends: {str(e)}")
        return None

def main():
    # Header
    st.markdown('<h1 class="main-header">📄 Paper2Video</h1>', unsafe_allow_html=True)
    st.markdown("### Transform Research Papers into Educational Videos")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        global API_BASE_URL
        API_BASE_URL = st.text_input("API Base URL", value=API_BASE_URL)
        
        # Health check
        if st.button("Check API Status"):
            if check_api_health():
                st.success("✅ API is running")
            else:
                st.error("❌ API is not accessible")
        
        st.markdown("---")
        st.markdown("### 📚 Navigation")
        page = st.radio(
            "Choose a page",
            ["Upload Paper", "Classify Text", "Trending Papers"]
        )
    
    # Main content based on selected page
    if page == "Upload Paper":
        upload_paper_page()
    elif page == "Classify Text":
        classify_text_page()
    elif page == "Trending Papers":
        trending_papers_page()

def upload_paper_page():
    st.header("📤 Upload Research Paper")
    st.markdown("Upload a PDF research paper to generate a video explanation")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload a research paper in PDF format"
    )
    
    if uploaded_file is not None:
        st.info(f"📄 File: {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")
        
        if st.button("🚀 Process Paper", type="primary"):
            response = upload_paper(uploaded_file)
            
            if response and response.status_code == 200:
                data = response.json()
                
                st.success("✅ Paper processed successfully!")
                
                # Display results in tabs
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "📝 Summary", "🏷️ Classification", "📑 Sections", "🎬 Video", "🔑 Keywords"
                ])
                
                with tab1:
                    st.subheader("Summary")
                    st.markdown(f'<div class="info-box">{data.get("summary", "N/A")}</div>', unsafe_allow_html=True)
                
                with tab2:
                    st.subheader("AI Field Classification")
                    field = data.get("field", "Unknown")
                    st.markdown(f'<div class="success-box"><h3>{field}</h3></div>', unsafe_allow_html=True)
                    
                    keywords = data.get("keywords", [])
                    if keywords:
                        st.subheader("Keywords")
                        keyword_tags = " ".join([f"`{kw}`" for kw in keywords])
                        st.markdown(keyword_tags)
                
                with tab3:
                    st.subheader("Paper Sections")
                    sections = data.get("sections", [])
                    for i, section in enumerate(sections, 1):
                        with st.expander(f"Section {i}: {section.get('title', 'Untitled')}"):
                            st.write(section.get("summary", ""))
                
                with tab4:
                    st.subheader("Generated Video")
                    video_filename = data.get("video_filename")
                    video_url = data.get("video_url")
                    
                    if video_filename and video_url:
                        st.info(f"Video: {video_filename}")
                        
                        # Try to display video
                        try:
                            video_response = requests.get(f"{API_BASE_URL}{video_url}", stream=True)
                            if video_response.status_code == 200:
                                video_path = f"temp_{video_filename}"
                                with open(video_path, "wb") as f:
                                    for chunk in video_response.iter_content(chunk_size=8192):
                                        f.write(chunk)
                                
                                st.video(video_path)
                                
                                # Download button
                                with open(video_path, "rb") as f:
                                    st.download_button(
                                        label="📥 Download Video",
                                        data=f.read(),
                                        file_name=video_filename,
                                        mime="video/mp4"
                                    )
                                
                                # Cleanup
                                if os.path.exists(video_path):
                                    os.remove(video_path)
                            else:
                                st.warning("Video file not found. Please check the API logs.")
                        except Exception as e:
                            st.error(f"Error loading video: {str(e)}")
                    else:
                        st.warning("Video not generated")
                
                with tab5:
                    st.subheader("Video Script")
                    script = data.get("script", [])
                    for i, scene in enumerate(script, 1):
                        with st.expander(f"Scene {i}"):
                            st.write("**On Screen:**", scene.get("overlay", ""))
                            st.write("**Narration:**", scene.get("narration", ""))
                
            elif response:
                error_data = response.json()
                st.error(f"❌ Error: {error_data.get('detail', 'Unknown error')}")
            else:
                st.error("❌ Failed to process paper. Please check API connection.")

def classify_text_page():
    st.header("🔍 Classify Text into AI Field")
    st.markdown("Enter text to classify it into an AI research field")
    
    text_input = st.text_area(
        "Enter text to classify",
        height=200,
        placeholder="Paste research paper abstract or relevant text here..."
    )
    
    if st.button("🔍 Classify", type="primary"):
        if not text_input or len(text_input.strip()) < 10:
            st.warning("Please enter at least 10 characters")
        else:
            with st.spinner("Classifying..."):
                response = classify_text(text_input)
                
                if response and response.status_code == 200:
                    data = response.json()
                    field = data.get("predicted_field", "Unknown")
                    
                    st.success("✅ Classification complete!")
                    st.markdown(f'<div class="success-box"><h2>Predicted Field: {field}</h2></div>', unsafe_allow_html=True)
                elif response:
                    error_data = response.json()
                    st.error(f"❌ Error: {error_data.get('detail', 'Unknown error')}")
                else:
                    st.error("❌ Failed to classify text. Please check API connection.")

def trending_papers_page():
    st.header("📈 Trending Papers")
    st.markdown("Browse trending research papers from arXiv")
    
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.selectbox(
            "Select Category",
            ["cs.LG", "cs.CV", "cs.CL", "cs.AI", "cs.NE", "stat.ML"],
            help="arXiv category"
        )
    
    with col2:
        limit = st.slider("Number of Papers", 5, 50, 10)
    
    if st.button("🔍 Fetch Trending Papers", type="primary"):
        with st.spinner("Fetching trending papers..."):
            response = fetch_trending(category=category, limit=limit)
            
            if response and response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                count = data.get("count", len(items))
                
                st.success(f"✅ Found {count} trending papers")
                
                if items:
                    for i, paper in enumerate(items, 1):
                        with st.expander(f"📄 {i}. {paper.get('title', 'Untitled')}"):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.write("**Abstract:**")
                                st.write(paper.get("summary", "No summary available"))
                                
                                if paper.get("link"):
                                    st.markdown(f"[🔗 View on arXiv]({paper.get('link')})")
                            
                            with col2:
                                field = paper.get("field", "Unknown")
                                st.markdown(f"**Field:** {field}")
                                
                                if paper.get("published"):
                                    st.write(f"**Published:** {paper.get('published')}")
                                
                                if paper.get("arxiv_id"):
                                    st.code(paper.get("arxiv_id"))
                else:
                    st.info("No papers found for this category")
                    
            elif response:
                error_data = response.json()
                st.error(f"❌ Error: {error_data.get('detail', 'Unknown error')}")
            else:
                st.error("❌ Failed to fetch trends. Please check API connection.")

if __name__ == "__main__":
    main()

