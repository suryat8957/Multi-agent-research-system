"""
Streamlit Web Application for Multi-Agent Autonomous Research System
Imports and executes the 4-agent research pipeline.
"""

import streamlit as st
import os
import time
from dotenv import load_dotenv
from pipeline import run_research_pipeline

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="DeepResearch AI | Multi-Agent System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling for a modern, sleek interface
st.markdown("""
<style>
    /* Metric & badge styling */
    .agent-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    .badge-search { background-color: rgba(59, 130, 246, 0.15); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.3); }
    .badge-reader { background-color: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-writer { background-color: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-critic { background-color: rgba(168, 85, 247, 0.15); color: #a855f7; border: 1px solid rgba(168, 85, 247, 0.3); }

    /* Card styling */
    .agent-card {
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 12px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = None
if "current_topic" not in st.session_state:
    st.session_state.current_topic = ""

# Sidebar: System Configuration & Architecture Info
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/artificial-intelligence.png", width=64)
    st.title("Research Hub")
    st.caption("Autonomous Collaborative Multi-Agent Pipeline")

    st.markdown("---")
    st.subheader("🤖 Agent Swarm")
    
    st.markdown("""
    <div class="agent-card">
        <span class="agent-badge badge-search">1. Search Agent</span>
        <div style="font-size: 0.82rem; color: #888;">Queries Tavily API to fetch top relevant web sources and URLs.</div>
    </div>
    <div class="agent-card">
        <span class="agent-badge badge-reader">2. Reader Agent</span>
        <div style="font-size: 0.82rem; color: #888;">Navigates top links & scrapes full body text using BeautifulSoup.</div>
    </div>
    <div class="agent-card">
        <span class="agent-badge badge-writer">3. Writer Agent</span>
        <div style="font-size: 0.82rem; color: #888;">Synthesizes raw research into a structured, publication-ready report.</div>
    </div>
    <div class="agent-card">
        <span class="agent-badge badge-critic">4. Critic Agent</span>
        <div style="font-size: 0.82rem; color: #888;">Performs rigorous peer review, scoring report quality from 1-10.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🔑 Environment Status")
    mistral_ok = bool(os.getenv("MISTRAL_API_KEY"))
    tavily_ok = bool(os.getenv("TAVILY_API_KEY"))

    col_k1, col_k2 = st.columns(2)
    with col_k1:
        if mistral_ok:
            st.success("Mistral: Active", icon="🟢")
        else:
            st.error("Mistral: Missing", icon="🔴")
    with col_k2:
        if tavily_ok:
            st.success("Tavily: Active", icon="🟢")
        else:
            st.error("Tavily: Missing", icon="🔴")

    if not (mistral_ok and tavily_ok):
        st.warning("Ensure `.env` contains `MISTRAL_API_KEY` and `TAVILY_API_KEY` to run queries.")

    st.markdown("---")
    st.markdown("💡 *Powered by Mistral AI, Tavily Search & LangChain.*")

# Main Page Header
st.title("🔬 Autonomous Multi-Agent Research System")
st.markdown(
    "Enter any topic to dispatch an autonomous team of AI agents that will search the web, "
    "scrape deep technical sources, draft a synthesized report, and conduct a strict peer review."
)

# Preset topic buttons for quick experimentation
st.markdown("##### ⚡ Quick Suggestion Topics")
sample_topics = [
    "Next-generation solid-state batteries in 2026",
    "Agentic AI workflows and LLM reasoning architectures",
    "Commercial viability of fusion energy reactors",
    "CRISPR gene therapy approvals and clinical trials"
]

cols = st.columns(len(sample_topics))
selected_sample = None
for idx, sample in enumerate(sample_topics):
    with cols[idx]:
        if st.button(sample, key=f"sample_{idx}", use_container_width=True):
            st.session_state.current_topic = sample

# Research Input
topic_input = st.text_input(
    "Enter Research Topic or Question:",
    value=st.session_state.current_topic,
    placeholder="e.g. Breakthroughs in Quantum Error Correction and commercial quantum computing...",
    help="Type any technical, academic, or industry research topic."
)

col_run, col_clear = st.columns([1, 5])
with col_run:
    start_btn = st.button("🚀 Start Research", type="primary", use_container_width=True)
with col_clear:
    if st.session_state.history and st.button("🧹 Clear Results"):
        st.session_state.history = None
        st.rerun()

# Execution Flow
if start_btn:
    if not topic_input.strip():
        st.error("Please enter a research topic first.")
    elif not (mistral_ok and tavily_ok):
        st.error("Missing API Keys! Please configure `MISTRAL_API_KEY` and `TAVILY_API_KEY` in your `.env` file.")
    else:
        st.session_state.current_topic = topic_input.strip()
        
        # Live multi-agent progression container
        with st.status("🧠 Multi-Agent Swarm at work...", expanded=True) as status:
            step_container = st.container()

            def handle_step(step_num: int, agent_name: str, status_text: str, content=None):
                if content is None:
                    step_container.write(f"⏳ **Step {step_num}: {agent_name}** — {status_text}")
                else:
                    step_container.write(f"✅ **Step {step_num}: {agent_name}** — {status_text}")

            try:
                start_time = time.time()
                result_state = run_research_pipeline(topic_input.strip(), step_callback=handle_step)
                elapsed = round(time.time() - start_time, 1)
                
                status.update(
                    label=f"🎉 Research completed in {elapsed}s across 4 agents!",
                    state="complete",
                    expanded=False
                )
                st.session_state.history = {
                    "topic": topic_input.strip(),
                    "state": result_state,
                    "elapsed": elapsed
                }
            except Exception as e:
                status.update(label="❌ Pipeline execution failed", state="error", expanded=True)
                st.error(f"Execution error: {str(e)}")

# Display Results View
if st.session_state.history:
    hist = st.session_state.history
    state = hist["state"]
    topic = hist["topic"]
    elapsed = hist["elapsed"]

    st.markdown("---")
    st.subheader(f"📊 Research Dossier: *{topic}*")
    st.caption(f"Generated via 4-agent consensus in {elapsed} seconds.")

    # Result Tabs
    tab_report, tab_critic, tab_search, tab_scrape = st.tabs([
        "📄 Research Report",
        "⚖️ Peer Review & Score",
        "🔍 Search Agent Data",
        "📖 Reader Agent Content"
    ])

    with tab_report:
        report_content = state.get("report", "No report generated.")
        st.markdown(report_content)
        
        st.markdown("---")
        # Download Button
        report_filename = f"research_{topic.lower()[:30].replace(' ', '_')}.md"
        st.download_button(
            label="📥 Download Research Report (.md)",
            data=report_content,
            file_name=report_filename,
            mime="text/markdown",
            use_container_width=True
        )

    with tab_critic:
        feedback_content = state.get("feedback", "No feedback recorded.")
        st.info("The Critic Agent evaluated the report based on factual depth, structure, and clarity.")
        st.markdown(feedback_content)

    with tab_search:
        st.markdown("#### Primary Search Results (Tavily)")
        search_data = state.get("search_results", "No search results recorded.")
        st.code(search_data, language="markdown")

    with tab_scrape:
        st.markdown("#### Scraped Primary Source Content (BeautifulSoup)")
        scraped_data = state.get("scraped_content", "No scraped content recorded.")
        st.text_area(
            "Extracted Raw Content",
            value=scraped_data,
            height=350,
            disabled=True
        )
