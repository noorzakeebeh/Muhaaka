import streamlit as st
import html
import json
import os
import datetime

from audio_handler import transcribe_audio_bytes, TranscriptionError
from llm_evaluator import generate_interview_question, evaluate_interview_answer, EvaluationError

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Muhaaka | AI Interview Simulator",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# APP CONFIG
# ============================================================
DEFAULT_NUM_QUESTIONS = 3
NUM_QUESTIONS_OPTIONS = [1, 2, 3, 4, 5]

LEADERBOARD_FILE = "leaderboard.json"
LEADERBOARD_TOP_N = 5
KIOSK_REFRESH_SECONDS = 20

SPECIALIZATIONS = [
    "Computer Science",
    "Software Engineering",
    "Computer Engineering",
    "Computer Information Systems (CIS)",
    "Management Information Systems (MIS)",
    "Business Information Technology (BIT)",
    "Artificial Intelligence",
    "Data Science",
    "Cyber Security",
    "Network Engineering",
    "Cloud Computing",
    "Web Development",
    "Mobile App Development",
    "Multimedia & Visual Computing",
    "Intelligent Systems",
]

# ============================================================
# 🔌 LIVE INTEGRATIONS (Member 1 + Member 2)
# ============================================================

def transcribe_audio(audio_file) -> str:
    """Transcribes a Streamlit audio_input recording via Member 1's Whisper wrapper."""
    if audio_file is None:
        return ""
    filename = getattr(audio_file, "name", "answer.wav")
    try:
        return transcribe_audio_bytes(audio_file.getvalue(), filename=filename)
    except TranscriptionError as e:
        st.error(f"🎙️ {e}")
        return ""


def get_question(specialization: str) -> str:
    """Generates a real interview question via Member 2's LLM wrapper."""
    try:
        return generate_interview_question(specialization)
    except EvaluationError as e:
        st.error(f"❓ {e}")
        return "We couldn't generate a question right now — please try starting again."


def get_feedback(name: str, question: str, answer: str) -> dict:
    """
    Evaluates the candidate's answer via Member 2's LLM wrapper.
    Returns a dict: {welcome, score (0-100), rating, strengths[], gaps[], tips[], model_answer}.
    """
    try:
        return evaluate_interview_answer(name, question, answer)
    except EvaluationError as e:
        st.error(f"📊 {e}")
        return {
            "welcome": f"Welcome, {name}!",
            "score": 0,
            "rating": "N/A",
            "strengths": [],
            "gaps": ["We couldn't evaluate your answer right now — please try again."],
            "tips": [],
            "model_answer": "",
        }

# ============================================================
# 🏆 LEADERBOARD PERSISTENCE
# ============================================================

def load_leaderboard() -> list:
    """Reads all saved leaderboard entries from the local JSON file. Never raises."""
    try:
        if not os.path.exists(LEADERBOARD_FILE):
            return []
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def save_leaderboard_entry(name: str, specialization: str, score: float) -> bool:
    """Appends a completed session's result to the local JSON leaderboard file."""
    now = datetime.datetime.now()
    entry = {
        "name": name,
        "specialization": specialization,
        "score": score,
        "date": now.date().isoformat(),
        "time": now.strftime("%H:%M"),
    }
    try:
        data = load_leaderboard()
        data.append(entry)
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def get_today_leaderboard(top_n: int = LEADERBOARD_TOP_N) -> list:
    """Returns today's top N entries, highest score first."""
    today_str = datetime.date.today().isoformat()
    data = load_leaderboard()
    today_entries = [e for e in data if e.get("date") == today_str]
    today_entries.sort(key=lambda e: e.get("score", 0) or 0, reverse=True)
    return today_entries[:top_n]

# ============================================================
# STYLES
# ============================================================
st.markdown("""
<style>

/* ===== 1. HIDE STREAMLIT CLOUD HEADER & FOOTER ===== */
header[data-testid="stHeader"] {
    display: none !important;
}
footer {
    visibility: hidden !important;
}
#MainMenu {
    visibility: hidden !important;
}

.stApp{
background:linear-gradient(135deg,#071021,#0E1B2A,#162B47);
color:white;
}

h1,h2,h3,h4,p,label,span{
color:white!important;
}

.block-container{
padding-top:1.5rem !important;
padding-left:5%;
padding-right:5%;
}

@media (min-width: 768px) {
    .block-container{
        padding-top:2rem !important;
        padding-left:8%;
        padding-right:8%;
    }
}

.title{
font-size:42px;
font-weight:800;
text-align:center;
margin-bottom:8px;
letter-spacing:1px;
}

@media (min-width: 768px) {
    .title{ font-size:60px; margin-bottom:10px; }
}

.subtitle{
font-size:18px;
text-align:center;
color:#AFC8FF;
margin-bottom:28px;
}

@media (min-width: 768px) {
    .subtitle{ font-size:22px; margin-bottom:40px; }
}

.st-key-card_home, .st-key-card_interview, .st-key-card_feedback, .st-key-card_summary, .st-key-card_leaderboard{
background:#17263A!important;
padding:12px 16px!important;
border-radius:20px!important;
border:1px solid #27496D!important;
box-shadow:0 0 18px rgba(0,0,0,.35)!important;
}

.stTextInput input, .stTextArea textarea{
background:#22344D;
color:white;
border-radius:12px;
border:1px solid #2A4E73;
}

div.stButton>button{
background:linear-gradient(90deg,#2F81F7,#38BDF8);
border:none;
height:52px;
font-size:18px;
font-weight:bold;
border-radius:14px;
color:white;
transition:.25s;
width:100%;
}

div.stButton>button:hover{
transform:scale(1.01);
box-shadow:0 0 18px #38BDF8;
}

.feature{
background:#17263A;
padding:20px;
border-radius:18px;
text-align:center;
border:1px solid #2A4E73;
height:auto;
margin-bottom:15px;
}

.feature h3{ margin-top:10px; }

.footer{
text-align:center;
margin-top:40px;
padding-top:24px;
border-top:1px solid #27496D;
}

.footer-team{
font-size:14px;
font-weight:600;
color:white!important;
letter-spacing:.4px;
margin-bottom:8px;
}

.footer-divider{
display:inline-block;
color:#3A5A80!important;
margin:0 8px;
}

.footer-uni{
color:#9FB4D1!important;
font-size:13px;
margin-bottom:6px;
letter-spacing:.3px;
}

.footer-copy{
color:#5E7292!important;
font-size:12px;
}

/* Interview screen */
.q-badge{
display:inline-block;
background:#22344D;
color:#8FD3FF!important;
padding:6px 16px;
border-radius:20px;
font-size:14px;
font-weight:600;
margin-bottom:16px;
border:1px solid #2A4E73;
}

.q-text{
font-size:22px;
font-weight:600;
line-height:1.4;
margin-bottom:10px;
}

@media (min-width: 768px) {
    .q-text{ font-size:26px; line-height:1.5; }
}

.timer-hint{
color:#9FB4D1!important;
font-size:14px;
margin-bottom:20px;
}

/* Feedback screen */
.score-ring{
width:110px;
height:110px;
border-radius:50%;
background:conic-gradient(#38BDF8 var(--pct), #22344D 0);
display:flex;
align-items:center;
justify-content:center;
margin:0 auto 20px auto;
}

.score-ring-inner{
width:88px;
height:88px;
border-radius:50%;
background:#17263A;
display:flex;
align-items:center;
justify-content:center;
font-size:26px;
font-weight:800;
color:#38BDF8!important;
}

.score-label{
text-align:center;
font-size:18px;
font-weight:700;
color:#8FD3FF!important;
margin-bottom:20px;
}

.feedback-block{
background:#101c2c;
border-left:4px solid #2F81F7;
padding:14px 18px;
border-radius:10px;
margin-bottom:14px;
}

.feedback-block h4{
margin:0 0 6px 0;
font-size:15px;
color:#8FD3FF!important;
}

.progress-label{
text-align:center;
color:#AFC8FF!important;
margin-bottom:6px;
font-size:14px;
}

/* Recording status hint */
.rec-status{
display:flex;
align-items:center;
gap:10px;
padding:12px 18px;
border-radius:14px;
font-size:14px;
font-weight:600;
margin-bottom:14px;
border:1px solid transparent;
transition:.25s;
}

.rec-status.ready{
background:rgba(47,129,247,.12);
border-color:#2F81F7;
color:#8FD3FF!important;
}

.rec-status.done{
background:rgba(56,189,248,.12);
border-color:#22c55e;
color:#7CF5A6!important;
}

/* Leaderboard */
.lb-row{
display:flex;
align-items:center;
justify-content:space-between;
background:#17263A;
border:1px solid #2A4E73;
border-radius:16px;
margin-bottom:12px;
}

.lb-name{
font-weight:700;
}

.lb-sub{
color:#9FB4D1!important;
}

.lb-score{
font-weight:800;
color:#38BDF8!important;
}

/* ===== 2. MOBILE-RESPONSIVE CONNECTED SEGMENTED BAR ===== */
.numq-label{
text-align:center;
color:#AFC8FF!important;
font-weight:700;
font-size:15px;
margin-bottom:10px;
letter-spacing:.3px;
}

.st-key-numq_bar{
background:#0E1B2A!important;
border:1px solid #2A4E73!important;
border-radius:16px!important;
padding:4px!important;
box-shadow:none!important;
margin-bottom:12px!important;
}

/* Force horizontal flex layout on mobile screens */
.st-key-numq_bar div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 0 !important;
    width: 100% !important;
}

.st-key-numq_bar div[data-testid="column"] {
    flex: 1 1 0px !important;
    min-width: 0 !important;
    padding: 0 !important;
}

.st-key-numq_bar div[data-testid="column"] div.stButton>button {
    height: 48px !important;
    width: 100% !important;
    border-radius: 0 !important;
    border: 1px solid #22344D !important;
    border-left: none !important;
    background: transparent !important;
    color: #AFC8FF !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    box-shadow: none !important;
    transition: .2s !important;
    padding: 0 !important;
}

.st-key-numq_bar div[data-testid="column"]:first-child div.stButton>button {
    border-left: 1px solid #22344D !important;
    border-top-left-radius: 12px !important;
    border-bottom-left-radius: 12px !important;
}

.st-key-numq_bar div[data-testid="column"]:last-child div.stButton>button {
    border-top-right-radius: 12px !important;
    border-bottom-right-radius: 12px !important;
}

.st-key-numq_bar div[data-testid="column"] div.stButton>button:hover {
    transform: none !important;
    background: #16283f !important;
    box-shadow: none !important;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================
defaults = {
    "page": "home",
    "name": "",
    "specialization": SPECIALIZATIONS[0],
    "num_questions": DEFAULT_NUM_QUESTIONS,
    "q_index": 0,
    "current_question": "",
    "current_feedback": None,
    "current_answer": "",
    "history": [],
    "logged_index": -1,
    "audio_key_seed": 0,
    "leaderboard_saved": False,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def reset_session():
    """Resets a session for a brand-new interview, while preserving the
    operator's chosen question count and guaranteeing a fresh audio widget."""
    preserved_num_questions = st.session_state.get("num_questions", DEFAULT_NUM_QUESTIONS)
    next_audio_seed = st.session_state.get("audio_key_seed", 0) + 1
    for key, value in defaults.items():
        st.session_state[key] = value
    st.session_state.num_questions = preserved_num_questions
    st.session_state.audio_key_seed = next_audio_seed


def score_label(percentage):
    """Returns an evaluative word for a given percentage score."""
    if percentage is None:
        return ""
    if percentage >= 90:
        return "Excellent"
    if percentage >= 75:
        return "Very Good"
    if percentage >= 60:
        return "Good"
    if percentage >= 40:
        return "Fair"
    return "Needs Improvement"


def _bullet_block(title, items):
    """Renders a titled feedback card with a bulleted list, HTML-escaping each item."""
    if not items:
        return
    safe_items = "".join(f"<li>{html.escape(str(i))}</li>" for i in items)
    st.markdown(
        f"<div class='feedback-block'><h4>{title}</h4><ul>{safe_items}</ul></div>",
        unsafe_allow_html=True,
    )


def render_feedback(feedback: dict):
    """Renders Member 2's structured evaluation dict."""
    score = feedback.get("score", 0) or 0
    rating = feedback.get("rating") or score_label(score)
    welcome = feedback.get("welcome", "")
    model_answer = feedback.get("model_answer", "")

    deg = f"{score * 3.6}deg"
    st.markdown(
        f"""
        <div class='score-ring' style='--pct:{deg}'>
            <div class='score-ring-inner'>{score}%</div>
        </div>
        <div class='score-label'>{html.escape(str(rating))}</div>
        """,
        unsafe_allow_html=True,
    )

    if welcome:
        st.markdown(
            f"<div class='feedback-block'><h4>Welcome & Score</h4>{html.escape(welcome)}</div>",
            unsafe_allow_html=True,
        )

    _bullet_block("Strengths", feedback.get("strengths"))
    _bullet_block("Areas for Improvement", feedback.get("gaps"))
    _bullet_block("Tip for Growth", feedback.get("tips"))

    if model_answer:
        with st.expander("💡 View AI Sample Answer (optional)"):
            st.write(model_answer)


def render_leaderboard_content(kiosk: bool = False):
    """Renders today's top performers."""
    top_entries = get_today_leaderboard(LEADERBOARD_TOP_N)
    today_str = datetime.date.today().strftime("%A, %d %B %Y")

    title_size = "48px" if kiosk else "26px"
    st.markdown(
        f"<div style='text-align:center;font-size:{title_size};font-weight:800;margin-bottom:4px;'>"
        f"🏆 Today's Top Performers</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='text-align:center;color:#9FB4D1;margin-bottom:26px;font-size:{'18px' if kiosk else '14px'};'>"
        f"{today_str}</div>",
        unsafe_allow_html=True,
    )

    if not top_entries:
        st.markdown(
            "<div style='text-align:center;color:#9FB4D1;padding:40px;font-size:18px;'>"
            "No completed interviews yet today — be the first! 🚀</div>",
            unsafe_allow_html=True,
        )
        return

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    padding = "24px 32px" if kiosk else "14px 20px"
    medal_size = "36px" if kiosk else "22px"
    name_size = "28px" if kiosk else "17px"
    sub_size = "16px" if kiosk else "13px"
    score_size = "34px" if kiosk else "20px"

    for i, entry in enumerate(top_entries):
        medal = medals[i] if i < len(medals) else f"{i + 1}."
        name = html.escape(str(entry.get("name", "-")))
        spec = html.escape(str(entry.get("specialization", "-")))
        time_str = html.escape(str(entry.get("time", "")))
        score = entry.get("score", 0)
        st.markdown(
            f"""
            <div class='lb-row' style='padding:{padding};'>
                <div style='display:flex;align-items:center;gap:16px;'>
                    <span style='font-size:{medal_size};'>{medal}</span>
                    <div>
                        <div class='lb-name' style='font-size:{name_size};'>{name}</div>
                        <div class='lb-sub' style='font-size:{sub_size};'>{spec} • {time_str}</div>
                    </div>
                </div>
                <div class='lb-score' style='font-size:{score_size};'>{score}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_question_count_selector() -> int:
    """Renders the question count selection bar."""
    current = st.session_state.num_questions

    st.markdown("<div class='numq-label'>🎚️ Choose Interview Length</div>", unsafe_allow_html=True)

    with st.container(key="numq_bar"):
        cols = st.columns(len(NUM_QUESTIONS_OPTIONS))
        for col, n in zip(cols, NUM_QUESTIONS_OPTIONS):
            with col:
                if st.button(str(n), key=f"numq_btn_{n}", use_container_width=True):
                    st.session_state.num_questions = n
                    current = n

    st.markdown(
        f"""
        <style>
        .st-key-numq_btn_{current} button{{
            background:#0f2f45!important;
            border-color:#38BDF8!important;
            color:#8FD3FF!important;
            box-shadow:0 0 14px rgba(56,189,248,.55), inset 0 0 0 1px #38BDF8!important;
            position:relative!important;
            z-index:2!important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    return current


# ============================================================
# 🖥️ KIOSK DISPLAY MODE
# ============================================================
_kiosk_param = st.query_params.get("kiosk", "0")
if isinstance(_kiosk_param, list):
    _kiosk_param = _kiosk_param[0] if _kiosk_param else "0"
KIOSK_MODE = str(_kiosk_param).lower() in ("1", "true", "yes")

if KIOSK_MODE:
    st.markdown(
        f"<meta http-equiv='refresh' content='{KIOSK_REFRESH_SECONDS}'>",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='title' style='font-size:70px;'>🎤 MUHAAKA</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subtitle' style='font-size:26px;'>Live Leaderboard — AI Technical Interview Simulator</div>",
        unsafe_allow_html=True,
    )
    render_leaderboard_content(kiosk=True)
    st.markdown(
        f"<div style='text-align:center;color:#5E7292;margin-top:30px;font-size:14px;'>"
        f"Auto-refreshing every {KIOSK_REFRESH_SECONDS}s • Powered by Muhaaka</div>",
        unsafe_allow_html=True,
    )
    st.stop()

# ============================================================
# HEADER
# ============================================================
st.markdown("<div class='title'>🎤 MUHAAKA</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI Technical Interview Simulator</div>", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    with st.expander("⚙️ Admin / Booth Tools", expanded=False):
        st.caption(
            "💡 **Kiosk display**: open this app's URL with `?kiosk=1` "
            "appended on an external screen for a full-screen leaderboard."
        )

# ============================================================
# PAGE: HOME
# ============================================================
def page_home():
    left, center, right = st.columns([1, 2, 1])

    with center:
        with st.container(border=True, key="card_home"):
            name = st.text_input("👤 Full Name", value=st.session_state.name, placeholder="e.g. Sara Ahmed")
            specialization = st.selectbox(
                "💻 Select IT Specialization",
                SPECIALIZATIONS,
                index=SPECIALIZATIONS.index(st.session_state.specialization),
            )

            num_questions = render_question_count_selector()

            st.write("")

            if st.button("🚀 Start Interview", use_container_width=True):
                if not name.strip():
                    st.warning("Please enter your name before starting.")
                else:
                    st.session_state.name = name.strip()
                    st.session_state.specialization = specialization
                    st.session_state.num_questions = num_questions
                    st.session_state.q_index = 0
                    st.session_state.history = []
                    st.session_state.logged_index = -1
                    st.session_state.leaderboard_saved = False
                    st.session_state.audio_key_seed += 1
                    with st.spinner("Preparing your first question..."):
                        st.session_state.current_question = get_question(specialization)
                    st.session_state.page = "interview"
                    st.rerun()

            if st.button("🏆 View Today's Leaderboard", use_container_width=True):
                st.session_state.page = "leaderboard"
                st.rerun()

    st.write("")
    st.write("")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="feature">
        <h1>🤖</h1>
        <h3>AI Evaluation</h3>
        Receive instant feedback on every answer.
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="feature">
        <h1>🎙</h1>
        <h3>Speech Recognition</h3>
        Record your voice naturally.
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="feature">
        <h1>📈</h1>
        <h3>Performance Report</h3>
        Discover strengths and weaknesses.
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# PAGE: INTERVIEW
# ============================================================
def page_interview():
    left, center, right = st.columns([1, 6, 1])
    num_questions = st.session_state.num_questions

    with center:
        progress = st.session_state.q_index / num_questions
        st.markdown(
            f"<div class='progress-label'>Question {st.session_state.q_index + 1} of {num_questions}</div>",
            unsafe_allow_html=True,
        )
        st.progress(progress)

        with st.container(border=True, key="card_interview"):
            st.markdown(f"<span class='q-badge'>{st.session_state.specialization}</span>", unsafe_allow_html=True)
            st.markdown(f"<div class='q-text'>{html.escape(st.session_state.current_question)}</div>", unsafe_allow_html=True)
            st.markdown("<div class='timer-hint'>⏱ Aim to answer in about 45 seconds.</div>", unsafe_allow_html=True)

            st.markdown("**🎙 Record your answer**")

            audio_key = f"audio_{st.session_state.audio_key_seed}"
            audio_value = st.audio_input("Tap to record", label_visibility="collapsed", key=audio_key)

            if audio_value is None:
                st.markdown(
                    "<div class='rec-status ready'>🎙️ Microphone ready — tap the button above and "
                    "speak clearly, close to the mic.</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    "<div class='rec-status done'>✅ Recording captured — play it back to make sure "
                    "it's clear and audible before submitting.</div>",
                    unsafe_allow_html=True,
                )
                if st.button("🔄 Clear & Re-record", use_container_width=True, key="clear_record_btn"):
                    st.session_state.audio_key_seed += 1
                    st.rerun()

            with st.expander("⌨️ Prefer to type your answer instead?"):
                typed_answer = st.text_area("Your answer", label_visibility="collapsed", height=100)

            st.write("")

            if st.button("✅ Submit Answer", use_container_width=True):
                answer_text = ""
                if audio_value is not None:
                    with st.spinner("Transcribing your answer..."):
                        answer_text = transcribe_audio(audio_value)
                elif "typed_answer" in dir() and typed_answer.strip():
                    answer_text = typed_answer.strip()

                if not answer_text:
                    st.warning("Please record or type an answer before submitting.")
                else:
                    with st.spinner("Evaluating your answer..."):
                        feedback = get_feedback(
                            st.session_state.name,
                            st.session_state.current_question,
                            answer_text,
                        )
                    st.session_state.current_answer = answer_text
                    st.session_state.current_feedback = feedback
                    st.session_state.page = "feedback"
                    st.rerun()


# ============================================================
# PAGE: FEEDBACK
# ============================================================
def page_feedback():
    left, center, right = st.columns([1, 6, 1])
    num_questions = st.session_state.num_questions

    with center:
        with st.container(border=True, key="card_feedback"):
            feedback = st.session_state.current_feedback or {}
            render_feedback(feedback)

            if st.session_state.logged_index != st.session_state.q_index:
                st.session_state.history.append({
                    "question": st.session_state.current_question,
                    "answer": st.session_state.current_answer,
                    "feedback": feedback,
                    "score": feedback.get("score", 0) or 0,
                })
                st.session_state.logged_index = st.session_state.q_index

            st.write("")

            is_last = st.session_state.q_index + 1 >= num_questions
            button_label = "📊 View Final Report" if is_last else "➡️ Next Question"

            if st.button(button_label, use_container_width=True):
                if is_last:
                    st.session_state.page = "summary"
                else:
                    st.session_state.q_index += 1
                    st.session_state.audio_key_seed += 1
                    with st.spinner("Preparing your next question..."):
                        st.session_state.current_question = get_question(st.session_state.specialization)
                    st.session_state.page = "interview"
                st.rerun()


# ============================================================
# PAGE: SUMMARY / FINAL REPORT
# ============================================================
def page_summary():
    left, center, right = st.columns([1, 3, 1])

    with center:
        with st.container(border=True, key="card_summary"):
            st.markdown(f"### 🏁 Great job, {st.session_state.name}!")
            st.markdown("Here's a summary of your interview session.")

            scores = [h["score"] for h in st.session_state.history if h["score"] is not None]
            avg_pct = None
            if scores:
                avg_pct = round(sum(scores) / len(scores), 1)
                st.metric("Average Score", f"{avg_pct}%", score_label(avg_pct))

            if avg_pct is not None and not st.session_state.leaderboard_saved:
                save_leaderboard_entry(
                    st.session_state.name,
                    st.session_state.specialization,
                    avg_pct,
                )
                st.session_state.leaderboard_saved = True

            st.write("")

            for i, item in enumerate(st.session_state.history, start=1):
                with st.expander(f"Question {i}: {item['question'][:60]}..."):
                    st.markdown(f"**Your answer:** {item['answer']}")
                    st.markdown("**Feedback:**")
                    render_feedback(item["feedback"])

            st.write("")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("🏆 View Leaderboard", use_container_width=True):
                    st.session_state.page = "leaderboard"
                    st.rerun()
            with c2:
                if st.button("🔁 Start New Interview", use_container_width=True):
                    reset_session()
                    st.rerun()


# ============================================================
# PAGE: LEADERBOARD
# ============================================================
def page_leaderboard():
    left, center, right = st.columns([1, 3, 1])

    with center:
        with st.container(border=True, key="card_leaderboard"):
            render_leaderboard_content(kiosk=False)

            st.write("")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("🔄 Refresh Now", use_container_width=True):
                    st.rerun()
            with c2:
                if st.button("⬅️ Back to Home", use_container_width=True):
                    st.session_state.page = "home"
                    st.rerun()


# ============================================================
# ROUTER
# ============================================================
if st.session_state.page == "home":
    page_home()
elif st.session_state.page == "interview":
    page_interview()
elif st.session_state.page == "feedback":
    page_feedback()
elif st.session_state.page == "summary":
    page_summary()
elif st.session_state.page == "leaderboard":
    page_leaderboard()

# ============================================================
# FOOTER
# ============================================================
st.write("")
st.markdown("""
<div class='footer'>
    <div class='footer-team'>Noor Al Zakeebeh<span class='footer-divider'>|</span>Sara Shbeita<span class='footer-divider'>|</span>Tasneem Abu Thuher</div>
    <div class='footer-uni'>The Hashemite University</div>
    <div class='footer-copy'>Muhaaka — AI-powered mock interviews to help students practice with confidence</div>
</div>
""", unsafe_allow_html=True)
