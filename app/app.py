import streamlit as st
import sys
import os

# Base directory & src folder ko path mein add karo
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(BASE_DIR, "src")

for p in [SRC_DIR, BASE_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from rag_pipeline import rag_query
except ImportError:
    from src.rag_pipeline import rag_query

# Page config
st.set_page_config(
    page_title="Semester Study Assistant",
    page_icon="📚",
    layout="wide"
)

# Custom CSS - clean dark look
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #9ca3af;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .answer-box {
        background: #1e1e2e;
        border: 1px solid #313244;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-top: 1rem;
    }
    .source-chip {
        display: inline-block;
        background: #313244;
        color: #cdd6f4;
        padding: 0.3rem 0.7rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.2rem 0.3rem 0.2rem 0;
    }
    div[data-testid="stSidebar"] {
        background: #11111b;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📚 Study Assistant")
    st.markdown("AI & Data Science — Current Semester")
    st.markdown("---")
    st.markdown("**Subjects covered**")
    st.markdown("- Computer Networks")
    st.markdown("- DBMS")
    st.markdown("- Discrete Mathematics")
    st.markdown("- DSA")
    st.markdown("- Data Science & Visualization")
    st.markdown("---")
    st.caption("First searches your notes, syllabus & PYQs.")
    st.caption("If not found, answers from general knowledge.")

    env_groq_key = os.getenv("GROQ_API_KEY", "").strip()
    if not env_groq_key or env_groq_key == "your_groq_api_key_here":
        st.markdown("---")
        st.warning("⚠️ GROQ_API_KEY not found in `.env`")
        sidebar_api_key = st.text_input(
            "Enter Groq API Key",
            type="password",
            placeholder="gsk_...",
            help="Get a free key from https://console.groq.com"
        )
    else:
        sidebar_api_key = None

# Main area
st.markdown('<p class="main-title">Semester Study Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Ask anything from your syllabus, notes, or previous year questions</p>', unsafe_allow_html=True)

# Question input
query = st.text_area(
    "Your question",
    placeholder="e.g. What is CSMA/CD?  |  Explain ER diagram  |  Unit 2 important topics",
    height=100
)

col1, col2 = st.columns([1, 5])
with col1:
    ask = st.button("Ask", type="primary", use_container_width=True)

# Answer section
if ask and query.strip():
    with st.spinner("Searching notes & generating answer..."):
        try:
            active_key = sidebar_api_key or env_groq_key
            answer, sources, source_type = rag_query(query.strip(), api_key=active_key)

            # Tag: notes vs general
            if source_type == "notes":
                st.success("From your notes")
            else:
                st.info("General knowledge (not found in your notes)")

            st.markdown("#### Answer")
            st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)

            # Sources sirf notes wale answer pe
            if source_type == "notes" and sources:
                unique_sources = []
                seen = set()
                for s in sources:
                    key = (s["subject"], s["filename"])
                    if key not in seen:
                        seen.add(key)
                        unique_sources.append(s)

                st.markdown("#### Sources")
                chips = ""
                for s in unique_sources:
                    chips += f'<span class="source-chip">{s["subject"]} · {s["filename"]}</span>'
                st.markdown(chips, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Something went wrong: {e}")

elif ask and not query.strip():
    st.warning("Please type a question first.")