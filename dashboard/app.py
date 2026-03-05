"""
dashboard/app.py

AutoClaw Live Monitoring Dashboard — built with Streamlit.
Run with: streamlit run dashboard/app.py
"""

import os
import sys
import streamlit as st
import pandas as pd

# Ensure the project root is on the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dashboard.db_queries import get_all_jobs, get_applied_jobs, get_stats

# ── Page Config ─────────────────────────────────────────────
st.set_page_config(
    page_title="AutoClaw Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background: #1c2333;
        border-radius: 10px;
        padding: 14px 20px;
        margin-bottom: 10px;
    }
    .status-applied  { color: #22c55e; font-weight: bold; }
    .status-skipped  { color: #f59e0b; font-weight: bold; }
    .status-discovered { color: #60a5fa; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar: Live Stats ──────────────────────────────────────
st.sidebar.image("https://avatars.githubusercontent.com/u/9919?s=80", width=50)
st.sidebar.title("🤖 AutoClaw")
st.sidebar.caption("AI Job Application Engine")
st.sidebar.divider()

@st.cache_data(ttl=30)
def load_stats():
    return get_stats()

stats = load_stats()

st.sidebar.metric("📋 Total Discovered", stats["total"])
st.sidebar.metric("✅ Applied", stats["applied"])
st.sidebar.metric("⏭️ Skipped", stats["skipped"])
st.sidebar.metric("⏳ Pending", stats["pending"])

if stats["total"] > 0:
    apply_rate = round((stats["applied"] / stats["total"]) * 100, 1)
    st.sidebar.progress(stats["applied"] / stats["total"])
    st.sidebar.caption(f"Apply rate: {apply_rate}%")

st.sidebar.divider()
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# ── Main Area ────────────────────────────────────────────────
st.title("🤖 AutoClaw Live Dashboard")
st.caption("Real-time view of job discovery and application pipeline. Auto-refreshes every 30s.")
st.divider()

# 3 Tabs
tab1, tab2, tab3 = st.tabs(["📋 Jobs Discovered", "✅ Jobs Applied", "🧠 LLM Match Scores"])

# ── Tab 1: All Discovered Jobs ───────────────────────────────
with tab1:
    st.subheader("All Discovered Jobs")

    @st.cache_data(ttl=30)
    def load_all_jobs():
        return get_all_jobs()

    df_all = load_all_jobs()

    if df_all.empty:
        st.info("No jobs discovered yet. AutoClaw is warming up...")
    else:
        # Color-code the Status column
        def highlight_status(val):
            colors = {
                "applied":    "color: #22c55e; font-weight: bold;",
                "skipped":    "color: #f59e0b; font-weight: bold;",
                "discovered": "color: #60a5fa; font-weight: bold;",
            }
            return colors.get(str(val).lower(), "")

        styled_df = df_all.style.applymap(highlight_status, subset=["Status"])
        st.dataframe(styled_df, use_container_width=True, height=450)
        st.caption(f"Showing {len(df_all)} jobs")

# ── Tab 2: Applied Jobs ──────────────────────────────────────
with tab2:
    st.subheader("Jobs Applied To")

    @st.cache_data(ttl=30)
    def load_applied_jobs():
        return get_applied_jobs()

    df_applied = load_applied_jobs()

    if df_applied.empty:
        st.info("No applications submitted yet.")
    else:
        def highlight_success(val):
            if val is True or val == 1:
                return "color: #22c55e; font-weight: bold;"
            elif val is False or val == 0:
                return "color: #ef4444; font-weight: bold;"
            return ""

        styled_applied = df_applied.style.applymap(highlight_success, subset=["Success"])
        st.dataframe(styled_applied, use_container_width=True, height=450)
        st.caption(f"Showing {len(df_applied)} applications")

# ── Tab 3: LLM Match Scores ──────────────────────────────────
with tab3:
    st.subheader("Recent LLM Match Scores & Notes")

    df_scores = load_applied_jobs()

    if df_scores.empty:
        st.info("No LLM scores recorded yet.")
    else:
        # Show only jobs that have notes (match scores are stored in the notes field)
        df_with_notes = df_scores[df_scores["Notes / LLM Score"].notna() & (df_scores["Notes / LLM Score"] != "")]

        if df_with_notes.empty:
            st.info("Jobs have been applied to, but no LLM scores recorded yet.")
        else:
            for _, row in df_with_notes.iterrows():
                with st.expander(f"🏢 {row['Company']} — {row['Title']}"):
                    st.write(f"**Applied At:** {row['Applied At']}")
                    st.write(f"**Success:** {'✅ Yes' if row['Success'] else '❌ No'}")
                    st.markdown(f"**LLM Notes:**\n\n{row['Notes / LLM Score']}")
