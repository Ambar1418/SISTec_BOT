"""
app.py - Main Streamlit App for SISTec AI Chatbot
Run with: streamlit run app.py
"""

import os
import time
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Page configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="SISTec AI Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject custom CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg-primary:    #06080f;
  --bg-secondary:  #0c0f1a;
  --bg-card:       #101422;
  --bg-input:      #0e1120;
  --border:        rgba(255,255,255,0.07);
  --border-accent: rgba(251,146,60,0.35);
  --accent:        #fb923c;
  --accent-2:      #f97316;
  --accent-glow:   rgba(251,146,60,0.18);
  --accent-soft:   rgba(251,146,60,0.08);
  --text-primary:  #f1f5f9;
  --text-secondary:#94a3b8;
  --text-muted:    #475569;
  --user-bg:       linear-gradient(135deg,#ea580c,#fb923c);
  --bot-bg:        #101422;
  --green:  #22c55e;
  --red:    #ef4444;
  --yellow: #f59e0b;
}

/* ── Global reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] {
  font-family: 'Sora', sans-serif !important;
  background: var(--bg-primary) !important;
  color: var(--text-primary) !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* Remove default padding */
.block-container { padding-top: 0 !important; padding-bottom: 0 !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--bg-secondary) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child {
  padding: 0 !important;
}

/* ── SIDEBAR LOGO STRIP ── */
.sb-logo {
  background: linear-gradient(160deg, #0f1626 0%, #0a0d18 100%);
  border-bottom: 1px solid var(--border);
  padding: 28px 20px 20px;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.sb-logo::before {
  content: '';
  position: absolute;
  top: -40px; right: -40px;
  width: 140px; height: 140px;
  border-radius: 50%;
  background: var(--accent-glow);
  filter: blur(40px);
}
.sb-logo-icon {
  font-size: 2.8rem;
  line-height: 1;
  margin-bottom: 10px;
  display: block;
  filter: drop-shadow(0 0 12px rgba(251,146,60,0.5));
}
.sb-logo-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.01em;
  margin-bottom: 3px;
}
.sb-logo-sub {
  font-size: 0.7rem;
  font-weight: 400;
  color: var(--text-muted);
  font-family: 'JetBrains Mono', monospace !important;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

/* ── Sidebar sections ── */
.sb-section-label {
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-muted);
  padding: 18px 20px 8px;
  display: block;
}

/* ── Status row ── */
.sb-status-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 20px;
}
.sb-status-label {
  font-size: 0.82rem;
  color: var(--text-secondary);
  font-weight: 500;
}
.sb-badge {
  font-size: 0.68rem;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  font-family: 'JetBrains Mono', monospace !important;
  letter-spacing: 0.03em;
}
.sb-badge-green { background: rgba(34,197,94,0.12); color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }
.sb-badge-red   { background: rgba(239,68,68,0.12);  color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
.sb-badge-yellow{ background: rgba(245,158,11,0.12); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }

/* ── Divider ── */
.sb-divider {
  border: none;
  border-top: 1px solid var(--border);
  margin: 12px 20px;
}

/* ── Buttons ── */
.stButton > button {
  background: transparent !important;
  color: var(--text-secondary) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  padding: 9px 16px !important;
  font-family: 'Sora', sans-serif !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
  width: 100% !important;
  text-align: left !important;
  transition: all 0.2s ease !important;
  letter-spacing: 0.01em !important;
}
.stButton > button:hover {
  background: var(--accent-soft) !important;
  border-color: var(--border-accent) !important;
  color: var(--accent) !important;
  transform: none !important;
  box-shadow: none !important;
}

/* Primary CTA button */
div[data-testid="stButton"]:has(button[kind="primary"]) button,
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #ea580c, #fb923c) !important;
  color: #fff !important;
  border: none !important;
  font-weight: 600 !important;
  box-shadow: 0 4px 20px rgba(251,146,60,0.25) !important;
}
.stButton > button[kind="primary"]:hover {
  box-shadow: 0 6px 28px rgba(251,146,60,0.4) !important;
  color: #fff !important;
}

/* Initialize & Send as primary feel */
.stButton > button:has(🚀),
div[data-testid="element-container"]:has(button) + div:has(button) .stButton > button {
  background: linear-gradient(135deg,#ea580c,#fb923c) !important;
  color: #fff !important;
  border: none !important;
  font-weight: 600 !important;
}

/* ── Suggestion pills ── */
.sug-pill {
  display: block;
  margin: 4px 20px;
  padding: 8px 14px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}
.sug-pill:hover {
  border-color: var(--border-accent);
  color: var(--accent);
  background: var(--accent-soft);
}

/* ── Main header ── */
.main-header {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  padding: 18px 32px;
  display: flex;
  align-items: center;
  gap: 14px;
}
.main-header-icon {
  font-size: 1.8rem;
  filter: drop-shadow(0 0 8px rgba(251,146,60,0.5));
}
.main-header-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}
.main-header-sub {
  font-size: 0.78rem;
  color: var(--text-muted);
  font-family: 'JetBrains Mono', monospace;
  margin-top: 2px;
}
.main-header-dot {
  width: 8px; height: 8px;
  background: var(--green);
  border-radius: 50%;
  margin-left: auto;
  box-shadow: 0 0 8px var(--green);
  animation: pulse-dot 2s infinite;
}
.main-header-dot.offline {
  background: var(--yellow);
  box-shadow: 0 0 8px var(--yellow);
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.5; transform: scale(1.3); }
}

/* ── Chat area ── */
.chat-outer {
  padding: 0 32px;
}
.chat-wrapper {
  max-height: 58vh;
  overflow-y: auto;
  padding: 24px 0 12px;
  scrollbar-width: thin;
  scrollbar-color: rgba(251,146,60,0.3) transparent;
}
.chat-wrapper::-webkit-scrollbar { width: 4px; }
.chat-wrapper::-webkit-scrollbar-track { background: transparent; }
.chat-wrapper::-webkit-scrollbar-thumb { background: rgba(251,146,60,0.3); border-radius: 2px; }

/* ── Message bubbles ── */
.msg-row { display: flex; margin-bottom: 20px; gap: 12px; align-items: flex-end; }
.msg-row.user { flex-direction: row-reverse; }
.msg-row.bot  { flex-direction: row; }

.avatar {
  width: 32px; height: 32px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}
.avatar-user {
  background: linear-gradient(135deg, #ea580c, #fb923c);
  box-shadow: 0 4px 12px rgba(251,146,60,0.3);
}
.avatar-bot {
  background: var(--bg-card);
  border: 1px solid var(--border);
}

.bubble {
  max-width: 75%;
  padding: 13px 17px;
  border-radius: 16px;
  font-size: 0.9rem;
  line-height: 1.7;
  position: relative;
}
.bubble-user {
  background: var(--user-bg);
  color: #fff;
  border-radius: 16px 16px 4px 16px;
  box-shadow: 0 4px 20px rgba(251,146,60,0.25);
}
.bubble-bot {
  background: var(--bot-bg);
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-radius: 16px 16px 16px 4px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.3);
}
.msg-time {
  font-size: 0.65rem;
  color: var(--text-muted);
  margin-top: 5px;
  font-family: 'JetBrains Mono', monospace;
}
.msg-time.right { text-align: right; }

/* ── Source pills ── */
.sources-wrap { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 5px; }
.source-pill {
  display: inline-flex; align-items: center; gap: 4px;
  background: rgba(251,146,60,0.08);
  border: 1px solid rgba(251,146,60,0.25);
  color: #fb923c;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
}
.source-pill:hover {
  background: rgba(251,146,60,0.16);
  border-color: var(--accent);
}

/* ── Welcome screen ── */
.welcome-screen {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  min-height: 38vh;
  text-align: center;
  padding: 40px 20px;
}
.welcome-badge {
  display: inline-block;
  background: var(--accent-soft);
  border: 1px solid var(--border-accent);
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 5px 14px;
  border-radius: 20px;
  margin-bottom: 20px;
  font-family: 'JetBrains Mono', monospace;
}
.welcome-heading {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
  margin-bottom: 12px;
  letter-spacing: -0.02em;
}
.welcome-heading span { color: var(--accent); }
.welcome-sub {
  font-size: 0.9rem;
  color: var(--text-secondary);
  max-width: 420px;
  line-height: 1.7;
  margin-bottom: 28px;
}
.welcome-tags { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
.welcome-tag {
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 0.78rem;
  padding: 5px 12px;
  border-radius: 6px;
}

/* ── Input area ── */
.input-area {
  position: sticky; bottom: 0;
  background: var(--bg-primary);
  border-top: 1px solid var(--border);
  padding: 16px 32px 20px;
}
.stTextInput > div > div > input {
  background: var(--bg-input) !important;
  border: 1px solid var(--border) !important;
  color: var(--text-primary) !important;
  border-radius: 12px !important;
  padding: 14px 18px !important;
  font-size: 0.88rem !important;
  font-family: 'Sora', sans-serif !important;
  transition: all 0.2s !important;
}
.stTextInput > div > div > input:focus {
  border-color: var(--border-accent) !important;
  box-shadow: 0 0 0 3px var(--accent-glow) !important;
  outline: none !important;
}
.stTextInput > div > div > input::placeholder {
  color: var(--text-muted) !important;
}

/* ── Send button override ── */
div[data-testid="column"]:last-child .stButton > button {
  background: linear-gradient(135deg,#ea580c,#fb923c) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 12px !important;
  font-weight: 600 !important;
  font-size: 0.88rem !important;
  padding: 14px 18px !important;
  letter-spacing: 0.01em !important;
  box-shadow: 0 4px 16px rgba(251,146,60,0.3) !important;
  text-align: center !important;
}
div[data-testid="column"]:last-child .stButton > button:hover {
  box-shadow: 0 6px 24px rgba(251,146,60,0.5) !important;
  color: #fff !important;
}

/* Initialize chatbot button */
div[data-testid="stSidebar"] .stButton > button {
  text-align: center !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--text-secondary) !important;
  font-size: 0.82rem !important;
  font-family: 'Sora', sans-serif !important;
}
.streamlit-expanderContent {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
}

/* ── Alerts ── */
.stAlert {
  border-radius: 10px !important;
  font-family: 'Sora', sans-serif !important;
  font-size: 0.85rem !important;
}
.stSuccess { background: rgba(34,197,94,0.08) !important; border: 1px solid rgba(34,197,94,0.25) !important; }
.stWarning { background: rgba(245,158,11,0.08) !important; border: 1px solid rgba(245,158,11,0.25) !important; }
.stError   { background: rgba(239,68,68,0.08)  !important; border: 1px solid rgba(239,68,68,0.25)  !important; }

/* ── Spinner ── */
.stSpinner > div > div { border-top-color: var(--accent) !important; }

/* ── Typing dots ── */
.typing-wrap { display: flex; align-items: center; gap: 4px; padding: 6px 0; }
.typing-dot {
  width: 7px; height: 7px;
  background: var(--accent);
  border-radius: 50%;
  animation: bounce-dot 1.3s infinite;
  opacity: 0.7;
}
.typing-dot:nth-child(2) { animation-delay: 0.18s; }
.typing-dot:nth-child(3) { animation-delay: 0.36s; }
@keyframes bounce-dot {
  0%, 60%, 100% { transform: translateY(0);  opacity: 0.7; }
  30%            { transform: translateY(-7px); opacity: 1; }
}

/* Progress bar */
.stProgress > div > div > div {
  background: linear-gradient(90deg,#ea580c,#fb923c) !important;
  border-radius: 4px !important;
}

/* Scrollbar for main area */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Imports ─────────────────────────────────────────────────────────────
from rag_pipeline import initialize_rag, query_rag, vectorstore_exists

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None
if "init_error" not in st.session_state:
    st.session_state.init_error = None

if "is_initialized" not in st.session_state:
    st.session_state.is_initialized = False
    if vectorstore_exists():
        try:
            st.session_state.rag_chain = initialize_rag([], progress_callback=lambda x: None)
            st.session_state.is_initialized = True
        except Exception as e:
            st.session_state.init_error = f"Auto-init failed: {e}"

# ── Source pills helper ───────────────────────────────────────────────────────
def render_sources(sources):
    if not sources:
        return ""
    html = '<div class="sources-wrap">'
    for url in sources[:4]:
        label = url.rstrip("/").split("/")[-1].replace("-", " ").replace("_", " ").title() or "Home"
        html += f'<a href="{url}" target="_blank" class="source-pill">↗ {label}</a>'
    html += "</div>"
    return html


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:

    # Logo strip
    st.markdown("""
    <div class="sb-logo">
      <span class="sb-logo-icon">🎓</span>
      <div class="sb-logo-title">SISTec AI Assistant</div>
      <div class="sb-logo-sub">Sagar Group of Institutions · Bhopal</div>
    </div>
    """, unsafe_allow_html=True)

    # System status
    st.markdown('<span class="sb-section-label">System Status</span>', unsafe_allow_html=True)

    vs_ok = vectorstore_exists()
    init_ok = st.session_state.is_initialized

    for label, ok, on_label, off_label in [
        ("Vector Store",  vs_ok,     "Ready",   "Missing"),
        ("Chatbot",       init_ok,   "Online",  "Offline"),
    ]:
        badge_cls = "sb-badge-green" if ok else ("sb-badge-yellow" if label == "Chatbot" and not ok else "sb-badge-red")
        badge_txt = on_label if ok else off_label
        st.markdown(f"""
        <div class="sb-status-row">
          <span class="sb-status-label">{label}</span>
          <span class="sb-badge {badge_cls}">{badge_txt}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # Initialize info
    if not st.session_state.is_initialized:
        if not vectorstore_exists():
            st.error("Vector store missing! Please ensure 'vectorstore/' folder is uploaded.")
        else:
            st.info("Initializing chatbot...")
            try:
                st.session_state.rag_chain = initialize_rag([], progress_callback=lambda x: None)
                st.session_state.is_initialized = True
                st.rerun()
            except Exception as e:
                st.error(f"Initialization failed: {e}")
    else:
        st.success("✓  Chatbot is Online")

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    if st.button("🗑️  Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
    st.markdown('<span class="sb-section-label">Suggested Questions</span>', unsafe_allow_html=True)

    suggestions = [
        "What courses does SISTec offer?",
        "How do I apply for admission?",
        "What are the placement statistics?",
        "Tell me about the departments",
        "What facilities are available?",
        "How to contact the college?",
    ]
    for q in suggestions:
        if st.button(q, use_container_width=True, key=f"sug_{q[:20]}"):
            st.session_state["pending_question"] = q
            st.rerun()

    st.markdown("""
    <hr class="sb-divider">
    <div style="text-align:center;padding:8px 0 16px;color:var(--text-muted);font-size:0.72rem;line-height:1.8;">
      Data sourced from<br>
      <a href="https://www.sistec.ac.in/" target="_blank"
         style="color:var(--accent);text-decoration:none;font-weight:600;">
        sistec.ac.in
      </a>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# MAIN AREA
# ═══════════════════════════════════════════════════════════════
dot_class = "main-header-dot" if st.session_state.is_initialized else "main-header-dot offline"
st.markdown(f"""
<div class="main-header">
  <span class="main-header-icon">🎓</span>
  <div>
    <div class="main-header-title">SISTec AI Assistant</div>
    <div class="main-header-sub">Sagar Institute of Science, Technology &amp; Engineering · Bhopal</div>
  </div>
  <div class="{dot_class}"></div>
</div>
""", unsafe_allow_html=True)

# Error banner
if st.session_state.init_error:
    st.error(f"Setup Error: {st.session_state.init_error}")
    st.info("Please check the sidebar and ensure your API keys are set in `.env`")

# ── Chat display ──────────────────────────────────────────────
st.markdown('<div class="chat-outer"><div class="chat-wrapper">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-screen">
      <div class="welcome-badge">AI-Powered · RAG + LLM</div>
      <div class="welcome-heading">Hello! I'm your<br><span>SISTec Assistant</span></div>
      <div class="welcome-sub">
        Ask me anything about courses, admissions, placements,
        faculty, departments, facilities, events &amp; more.
      </div>
      <div class="welcome-tags">
        <span class="welcome-tag">🎓 Courses</span>
        <span class="welcome-tag">📋 Admissions</span>
        <span class="welcome-tag">💼 Placements</span>
        <span class="welcome-tag">🏛️ Departments</span>
        <span class="welcome-tag">🏠 Facilities</span>
        <span class="welcome-tag">📞 Contact</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        ts = msg.get("time", "")
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="msg-row user">
              <div class="avatar avatar-user">👤</div>
              <div>
                <div class="bubble bubble-user">{msg["content"]}</div>
                <div class="msg-time right">{ts}</div>
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            sources_html = render_sources(msg.get("sources", []))
            st.markdown(f"""
            <div class="msg-row bot">
              <div class="avatar avatar-bot">🎓</div>
              <div>
                <div class="bubble bubble-bot">{msg["content"]}{sources_html}</div>
                <div class="msg-time">{ts}</div>
              </div>
            </div>""", unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

# ── Input area ────────────────────────────────────────────────
st.markdown('<div class="input-area">', unsafe_allow_html=True)
col_input, col_send = st.columns([5, 1])

with col_input:
    pending = st.session_state.pop("pending_question", None)
    user_input = st.text_input(
        "message",
        value=pending or "",
        placeholder="Ask anything about SISTec — admissions, courses, placements…",
        label_visibility="collapsed",
        key="chat_input",
    )

with col_send:
    send_clicked = st.button("Send ➤", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Process question ──────────────────────────────────────────
if (send_clicked or pending) and user_input.strip():
    question = user_input.strip()

    if not st.session_state.is_initialized or st.session_state.rag_chain is None:
        st.warning("Please initialize the chatbot first using the sidebar button.")
    else:
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M")
        st.session_state.messages.append({"role": "user", "content": question, "time": ts})

        with st.spinner(""):
            st.markdown("""
            <div class="msg-row bot">
              <div class="avatar avatar-bot">🎓</div>
              <div class="bubble bubble-bot">
                <div class="typing-wrap">
                  <div class="typing-dot"></div>
                  <div class="typing-dot"></div>
                  <div class="typing-dot"></div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

            answer, sources = query_rag(st.session_state.rag_chain, question)

        ts_bot = datetime.now().strftime("%H:%M")
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "time": ts_bot,
        })
        st.rerun()