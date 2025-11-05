import streamlit as st
import requests
import os
from pathlib import Path
import time
import json

# =============================
# PAGE CONFIGURATION
# =============================
st.set_page_config(
    page_title="Paper2Video",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================
# CUSTOM CSS
# =============================
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
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# =============================
# CONFIGURATION
# =============================
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
REQUEST_TIMEOUT_DEFAULT = int(os.getenv("REQUEST_TIMEOUT", "600"))


# =============================
# FUNCTIONS
# =============================

def check_api_health():
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        elif response.status_code == 403:
            return False, {"error": "403 Forbidden - CORS issue", "status_code": 403}
        else:
            return False, {"error": f"Status {response.status_code}", "status_code": response.status_code}
    except requests.exceptions.ConnectionError:
        return False, {"error": "Connection refused - Backend not running"}
    except requests.exceptions.Timeout:
        return False, {"error": "Request timeout"}
    except Exception as e:
        return False, {"error": str(e)}


def upload_paper(file, timeout_seconds: int):
    try:
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        with st.spinner("Processing paper... This may take a few minutes."):
            response = requests.post(f"{API_BASE_URL}/papers/upload", files=files, timeout=timeout_seconds)
        return response
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend API. Please make sure the backend server is running on port 8000.")
    except requests.exceptions.Timeout:
        st.error("Request timed out. The paper might be too large or processing is taking longer than expected.")
    except Exception as e:
        st.error(f"Error uploading paper: {str(e)}")


def classify_text(text):
    try:
        response = requests.post(
            f"{API_BASE_URL}/classify/field",
            data=json.dumps(text),
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        return response
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend API. Please make sure the backend server is running on port 8000.")
    except Exception as e:
        st.error(f"Error classifying text: {str(e)}")


def fetch_trending(category="cs.LG", limit=10):
    try:
        response = requests.get(f"{API_BASE_URL}/trends/trending", params={"category": category, "limit": limit}, timeout=180)
        return response
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend API. Please make sure the backend server is running on port 8000.")
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. The backend is processing a large number of papers. Please try again or reduce the limit.")
    except Exception as e:
        st.error(f"Error fetching trends: {str(e)}")


def translate_text_api(text: str, target_language: str):
    try:
        payload = {"text": text, "target_language": target_language}
        r = requests.post(f"{API_BASE_URL}/papers/translate", params=payload, timeout=60)
        if r.status_code == 200:
            return r.json().get("translated", "")
        else:
            st.error("Translation failed")
            return ""
    except Exception as e:
        st.error(f"Translation error: {e}")
        return ""


# =============================
# PAGE FUNCTIONS
# =============================

def upload_paper_page(api_healthy):
    st.header("📤 Upload Research Paper")
    st.markdown("Upload a PDF research paper to generate a video explanation")

    if not api_healthy:
        st.info("Please ensure the backend API is running before uploading papers.")
        return

    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    timeout_seconds = st.number_input("Request timeout (seconds)", min_value=60, max_value=3600, value=REQUEST_TIMEOUT_DEFAULT, step=30, help="Increase if your paper is long.")

    if uploaded_file and st.button("🚀 Process Paper", type="primary"):
        response = upload_paper(uploaded_file, timeout_seconds=timeout_seconds)
        if response and response.status_code == 200:
            resp = response.json()
            job_id = resp.get("job_id")
            if not job_id:
                st.error("❌ Failed to start job.")
                return
            st.info(f"Job started: {job_id}")
            progress = st.progress(0)
            status_text = st.empty()
            result_placeholder = st.empty()

            import time
            while True:
                try:
                    r = requests.get(f"{API_BASE_URL}/papers/status/{job_id}", timeout=120)
                    if r.status_code != 200:
                        status_text.error("Failed to fetch job status")
                        break
                    job = r.json()
                    p = int(job.get("progress", 0))
                    progress.progress(max(0, min(100, p)))
                    status = job.get("status", "")
                    if status == "done":
                        status_text.success("✅ Completed")
                        result = job.get("result", {})

                        # Show Arabic summary directly
                        summary = result.get("summary", "")
                        st.subheader("📄 الملخص بالعربية")
                        st.write(summary)

                        # Translation controls
                        with st.expander("🌐 ترجمة الملخص"):
                            target_lang = st.text_input("اللغة المستهدفة", value="English")
                            if st.button("ترجمة"):
                                translated = translate_text_api(summary, target_lang)
                                if translated:
                                    st.text_area("الترجمة", translated, height=300)

                        # Sections and script (optional raw view)
                        with st.expander("🧩 Sections & Script (Raw)"):
                            st.json({"sections": result.get("sections", []), "script": result.get("script", [])})

                        # Inline video rendering
                        video_url = result.get("video_url")
                        if video_url:
                            full_url = f"{API_BASE_URL}{video_url}"
                            try:
                                vr = requests.get(full_url, timeout=120)
                                if vr.status_code == 200:
                                    st.subheader("🎬 الفيديو")
                                    st.video(vr.content)
                                else:
                                    st.warning("Could not fetch video bytes, showing link instead")
                                    st.write(full_url)
                            except Exception:
                                st.warning("Could not fetch video bytes, showing link instead")
                                st.write(full_url)

                        # Keywords & Field
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**🔎 Field**")
                            st.write(result.get("field", "Unknown"))
                        with col2:
                            st.markdown("**🏷️ Keywords**")
                            st.write(", ".join(result.get("keywords", [])))

                        break
                    elif status == "error":
                        status_text.error("❌ Error: " + str(job.get("error", "Unknown")))
                        break
                    else:
                        status_text.info(f"Status: {status} ({p}%)")
                    time.sleep(2)
                except requests.exceptions.Timeout:
                    # Non-fatal: keep polling
                    status_text.info("Status: polling timed out, retrying...")
                    time.sleep(2)
                    continue
                except Exception as e:
                    status_text.error(f"Polling error: {e}")
                    time.sleep(2)
                    continue
        else:
            st.error("❌ Failed to process paper.")


def classify_text_page(api_healthy):
    st.header("🔍 Classify Text into AI Field")
    st.markdown("Enter text to classify it into an AI research field")

    if not api_healthy:
        st.info("Please ensure the backend API is running before classifying text.")
        return

    text_input = st.text_area("Enter text to classify", height=200)
    if st.button("🔍 Classify", type="primary"):
        if len(text_input.strip()) < 10:
            st.warning("Please enter at least 10 characters")
        else:
            with st.spinner("Classifying..."):
                response = classify_text(text_input)
                if response and response.status_code == 200:
                    data = response.json()
                    st.success(f"✅ Predicted Field: {data.get('predicted_field', 'Unknown')}")
                else:
                    st.error("❌ Failed to classify text.")


def trending_papers_page(api_healthy):
    st.header("📈 Trending Papers")
    st.markdown("Browse trending research papers from arXiv")

    if not api_healthy:
        st.info("Please ensure the backend API is running before fetching trending papers.")
        return

    category = st.selectbox("Select Category", ["cs.LG", "cs.CV", "cs.CL", "cs.AI", "cs.NE", "stat.ML"])
    limit = st.slider("Number of Papers", 5, 50, 10)

    if st.button("🔍 Fetch Trending Papers", type="primary"):
        with st.spinner("Fetching trending papers..."):
            response = fetch_trending(category=category, limit=limit)
            if response and response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                count = data.get('count', len(items))
                st.success(f"✅ Found {count} papers")
                
                # Display each paper in a formatted way
                for idx, paper in enumerate(items, 1):
                    with st.container():
                        # Title
                        st.markdown(f"### {idx}. {paper.get('title', 'Untitled')}")
                        
                        # Summary
                        summary = paper.get('summary', 'No summary available')
                        st.markdown(f"**Summary:** {summary}")
                        
                        # Link and Source
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            link = paper.get('link', '')
                            if link:
                                st.markdown(f"🔗 [Read Paper]({link})")
                        with col2:
                            published = paper.get('published', '')
                            if published:
                                # Parse date if needed
                                st.markdown(f"📅 **Published:** {published}")
                        
                        # Field (if available)
                        field = paper.get('field', '')
                        if field:
                            st.markdown(f"🏷️ **Field:** {field}")
                        
                        st.markdown("---")
            else:
                st.error("❌ Failed to fetch trending papers.")


# =============================
# MAIN APP
# =============================

def main():
    st.markdown('<h1 class="main-header">📄 Paper2Video</h1>', unsafe_allow_html=True)
    st.markdown("### Transform Research Papers into Educational Videos")

    with st.sidebar:
        st.header("⚙️ Configuration")
        global API_BASE_URL
        API_BASE_URL = st.text_input("API Base URL", value=API_BASE_URL)
        st.markdown("---")

        st.subheader("🔌 API Status")
        is_healthy, health_data = check_api_health()

        if is_healthy:
            st.success(" API is running")
        else:
            st.error(" API is not accessible")

        st.markdown("---")
        page = st.radio("📚 Navigation", ["Upload Paper", "Classify Text", "Trending Papers"])

    if page == "Upload Paper":
        upload_paper_page(is_healthy)
    elif page == "Classify Text":
        classify_text_page(is_healthy)
    elif page == "Trending Papers":
        trending_papers_page(is_healthy)


# =============================
# ENTRY POINT
# =============================
if __name__ == "__main__":
    main()
