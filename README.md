# 🎤 Muhaaka (مُحاكاة) — AI Technical Interview Simulator

**Muhaaka** is an AI-powered mock interview web app that lets university students and fresh graduates practice real technical interview questions out loud (or in writing), and get instant, structured AI feedback on their answers.

Built as part of the **AIdea Team** to be showcased at an event hosted by **Al-Hussein Technical University (HTU)**.

---

## 👩‍💻 Team — (Hashemite University)

| Name | Major | Role |
|---|---|---|
| Noor Al Zakeebeh | Computer Information Systems (CIS) | Data Architecture & System Integration (Environment Config, Data Flow & System Testing) |
| Sara Shbeita | Artificial Intelligence (AI) | AI Logic & Audio Processing (Audio Handler, LLM Integration & Evaluation Logic) |
| Tasneem Abu Thuher | Software Engineering (SWE) | Frontend & System Architecture (Streamlit UI/UX Layout, App Flow & User Experience) |

All three members collaborated on integrating the final application.

---

## ✨ Features

- 🎯 **Specialization selection** — 15 IT-related tracks (CS, SWE, AI, Data Science, Cyber Security, etc.)
- ❓ **Live question generation** — a real, industry-style interview question is generated on the fly via an LLM (Groq)
- 🎙️ **Voice answers** — record your answer directly in the browser; it's transcribed automatically with Whisper
- ⌨️ **Typed answers** — optional fallback for anyone who prefers typing
- 📊 **AI evaluation** — every answer gets a 0–100 score, a rating label, strengths, gaps, a growth tip, and a model answer
- 🏁 **Final report** — a session summary with the average score and a full recap of every question/answer/feedback

---

## 🧱 Tech Stack

- **Frontend / App:** [Streamlit](https://streamlit.io/)
- **LLM (question generation + evaluation):** Groq API — `openai/gpt-oss-120b`
- **Speech-to-text:** Groq API — `whisper-large-v3`
- **Config:** `python-dotenv`

---

## 📁 Project Structure

```
.
├── app.py              # Streamlit UI, routing (home → interview → feedback → summary), styling
├── audio_handler.py    # Wraps Groq Whisper API for voice → text transcription
├── llm_evaluator.py    # Wraps Groq LLM for question generation + answer evaluation (JSON output)
├── requirements.txt     # Python dependencies
├── .env.example         # Template for the required environment variable
└── .gitignore           # Keeps secrets and junk files out of git
```

---

## ⚙️ Setup & Installation

**1. Clone the repository**
```bash
git clone <https://github.com/sarashbeita06/Muhaak>
cd <repo-folder>Muhaaka
```

**2. Create a virtual environment (recommended)**
```bash
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up your API key**
```bash
cp .env.example .env
```
Then open `.env` and paste your real Groq API key:
```
GROQ_API_KEY=your_real_key_here
```
> Get a free key from [console.groq.com](https://console.groq.com/). Never commit your real `.env` file — it's already excluded via `.gitignore`.

**5. Run the app**
```bash
streamlit run app.py
```
The app will open automatically in your browser (usually `http://localhost:8501`).

---

## 🕹️ How It Works

1. **Home** — candidate enters their name and picks a specialization
2. **Interview** — an AI-generated question is shown; the candidate records (or types) an answer
3. **Feedback** — the answer is transcribed (if audio) and evaluated instantly: score, rating, strengths, gaps, a tip, and a model answer
4. **Summary** — after the session, a final report shows the average score and a recap of every Q&A

---

## 📝 Notes

- `llama-3.3-70b-versatile` is deprecated on Groq (scheduled shutdown Aug 16, 2026), so the project uses `openai/gpt-oss-120b` instead, per Groq's recommended migration path.
- Requests use an 8s timeout and a single retry to stay within a tight 3–5s latency budget suitable for a live event/demo.

---

<p align="center">Made with 💙 by <b>AIdea Team</b> — The Hashemite University<br>Presented at an Al-Hussein Technical University (HTU) event</p>
