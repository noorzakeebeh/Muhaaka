import streamlit as st
import html

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
QUESTIONS_PER_SESSION = 1

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
# STYLES
# ============================================================
st.markdown("""
<style>

.stApp{

background:linear-gradient(135deg,#071021,#0E1B2A,#162B47);
color:white;
}

h1,h2,h3,h4,p,label,span{
color:white!important;
}

.block-container{
padding-top:2rem;
padding-left:8%;
padding-right:8%;
}

.title{
font-size:60px;
font-weight:800;
text-align:center;
margin-bottom:10px;
letter-spacing:1px;
}

.subtitle{
font-size:22px;
text-align:center;
color:#AFC8FF;
margin-bottom:40px;
}

.st-key-card_home, .st-key-card_interview, .st-key-card_feedback, .st-key-card_summary{
background:#17263A!important;
padding:10px 15px!important;
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
height:56px;
font-size:19px;
font-weight:bold;
border-radius:14px;
color:white;
transition:.25s;
width:100%;
}

div.stButton>button:hover{
transform:scale(1.02);
box-shadow:0 0 20px #38BDF8;
}

.feature{
background:#17263A;
padding:25px;
border-radius:18px;
text-align:center;
border:1px solid #2A4E73;
height:170px;
}

.feature h3{ margin-top:10px; }

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

</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================
defaults = {
    "page": "home",
    "name": "",
    "specialization": SPECIALIZATIONS[0],
    "q_index": 0,
    "current_question": "",
    "current_feedback": None,  # dict from evaluate_interview_answer()
    "current_answer": "",
    "history": [],  # list of dicts: {question, answer, feedback}
    "logged_index": -1,  # guards against duplicate history entries on rerun
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def reset_session():
    for key, value in defaults.items():
        st.session_state[key] = value


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


# ============================================================
# HEADER (shown on every page)
# ============================================================
st.markdown("<div class='title'>🎤 MUHAAKA</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI Technical Interview Simulator</div>", unsafe_allow_html=True)

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

            st.write("")

            if st.button("🚀 Start Interview", use_container_width=True):
                if not name.strip():
                    st.warning("Please enter your name before starting.")
                else:
                    st.session_state.name = name.strip()
                    st.session_state.specialization = specialization
                    st.session_state.q_index = 0
                    st.session_state.history = []
                    st.session_state.logged_index = -1
                    with st.spinner("Preparing your first question..."):
                        st.session_state.current_question = get_question(specialization)
                    st.session_state.page = "interview"
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

    with center:
        progress = st.session_state.q_index / QUESTIONS_PER_SESSION
        st.markdown(
            f"<div class='progress-label'>Question {st.session_state.q_index + 1} of {QUESTIONS_PER_SESSION}</div>",
            unsafe_allow_html=True,
        )
        st.progress(progress)

        with st.container(border=True, key="card_interview"):
            st.markdown(f"<span class='q-badge'>{st.session_state.specialization}</span>", unsafe_allow_html=True)
            st.markdown(f"<div class='q-text'>{html.escape(st.session_state.current_question)}</div>", unsafe_allow_html=True)
            st.markdown("<div class='timer-hint'>⏱ Aim to answer in about 45 seconds.</div>", unsafe_allow_html=True)


            st.markdown("**🎙 Record your answer**")
            audio_value = st.audio_input("Tap to record", label_visibility="collapsed")

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

            is_last = st.session_state.q_index + 1 >= QUESTIONS_PER_SESSION
            button_label = "📊 View Final Report" if is_last else "➡️ Next Question"

            if st.button(button_label, use_container_width=True):
                if is_last:
                    st.session_state.page = "summary"
                else:
                    st.session_state.q_index += 1
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
            if scores:
                avg_pct = round(sum(scores) / len(scores), 1)
                st.metric("Average Score", f"{avg_pct}%", score_label(avg_pct))

            st.write("")

            for i, item in enumerate(st.session_state.history, start=1):
                with st.expander(f"Question {i}: {item['question'][:60]}..."):
                    st.markdown(f"**Your answer:** {item['answer']}")
                    st.markdown("**Feedback:**")
                    render_feedback(item["feedback"])

            st.write("")

            if st.button("🔁 Start New Interview", use_container_width=True):
                reset_session()
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
