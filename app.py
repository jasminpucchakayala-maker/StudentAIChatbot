import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
import time
import os
import config
from chatbot import StudentChatbot
from utils.history import (
    load_chat_history, 
    clear_chat_history, 
    export_history_to_csv, 
    export_history_to_json
)
from utils.helpers import (
    format_response_time, 
    calculate_analytics_metrics, 
    generate_intent_bar_chart, 
    generate_confidence_pie_chart, 
    generate_response_time_line_chart
)

# Page Configuration
st.set_page_config(
    page_title=f"{config.APP_TITLE} - AI Student Query Chatbot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- SESSION STATE SETUP -----------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chatbot" not in st.session_state:
    with st.spinner("Initializing AI Brain and Loading Datasets..."):
        st.session_state.chatbot = StudentChatbot()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "theme" not in st.session_state:
    st.session_state.theme = "Dark Mode"

if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

if "stats_key" not in st.session_state:
    st.session_state.stats_key = 0

# ----------------- INJECT CUSTOM CSS -----------------
def load_css():
    css_path = config.STYLES_DIR / "style.css"
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            
load_css()

# Theme Overcharge Logic
if "Light Mode" in st.session_state.theme:
    st.markdown("""
        <style>
        :root {
            --bg-dark: #F8FAFC !important;
            --glass-bg: rgba(14, 165, 233, 0.03) !important;
            --glass-border: rgba(14, 165, 233, 0.12) !important;
            --bot-bubble-bg: rgba(226, 232, 240, 0.85) !important;
            --user-bubble-bg: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%) !important;
            
            /* Theme color overrides for light mode readability */
            --text-main: #1E293B !important;
            --text-muted: #475569 !important;
            --card-bg: rgba(255, 255, 255, 0.92) !important;
            --card-border: rgba(14, 165, 233, 0.12) !important;
        }
        .chat-bubble-bot .bubble-content { color: var(--text-main) !important; }
        .chat-bubble-bot .bubble-meta { color: var(--text-muted) !important; }
        .chat-bubble-user .bubble-content { color: #FFFFFF !important; }
        .chat-bubble-user .bubble-meta { color: rgba(255, 255, 255, 0.6) !important; }
        .stApp { background-color: #F8FAFC !important; color: #1E293B !important; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp { background-color: #0F172A !important; color: #F1F5F9 !important; }
        </style>
    """, unsafe_allow_html=True)

# ----------------- SIDEBAR INTERFACE -----------------
with st.sidebar:
    # Project Identity
    # Display logo placeholder if logo doesn't exist
    logo_path = config.ASSETS_DIR / "logo.png"
    if os.path.exists(logo_path):
        st.image(str(logo_path), width=75)
    else:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%); width: 64px; height: 64px; 
                         border-radius: 12px; display: flex; align-items: center; justify-content: center; 
                         font-size: 28px; color: white; font-weight: bold; margin-bottom: 12px; box-shadow: 0 4px 10px rgba(14, 165, 233, 0.3);'>
                EQ
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown(f"### {config.APP_TITLE}")
    
    st.markdown("---")
    
    # Navigation Selector
    menu = st.radio(
        "Navigate Platform",
        ["💬 AI Chat Copilot", "📊 Analytics Dashboard", "📋 Intent Log Table", "ℹ️ About & Reference"],
        index=0
    )
    
    st.markdown("---")
    
    # Themes & Display Controls
    selected_theme = st.selectbox(
        "Aesthetic Theme Style",
        ["🌌 Dark Mode", "☀️ Light Mode"],
        index=0 if "Dark" in st.session_state.theme else 1
    )
    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.rerun()

    # Session Activity Details
    st.markdown("##### Session Diagnostics")
    live_time = datetime.now().strftime("%I:%M %p")
    st.markdown(f"""
        <div class='status-pill'>
            <div class='status-dot'></div> System Online | {live_time}
        </div>
    """, unsafe_allow_html=True)
    
    history_df = load_chat_history()
    stats = calculate_analytics_metrics(history_df)
    
    st.write(f"⏱️ **Local Date**: {date.today().strftime('%b %d, %Y')}")
    st.write(f"🔄 **Session ID**: `{st.session_state.session_id[:8]}...`")
    st.write(f"❓ **Total Questions Count**: `{stats['total_questions']}`")
    
    st.markdown("---")
    
    # Quick Commands Block
    st.markdown("##### Conversation Controls")
    col_clear, col_reload = st.columns(2)
    with col_clear:
        if st.button("🗑️ Reset Chat", use_container_width=True):
            st.session_state.messages = []
            st.toast("Chat container flushed locally!")
            st.rerun()
    with col_reload:
        if st.button("🔄 Clear System logs", use_container_width=True, help="Wipes CSV database records"):
            if clear_chat_history():
                st.session_state.stats_key += 1
                st.toast("Internal log registers flushed!")
                st.rerun()
                
    # Direct Downloads
    if not history_df.empty:
        st.markdown("##### Export Data registers")
        csv_data = export_history_to_csv()
        json_data = export_history_to_json()
        
        st.download_button(
            label="📥 Download CSV Logs",
            data=csv_data,
            file_name=f"chat_logs_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        st.download_button(
            label="📥 Export JSON Transcript",
            data=json_data,
            file_name=f"chat_transcript_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )

# ----------------- MAIN PAGES HANDLING -----------------

# Process suggestion chips click immediately before drawing layout
if st.session_state.pending_query:
    user_query = st.session_state.pending_query
    st.session_state.pending_query = None  # Clear immediately
    
    # 1. Save user item to state
    st.session_state.messages.append({"role": "user", "content": user_query, "time": datetime.now().strftime("%I:%M %p")})
    
    # 2. Query Agent
    reply_dict = st.session_state.chatbot.get_response(user_query, st.session_state.session_id)
    
    # 3. Save agent item to state
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply_dict["response"],
        "time": datetime.now().strftime("%I:%M %p"),
        "confidence": reply_dict["confidence"],
        "intent": reply_dict["intent"],
        "suggestions": reply_dict["suggestions"],
        "time_taken": reply_dict["response_time"]
    })
    st.rerun()


# A) AI CHAT COPILOT
if menu == "💬 AI Chat Copilot":
    
    # Title Banner and Header
    st.markdown(f"<div class='gradient-title'>{config.APP_TITLE}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='gradient-subtitle'>{config.APP_SUBTITLE}</div>", unsafe_allow_html=True)
    
    # Welcome Card (if conversation is empty)
    if not st.session_state.messages:
        st.markdown("""
            <div class='glass-container' style='text-align: left; max-width: 800px; margin-bottom: 2rem;'>
                <h4 style='margin-top:0; color:#38BDF8; font-weight:600;'>Welcome to the Student Academic Portal Copilot! 👋</h4>
                <p style='font-size:0.92rem; line-height:1.6; color:var(--text-muted);'>
                    I am an NLP-powered chatbot designed to resolve queries regarding college operations instantly. 
                    Search for topics using conversational sentences. Or click any common template chip below.
                </p>
                <div style='display:flex; flex-direction:column; gap:8px; font-size:0.85rem; color:var(--text-main); margin-top:1rem;'>
                    <div>💡 <b>Admissions & Courses</b>: "How do I take admission?" or "What MCA subjects are there?"</div>
                    <div>💰 <b>Finances</b>: "Tell me about tuition fee packages" or "Merit scholarships eligibility"</div>
                    <div>🏥 <b>Campus Welfare</b>: "Is there a hostel mess?" or "How is anti-ragging handled here?"</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    # Render Conversation Logs
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
                <div class='chat-bubble chat-bubble-user'>
                    <div class='chat-avatar'>👤</div>
                    <div class='bubble-content'>
                        {msg['content']}
                        <span class='bubble-meta'>{msg['time']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            # Stats metrics display metadata helper inside bot envelope
            meta_line = f"Metric: {format_response_time(msg['time_taken'])} | Conf: {int(msg['confidence']*100)}%"
            if msg['intent'] != 'unknown' and msg['confidence'] < 1.0:
                meta_line += f" | Categorized: {msg['intent'].capitalize()}"
                
            st.markdown(f"""
                <div class='chat-bubble chat-bubble-bot'>
                    <div class='chat-avatar'>🤖</div>
                    <div class='bubble-content'>
                        {msg['content']}
                        <span class='bubble-meta'>{msg['time']} • {meta_line}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
    # Check for suggested buttons from the LAST message if it came from the assistant
    current_suggestions = []
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
        current_suggestions = st.session_state.messages[-1].get("suggestions", [])
    else:
        # Defaults
        current_suggestions = config.SUGGESTED_QUESTIONS[:4]
        
    if current_suggestions:
        st.markdown("<p style='font-size:0.8rem; margin: 1.5rem 0 0.2rem 0; color:#64748B; font-weight:600;'>SUGGESTED FOLLOW-UP QUESTIONS:</p>", unsafe_allow_html=True)
        cols = st.columns(len(current_suggestions))
        for idx, sug in enumerate(current_suggestions):
            with cols[idx]:
                # Streamlit standard button click will reload and submit
                if st.button(sug, key=f"sug_{idx}", use_container_width=True, type="secondary"):
                    st.session_state.pending_query = sug
                    st.rerun()

    # Chat Room Core Input Textbox
    user_input = st.chat_input("Input your query here... (e.g. What is the fee of hostlers?)")
    if user_input:
        st.session_state.pending_query = user_input
        st.rerun()

# B) ANALYTICS DASHBOARD
elif menu == "📊 Analytics Dashboard":
    st.markdown(f"<div class='gradient-title'>System Intelligence Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<p class='gradient-subtitle'>Live aggregate utilization metrics loaded from system CSV logs.</p>", unsafe_allow_html=True)
    
    if history_df.empty:
        st.info("No query registers recorded yet! Interact with the robot to build visual analytics here.")
    else:
        # 1. Top Numeric Stats Cards row
        st.markdown(f"### System KPI Registers (Based on {len(history_df)} entries)", unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-val'>{stats['total_questions']}</div>
                    <div class='metric-lbl'>Total Requests</div>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-val'>{stats['questions_today']}</div>
                    <div class='metric-lbl'>Requests Today</div>
                </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-val'>{format_response_time(stats['avg_response_time'])}</div>
                    <div class='metric-lbl'>Avg Response Time</div>
                </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-val'>{stats['avg_confidence']*100:.1f}%</div>
                    <div class='metric-lbl'>Recognition Confidence</div>
                </div>
            """, unsafe_allow_html=True)
            
        c5, c6 = st.columns(2)
        with c5:
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-val'>{stats['most_common_category']}</div>
                    <div class='metric-lbl'>Most Active Subject Topic</div>
                </div>
            """, unsafe_allow_html=True)
        with c6:
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-val'>{stats['unknown_percentage']:.1f}%</div>
                    <div class='metric-lbl'>Fallback/Unknown Rate</div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        
        # 2. Plotly Charts Row
        st.markdown("### User Search Trends & Topic Distributions")
        g1, g2 = st.columns(2)
        with g1:
            fig_bar = generate_intent_bar_chart(history_df)
            if fig_bar:
                st.plotly_chart(fig_bar, use_container_width=True)
        with g2:
            fig_pie = generate_confidence_pie_chart(history_df)
            if fig_pie:
                st.plotly_chart(fig_pie, use_container_width=True)
                
        st.markdown("---")
        
        # 3. Response speed charts
        st.markdown("### Performance Indicators")
        fig_line = generate_response_time_line_chart(history_df)
        if fig_line:
            st.plotly_chart(fig_line, use_container_width=True)

# C) INTENT LOG TABLE
elif menu == "📋 Intent Log Table":
    st.markdown(f"<div class='gradient-title'>Interactive Data Registers</div>", unsafe_allow_html=True)
    st.markdown("<p class='gradient-subtitle'>View, filter, and inspect raw transaction log rows.</p>", unsafe_allow_html=True)
    
    if history_df.empty:
        st.info("Log database is empty. Once queries occur, they populate records here.")
    else:
        st.markdown("##### Filter Log Register Entries")
        search_term = st.text_input("🔍 Search user queries or robot replies:")
        
        filtered_df = history_df.copy()
        if search_term:
            filtered_df = filtered_df[
                filtered_df["UserQuestion"].str.contains(search_term, case=False, na=False) |
                filtered_df["BotResponse"].str.contains(search_term, case=False, na=False) |
                filtered_df["IntentMatched"].str.contains(search_term, case=False, na=False)
            ]
            
        st.write(f"Showing {len(filtered_df)} of {len(history_df)} entries:")
        
        # Format datetimes for cleaner display
        display_df = filtered_df.copy()
        display_df["Timestamp"] = display_df["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
        
        st.dataframe(
            display_df.sort_values(by="Timestamp", ascending=False),
            use_container_width=True,
            column_config={
                "Timestamp": st.column_config.TextColumn("Date & Time"),
                "SessionID": st.column_config.TextColumn("Session ID"),
                "UserQuestion": st.column_config.TextColumn("Question"),
                "BotResponse": st.column_config.TextColumn("Agent Reply"),
                "IntentMatched": st.column_config.TextColumn("Matched Intent"),
                "Confidence": st.column_config.NumberColumn("Confidence", format="%.2f"),
                "ResponseTimeSec": st.column_config.NumberColumn("Response Speed (sec)", format="%.4f")
            }
        )

# D) ABOUT & REFERENCE
else:
    st.markdown(f"<div class='gradient-title'>About & Academic Reference</div>", unsafe_allow_html=True)
    st.markdown("<p class='gradient-subtitle'>Documentation, design architecture, and system details.</p>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class='glass-container'>
            <h4 style='margin-top:0; color:#38BDF8; font-weight:600;'>System Intentions & Objectives 🎯</h4>
            <p style='font-size:0.95rem; line-height:1.6; color:var(--text-main); margin-bottom:1.5rem;'>
                Developed for an academic internship review board, this project models an advanced student affairs 
                copilot. It solves high-volume, repetitive inquiries regarding campus guidelines and enrollment 
                schedules instantly, reducing workload on institutional administration.
            </p>
            <h4 style='color:#38BDF8; font-weight:600;'>NLP Pre-processing & Similarity Logic ⚙️</h4>
            <ul style='font-size:0.92rem; line-height:1.7; color:var(--text-main);'>
                <li><b>Text Normalization</b>: Lowercases characters, strips punctuation, and matches regex spaces.</li>
                <li><b>NLTK Word Tokenization</b>: Segmenting conversational paragraphs into semantic term matrices.</li>
                <li><b>State-Clean Stopwords</b>: Weeding out connectors ("a", "is", "about") to improve match performance.</li>
                <li><b>WordNet Lemmatizer</b>: Canonical reduction of plurals or tenses (e.g. <i>admissions</i> $\to$ <i>admission</i>).</li>
                <li><b>Fuzzy Hybrid Matching</b>: Merges Jaccard/Overlap sets with Levenshtein fuzzy distance checks.</li>
            </ul>
        </div>
        
        <div class='glass-container' style='margin-top:-0.5rem;'>
            <h4 style='margin-top:0; color:#38BDF8; font-weight:600;'>Platform Capabilities ⚡</h4>
            <div class='faq-grid'>
                <div class='faq-card'>
                    <div class='faq-card-title'>⚡ Ultra Fast Matches</div>
                    <div class='faq-card-desc'>Matches are calculated locally, with response speeds under 15 milliseconds.</div>
                </div>
                <div class='faq-card'>
                    <div class='faq-card-title'>🎨 Glassmorphic Layout</div>
                    <div class='faq-card-desc'>Custom stylesheet with hover blurs, smooth rounded bounds, offsets, and shadows.</div>
                </div>
                <div class='faq-card'>
                    <div class='faq-card-title'>📊 Integrated Analytics</div>
                    <div class='faq-card-desc'>Real-time dashboard charting common categories, intent confidence, and timings.</div>
                </div>
                <div class='faq-card'>
                    <div class='faq-card-title'>📥 Log Downloads</div>
                    <div class='faq-card-desc'>Export conversation histories easily in CSV or JSON schemas for auditing.</div>
                </div>
            </div>
        </div>
        
        <div class='glass-container' style='margin-top:-0.5rem;'>
            <h4 style='margin-top:0; color:#38BDF8; font-weight:600;'>Tech Stack Breakdown 🛠️</h4>
            <ul style='font-size:0.90rem; line-height:1.7; color:var(--text-main);'>
                <li><b>Frontend Framework</b>: Streamlit web framework</li>
                <li><b>Styling Extensions</b>: HTML5, CSS Variables, and Javascript custom injection</li>
                <li><b>NLP Engine</b>: NLTK (Tokenization, Stopwords, WordNetLemmatizer)</li>
                <li><b>String Comparison</b>: RapidFuzz / FuzzyWuzzy / Difflib</li>
                <li><b>Logs & Dashboards</b>: Pandas, Plotly Express & Graph Objects</li>
            </ul>
            <h4 style='color:#38BDF8; font-weight:600; margin-top:2rem;'>Developer and License Information 📝</h4>
            <p style='font-size:0.90rem; line-height:1.6; color:var(--text-muted);'>
                <b>Author</b>: Antigravity Dev Team & Student Intern<br>
                <b>System Version</b>: v2.1.0-Beta<br>
                <b>Build Target</b>: Production Sandbox Internship Submission<br>
                <b>License</b>: MIT License. Open source.
            </p>
        </div>
    """, unsafe_allow_html=True)

# ----------------- FOOTER SECTION -----------------
st.markdown(f"""
    <div class='footer-text'>
        CHINGU AI • {datetime.now().year} • Created with Python & Streamlit • Developer Team Internship Submission<br>
        <span style='font-size:0.75rem; color:#475569;'>Responsive HTML5 | PEP8 Checked | Glassmorphic design</span>
    </div>
""", unsafe_allow_html=True)
