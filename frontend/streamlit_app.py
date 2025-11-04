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


def upload_paper(file):
    try:
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        with st.spinner("Processing paper... This may take a few minutes."):
            response = requests.post(f"{API_BASE_URL}/papers/upload", files=files, timeout=300)
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
        response = requests.get(f"{API_BASE_URL}/trends/trending", params={"category": category, "limit": limit}, timeout=30)
        return response
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend API. Please make sure the backend server is running on port 8000.")
    except Exception as e:
        st.error(f"Error fetching trends: {str(e)}")


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
    if uploaded_file and st.button("🚀 Process Paper", type="primary"):
        response = upload_paper(uploaded_file)
        if response and response.status_code == 200:
            data = response.json()
            st.success("✅ Paper processed successfully!")
            st.json(data)
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
                st.success(f"✅ Found {data.get('count', len(data.get('items', [])))} papers")
                st.json(data)
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
