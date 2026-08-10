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
# Angular position (degrees, CSS rotate convention) of each number on the radial dial,
# spaced 72° apart starting at the top and going clockwise.
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
# ------------------------------------------------------------
# These wrap the real Groq-backed functions from audio_handler.py
# and llm_evaluator.py. Both modules can raise a custom error
# (TranscriptionError / EvaluationError) on API failure, so each
# wrapper catches that specifically and shows a friendly message
# instead of crashing the whole app mid-demo.
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


def get_question(specialization: str, difficulty: str) -> str:
    """Generates a real interview question at the selected difficulty."""
    try:
        return generate_interview_question(specialization, difficulty)
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
# 🏆 LEADERBOARD PERSISTENCE (lightweight local JSON, no auth)
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

/* ---------- Global dark glassmorphism ---------- */
.stApp{
    background:
        radial-gradient(circle at 88% 10%, rgba(0,126,255,.16), transparent 28%),
        radial-gradient(circle at 8% 78%, rgba(34,102,220,.12), transparent 30%),
        linear-gradient(135deg,#080E1E 0%,#0B172A 52%,#09152A 100%);
    color:#F5F8FF;
    min-height:100vh;
}

[data-testid="stAppViewContainer"] > .main{
    background:transparent;
}

h1,h2,h3,h4,h5,h6,p,label,span{
    color:#F5F8FF;
}

.block-container{
    max-width:1180px;
    padding-top:1.6rem!important;
    padding-left:2.2rem!important;
    padding-right:2.2rem!important;
    padding-bottom:1rem!important;
}

/* ---------- Header / logo ---------- */
.title{
    font-size:60px;
    font-weight:800;
    text-align:center;
    margin-bottom:10px;
    letter-spacing:1px;
    text-shadow:0 0 24px rgba(67,155,255,.25);
}

.subtitle{
    font-size:22px;
    text-align:center;
    color:#AFC8FF!important;
    margin-bottom:34px;
}

.home-brand{
    text-align:center;
    margin:2px 0 28px;
}

.home-mic{
    width:64px;
    height:64px;
    margin:0 auto 10px;
    border-radius:18px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:34px;
    background:linear-gradient(145deg,rgba(70,147,255,.22),rgba(23,71,130,.16));
    border:1px solid rgba(104,174,255,.30);
    box-shadow:0 0 26px rgba(30,133,255,.20), inset 0 0 18px rgba(255,255,255,.03);
}

.home-brand-title{
    font-size:52px;
    line-height:1;
    font-weight:850;
    letter-spacing:1px;
    text-shadow:0 0 28px rgba(60,153,255,.20);
}

.home-brand-subtitle{
    margin-top:10px;
    font-size:20px;
    color:#D5E1F7!important;
}

/* ---------- Main cards ---------- */
.st-key-card_home,
.st-key-card_interview,
.st-key-card_feedback,
.st-key-card_summary,
.st-key-card_leaderboard{
    background:rgba(18,30,52,.58)!important;
    padding:28px 30px!important;
    border-radius:26px!important;
    border:1px solid rgba(93,154,231,.24)!important;
    box-shadow:
        0 0 32px rgba(0,110,255,.10),
        inset 0 0 24px rgba(255,255,255,.018)!important;
    backdrop-filter:blur(18px);
    -webkit-backdrop-filter:blur(18px);
}

/* ---------- Inputs ---------- */
.stTextInput input,
.stTextArea textarea,
[data-baseweb="select"] > div{
    background:rgba(23,38,64,.72)!important;
    color:#F4F8FF!important;
    border-radius:13px!important;
    border:1px solid rgba(87,143,210,.28)!important;
    box-shadow:inset 0 0 14px rgba(255,255,255,.018);
}

.stTextInput input:focus,
.stTextArea textarea:focus,
[data-baseweb="select"] > div:focus-within{
    border-color:#3497FF!important;
    box-shadow:0 0 0 1px rgba(52,151,255,.35),0 0 18px rgba(52,151,255,.16)!important;
}

[data-baseweb="select"] *{
    color:#F4F8FF!important;
}

/* Keep the native Streamlit specialization dropdown visible and readable. */
[data-baseweb="popover"]{
    background:#101D32!important;
    border:1px solid #2A4E73!important;
    border-radius:12px!important;
    box-shadow:0 12px 35px rgba(0,0,0,.45),0 0 18px rgba(47,129,247,.12)!important;
}

[data-baseweb="popover"] [role="option"]{
    background:#101D32!important;
    color:#EAF2FF!important;
}

[data-baseweb="popover"] [role="option"] *{
    color:#EAF2FF!important;
}

[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [role="option"][aria-selected="true"]{
    background:rgba(47,129,247,.20)!important;
}

label[data-testid="stWidgetLabel"] p,
.stTextInput label,
.stSelectbox label{
    color:#DDE9FA!important;
    font-weight:650!important;
}

/* ---------- Buttons: default ---------- */
div.stButton>button{
    background:linear-gradient(90deg,#2F81F7,#38BDF8);
    border:1px solid rgba(127,196,255,.20);
    height:52px;
    font-size:17px;
    font-weight:750;
    border-radius:14px;
    color:white;
    transition:all .22s ease;
    width:100%;
    box-shadow:0 8px 20px rgba(18,109,221,.16);
}

div.stButton>button:hover{
    transform:translateY(-1px);
    box-shadow:0 0 24px rgba(56,189,248,.42);
    border-color:rgba(111,190,255,.48);
}

/* ---------- Difficulty selector ---------- */
.difficulty-heading{
    text-align:center;
    font-size:16px;
    font-weight:750;
    color:#EAF2FF!important;
    margin:24px 0 12px;
}

.st-key-difficulty_easy button,
.st-key-difficulty_medium button,
.st-key-difficulty_hard button{
    height:52px!important;
    border-radius:28px!important;
    background:rgba(255,255,255,.045)!important;
    border:1px solid rgba(101,146,202,.28)!important;
    color:#E8F0FF!important;
    box-shadow:inset 0 0 14px rgba(255,255,255,.018)!important;
    font-size:16px!important;
    font-weight:700!important;
}

.st-key-difficulty_easy button:hover,
.st-key-difficulty_medium button:hover,
.st-key-difficulty_hard button:hover{
    background:rgba(47,129,247,.10)!important;
    border-color:rgba(79,160,255,.55)!important;
    box-shadow:0 0 16px rgba(47,129,247,.18)!important;
}

/* ---------- Digital interview-length meter ---------- */
.numq-label{
    text-align:center;
    color:#EAF2FF!important;
    font-weight:750;
    font-size:16px;
    margin:25px 0 14px;
}

.question-meter-wrap{
    display:flex;
    align-items:center;
    justify-content:center;
    gap:18px;
    margin:0 auto 8px;
}

.question-meter{
    width:148px;
    height:148px;
    border-radius:50%;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    position:relative;
    background:radial-gradient(circle at 50% 48%,rgba(24,42,72,.96) 0 52%,rgba(11,23,42,.72) 53% 100%);
    border:7px solid rgba(55,142,246,.13);
    box-shadow:
        0 0 0 2px rgba(64,153,255,.10),
        0 0 18px rgba(47,129,247,.34),
        0 0 38px rgba(47,129,247,.13),
        inset 0 0 20px rgba(28,112,221,.18);
}

.question-meter::before{
    content:"";
    position:absolute;
    inset:-8px;
    border-radius:50%;
    border:2px solid transparent;
    border-top-color:#3C9BFF;
    border-right-color:rgba(60,155,255,.50);
    transform:rotate(-38deg);
    filter:drop-shadow(0 0 7px rgba(60,155,255,.75));
}

.question-number{
    font-size:42px;
    line-height:1;
    font-weight:850;
    color:#F6FAFF!important;
    text-shadow:0 0 16px rgba(74,168,255,.38);
}

.question-text{
    margin-top:6px;
    font-size:14px;
    color:#AFC8FF!important;
    font-weight:650;
}

.st-key-numq_prev_wrap button,
.st-key-numq_next_wrap button{
    width:44px!important;
    min-width:44px!important;
    height:44px!important;
    border-radius:50%!important;
    padding:0!important;
    font-size:22px!important;
    background:rgba(25,48,81,.65)!important;
    border:1px solid rgba(83,147,216,.30)!important;
    box-shadow:0 0 12px rgba(47,129,247,.10)!important;
}

.numq-hint{
    text-align:center;
    color:#6F86A9!important;
    font-size:12px;
    margin-top:8px;
}

/* ---------- Start button ---------- */
.st-key-start_interview_btn button{
    height:58px!important;
    border-radius:17px!important;
    font-size:18px!important;
    background:linear-gradient(90deg,#2385F5,#36B8FF)!important;
    border:1px solid rgba(131,205,255,.32)!important;
    box-shadow:
        0 0 18px rgba(38,141,255,.45),
        0 8px 25px rgba(16,99,211,.25)!important;
}

.st-key-start_interview_btn button:hover{
    transform:translateY(-2px)!important;
    box-shadow:
        0 0 28px rgba(57,174,255,.62),
        0 10px 30px rgba(16,99,211,.28)!important;
}

.st-key-secondary_home_btn button{
    background:rgba(255,255,255,.035)!important;
    border:1px solid rgba(92,140,198,.22)!important;
    color:#AFC8FF!important;
    box-shadow:none!important;
    height:46px!important;
    font-size:14px!important;
}

/* ---------- Feature cards ---------- */
.feature{
    background:rgba(18,30,52,.55);
    padding:22px 18px;
    border-radius:20px;
    text-align:left;
    border:1px solid rgba(92,148,218,.19);
    min-height:132px;
    box-shadow:0 0 20px rgba(0,110,255,.08), inset 0 0 18px rgba(255,255,255,.015);
    backdrop-filter:blur(14px);
}

.feature h1{
    margin:0 0 8px 0;
    font-size:27px;
}

.feature h3{
    margin:0 0 7px 0;
    font-size:17px;
}

.feature p,
.feature-text{
    color:#8EA5C8!important;
    font-size:13px;
    line-height:1.45;
}


.footer{
text-align:center;
margin-top:50px;
padding-top:28px;
border-top:1px solid #27496D;
}

.footer-team{
font-size:15px;
font-weight:600;
color:white!important;
letter-spacing:.4px;
margin-bottom:8px;
}

.footer-divider{
display:inline-block;
color:#3A5A80!important;
margin:0 10px;
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

/* ---------- Interview screen ---------- */
.q-badge{
    display:inline-block;
    background:rgba(47,129,247,.10);
    color:#8FD3FF!important;
    padding:6px 16px;
    border-radius:20px;
    font-size:14px;
    font-weight:650;
    margin-bottom:16px;
    border:1px solid rgba(47,129,247,.30);
}

.q-text{
    font-size:26px;
    font-weight:600;
    line-height:1.5;
    margin-bottom:10px;
}

.timer-hint{
    color:#9FB4D1!important;
    font-size:14px;
    margin-bottom:20px;
}

.rec-status{
    display:flex;
    align-items:center;
    gap:10px;
    padding:12px 18px;
    border-radius:14px;
    font-size:15px;
    font-weight:600;
    margin-bottom:14px;
    border:1px solid transparent;
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

.progress-label{
    text-align:center;
    color:#AFC8FF!important;
    margin-bottom:6px;
    font-size:14px;
}

/* ---------- Feedback screen ---------- */
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
    background:rgba(16,28,44,.72);
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

/* ---------- Leaderboard ---------- */
.lb-row{
    display:flex;
    align-items:center;
    justify-content:space-between;
    background:rgba(23,38,58,.72);
    border:1px solid rgba(42,78,115,.55);
    border-radius:16px;
    margin-bottom:12px;
}

.lb-name{font-weight:700;}
.lb-sub{color:#9FB4D1!important;}
.lb-score{font-weight:800;color:#38BDF8!important;}

/* ---------- Streamlit chrome ---------- */
#MainMenu{visibility:hidden!important;}
header[data-testid="stHeader"]{display:none!important;height:0!important;}
[data-testid="stToolbar"]{visibility:hidden!important;height:0!important;}
[data-testid="stDecoration"]{display:none!important;height:0!important;}
[data-testid="stStatusWidget"]{visibility:hidden!important;height:0!important;}
.stDeployButton{display:none!important;}

/* ---------- Responsive ---------- */
@media (max-width: 760px){
    .block-container{padding-left:1rem!important;padding-right:1rem!important;}
    .home-brand-title{font-size:40px;}
    .home-brand-subtitle{font-size:16px;}
    .st-key-card_home{padding:22px 18px!important;}
    .feature{min-height:120px;padding:18px 14px;}
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
    "difficulty": "Medium",
    "q_index": 0,
    "current_question": "",
    "current_feedback": None,  # dict from evaluate_interview_answer()
    "current_answer": "",
    "history": [],  # list of dicts: {question, answer, feedback}
    "logged_index": -1,  # guards against duplicate history entries on rerun
    "audio_key_seed": 0,  # bumped to force a fresh, empty audio_input widget
    "leaderboard_saved": False,  # guards against duplicate leaderboard entries on rerun
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def reset_session():
    """Resets a session for a brand-new interview, while preserving the
    operator's chosen question count and guaranteeing a fresh audio widget."""
    preserved_num_questions = st.session_state.get("num_questions", DEFAULT_NUM_QUESTIONS)
    preserved_difficulty = st.session_state.get("difficulty", "Medium")
    next_audio_seed = st.session_state.get("audio_key_seed", 0) + 1
    for key, value in defaults.items():
        st.session_state[key] = value
    st.session_state.num_questions = preserved_num_questions
    st.session_state.difficulty = preserved_difficulty
    st.session_state.audio_key_seed = next_audio_seed


def score_label(percentage):
    """Returns an evaluative word for a given percentage score (fallback if 'rating' is missing)."""
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
    """
    Renders Member 2's structured evaluation dict:
    {welcome, score (0-100), rating, strengths[], gaps[], tips[], model_answer}
    Used identically on both the feedback page and the final report.
    """
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
    """Renders today's top performers. Shared by the in-app leaderboard page and kiosk mode."""
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


def render_difficulty_selector() -> str:
    """Render Easy / Medium / Hard as three glassmorphic interactive buttons."""
    current = st.session_state.get("difficulty", "Medium")

    st.markdown("<div class='difficulty-heading'>🎚️ Select Question Difficulty</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    options = [(c1, "Easy", "🟢 Easy", "difficulty_easy"),
               (c2, "Medium", "🟡 Medium", "difficulty_medium"),
               (c3, "Hard", "🔴 Hard", "difficulty_hard")]

    for col, value, label, key in options:
        with col:
            with st.container(key=key):
                if st.button(label, key=f"{key}_button", use_container_width=True):
                    st.session_state.difficulty = value
                    current = value


    st.markdown(
        f"""
        <style>
        .st-key-difficulty_{current.lower()} button {{
            background:linear-gradient(180deg,rgba(44,139,255,.24),rgba(24,73,135,.25))!important;
            border:1px solid #3FA0FF!important;
            box-shadow:0 0 9px rgba(47,129,247,.55),0 0 24px rgba(47,129,247,.25),inset 0 0 14px rgba(86,174,255,.12)!important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    return current


def render_question_count_selector() -> int:
    """Render a compact neon digital counter instead of the previous radial dial."""
    current = int(st.session_state.get("num_questions", DEFAULT_NUM_QUESTIONS))

    st.markdown("<div class='numq-label'>🎚️ Choose Interview Length</div>", unsafe_allow_html=True)
    left, meter, right = st.columns([1, 2.2, 1])

    with left:
        with st.container(key="numq_prev_wrap"):
            if st.button("‹", key="numq_prev", help="Previous question count"):
                st.session_state.num_questions = max(NUM_QUESTIONS_OPTIONS[0], current - 1)
                current = st.session_state.num_questions

    with meter:
        st.markdown(
            f"""
            <div class='question-meter-wrap'>
                <div class='question-meter'>
                    <div class='question-number'>{current}</div>
                    <div class='question-text'>Question{"s" if current != 1 else ""}</div>
                </div>
            </div>
            <div class='numq-hint'>Use the arrows to change the number of questions</div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        with st.container(key="numq_next_wrap"):
            if st.button("›", key="numq_next", help="Next question count"):
                st.session_state.num_questions = min(NUM_QUESTIONS_OPTIONS[-1], current + 1)
                current = st.session_state.num_questions

    return current


# ============================================================
# 🖥️ KIOSK / FULL-SCREEN DISPLAY MODE
# ------------------------------------------------------------
# Visiting the app with ?kiosk=1 in the URL shows a booth-friendly,
# auto-refreshing, full-screen leaderboard — no interaction needed.
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
# HEADER (shown on secondary pages; home has its own hero card)
# ============================================================
if st.session_state.page != "home":
    st.markdown("<div class='title'>🎤 MUHAAKA</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>AI Technical Interview Simulator</div>", unsafe_allow_html=True)

# ============================================================
# SIDEBAR (admin-only helpers — kept out of the visitor-facing pages)
# ============================================================
with st.sidebar:
    with st.expander("⚙️ Admin / Booth Tools", expanded=False):
        st.caption(
            "💡 **Kiosk display**: open this app's URL with `?kiosk=1` "
            "appended (e.g. `your-app-url?kiosk=1`) on an external screen "
            f"for a full-screen leaderboard that auto-refreshes every "
            f"{KIOSK_REFRESH_SECONDS}s."
        )

# ============================================================
# PAGE: HOME
# ============================================================
def page_home():
    left, center, right = st.columns([1, 2.25, 1])

    with center:
        with st.container(border=True, key="card_home"):
            st.markdown(
                """
                <div class='home-brand'>
                    <div class='home-mic'>🎙</div>
                    <div class='home-brand-title'>MUHAAKA</div>
                    <div class='home-brand-subtitle'>AI Technical Interview Simulator</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            name = st.text_input(
                "👤 Full Name",
                value=st.session_state.name,
                placeholder="e.g. Sara Ahmed",
            )
            specialization = st.selectbox(
                "💻 Select IT Specialization",
                SPECIALIZATIONS,
                index=SPECIALIZATIONS.index(st.session_state.specialization),
            )

            difficulty = render_difficulty_selector()
            num_questions = render_question_count_selector()

            st.write("")
            with st.container(key="start_interview_btn"):
                start_clicked = st.button("🚀 Start Interview", use_container_width=True, key="start_interview_home")

            if start_clicked:
                if not name.strip():
                    st.warning("Please enter your name before starting.")
                else:
                    st.session_state.name = name.strip()
                    st.session_state.specialization = specialization
                    st.session_state.difficulty = difficulty
                    st.session_state.num_questions = num_questions
                    st.session_state.q_index = 0
                    st.session_state.history = []
                    st.session_state.logged_index = -1
                    st.session_state.leaderboard_saved = False
                    st.session_state.audio_key_seed += 1
                    with st.spinner("Preparing your first question..."):
                        st.session_state.current_question = get_question(specialization, difficulty)
                    st.session_state.page = "interview"
                    st.rerun()

            with st.container(key="secondary_home_btn"):
                leaderboard_clicked = st.button("🏆 View Today's Leaderboard", use_container_width=True, key="home_leaderboard")

            if leaderboard_clicked:
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
            <div class="feature-text">Receive instant feedback on every answer.</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="feature">
            <h1>🎙️</h1>
            <h3>Speech Recognition</h3>
            <div class="feature-text">Record your voice naturally.</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="feature">
            <h1>📈</h1>
            <h3>Performance Report</h3>
            <div class="feature-text">Discover strengths and weaknesses.</div>
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
            st.markdown(f"<span class='q-badge'>{html.escape(st.session_state.specialization)} • {html.escape(st.session_state.difficulty)}</span>", unsafe_allow_html=True)
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
                    st.session_state.audio_key_seed += 1  # fresh recorder for the next question
                    with st.spinner("Preparing your next question..."):
                        st.session_state.current_question = get_question(
                            st.session_state.specialization,
                            st.session_state.difficulty,
                        )
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

            # Save this session's result to the local leaderboard, once per session.
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
