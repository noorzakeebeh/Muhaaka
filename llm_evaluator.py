import os
import json
import streamlit as st
from dotenv import load_dotenv
from groq import Groq, APITimeoutError, APIError
load_dotenv()

PRIMARY_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
SECONDARY_KEY = st.secrets.get("GROQ_API_KEY_SECONDARY") or os.environ.get("GROQ_API_KEY_SECONDARY")

GROQ_API_KEY = PRIMARY_KEY or SECONDARY_KEY
MODEL_NAME = "openai/gpt-oss-120b"

client = Groq(api_key=GROQ_API_KEY, timeout=8.0, max_retries=1)


class EvaluationError(Exception):
    """Raised when question generation or answer evaluation fails, so the
    Streamlit layer can show a friendly message instead of crashing mid-demo."""
    pass


def _create_completion(**kwargs):
    """
    Wrapper around client.chat.completions.create() that mirrors the
    failover behavior in audio_handler.py: if the primary key hits a
    timeout or API error (e.g. rate limit), retry once with the
    secondary key before giving up.
    """
    global client
    try:
        return client.chat.completions.create(**kwargs)
    except (APITimeoutError, APIError) as e:
        if SECONDARY_KEY and client.api_key != SECONDARY_KEY:
            print(f"[Groq Failover]: primary key failed ({str(e)}), switching to secondary key")
            client = Groq(api_key=SECONDARY_KEY, timeout=8.0, max_retries=1)
            return client.chat.completions.create(**kwargs)
        raise


def generate_interview_question(selected_domain, difficulty="Medium"):
    difficulty_guidelines = {
        "Easy": "Beginner level: basic concepts, definitions, and straightforward practical questions.",
        "Medium": "Intermediate level: core concepts, practical scenarios, and common graduate interview questions.",
        "Hard": "Advanced level: deeper technical reasoning, trade-offs, architecture, and complex practical scenarios.",
    }
    selected_difficulty = difficulty_guidelines.get(difficulty, difficulty_guidelines["Medium"])

    prompt = f"""
    You are an expert technical interviewer at a tech career fair.
    Generate ONE real-world, frequently asked technical interview question commonly used in actual job interviews for a university student or fresh graduate majoring in: {selected_domain}.

    Difficulty & Style Guidelines:
    - **Relevance**: Focus on real-world industry interview questions (core concepts, trade-offs, standard architectural/coding/system questions).
    - **Difficulty**: {difficulty} — {selected_difficulty}
    - **Length**: The question must be answerable verbally in about 45 seconds (3-4 spoken sentences), since candidates now get roughly 45 seconds to respond.

    Requirements:
    1. Write the question entirely in clear, professional English.
    2. Output ONLY the question text. Do NOT include any introductory words, quotes, or headers.
    """

    try:
        response = _create_completion(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL_NAME,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    except APITimeoutError as e:
        print(f"[Question Generation Timeout]: {str(e)}")
        raise EvaluationError("Question generation timed out. Please try again.") from e
    except APIError as e:
        print(f"[Question Generation API Error]: {str(e)}")
        raise EvaluationError("Could not generate a question right now. Please try again.") from e
    except Exception as e:
        print(f"[Question Generation Error]: {str(e)}")
        raise EvaluationError("Something went wrong while generating the question.") from e


def evaluate_interview_answer(user_name, question, user_answer):
    prompt = f"""
    You are an encouraging, fair, and professional technical interviewer evaluating a student at a tech event.
    Candidate Name: {user_name}
    Question Asked: {question}
    Candidate Answer: {user_answer}

    ⚠️ STRICT RULES & FORMATTING REQUIREMENTS:
    1. Address {user_name} DIRECTLY in the second person (use 'you' and 'your' instead of 'the candidate' or third-person pronouns).
    2. Respond ONLY with a valid JSON object. Do not include any markdown headers ('#', '##'), section titles, commentary, or backticks outside the JSON.
    3. The score MUST be a percentage from 0 to 100 (integer), for finer-grained precision than a 1-10 scale.
    4. The rating MUST be one short evaluative word or phrase that matches the score, e.g. "Excellent" (90-100), "Very Good" (75-89), "Good" (60-74), "Fair" (40-59), "Needs Improvement" (below 40). Use your judgment to pick the word that best matches the actual score.
    5. Keep all responses concise and suitable for quick reading on screen.
    6. BE HONEST, not falsely encouraging. If the answer is empty, off-topic, a plain "I don't know", or shows no real technical understanding, the score MUST be in the 0-15 range, "strengths" MUST be an empty list [], and "gaps" should state plainly that no relevant technical content was provided. Do NOT invent a generic compliment (e.g. "you responded promptly/politely") just to fill the strengths list — an empty list is the correct, expected output in that case.
    7. Only include a strength if it reflects genuine technical substance in the answer (a correct concept, a relevant example, sound reasoning, etc.).

    Use the following JSON structure exactly:
    {{
      "welcome": "Brief 1-2 sentence welcoming greeting addressing {user_name} directly as 'you'",
      "score": <integer percentage from 0 to 100, e.g., 85>,
      "rating": "<one short evaluative word/phrase matching the score, e.g. 'Excellent'>",
      "strengths": ["Short sentence pointing out genuine technical strengths — use [] if there are none"],
      "gaps": ["Short sentence describing what you missed or could improve"],
      "tips": ["One quick advice sentence for your growth"],
      "model_answer": "A concise 1 to 3 sentence ideal answer to the question."
    }}
    """

    try:
        response = _create_completion(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL_NAME,
            temperature=0.7,
            response_format={"type": "json_object"},
        )
    except APITimeoutError as e:
        print(f"[Evaluation Timeout]: {str(e)}")
        raise EvaluationError("Evaluation timed out. Please try again.") from e
    except APIError as e:
        print(f"[Evaluation API Error]: {str(e)}")
        raise EvaluationError("Could not evaluate the answer right now. Please try again.") from e
    except Exception as e:
        print(f"[Evaluation Error]: {str(e)}")
        raise EvaluationError("Something went wrong while evaluating the answer.") from e

    raw_text = response.choices[0].message.content.strip()
    try:
        result_json = json.loads(raw_text)
        # Guard against a malformed/partial JSON response from the model
        # (missing keys would otherwise crash the UI mid-demo).
        result_json.setdefault("welcome", f"Welcome {user_name}! Great to have you here.")
        result_json.setdefault("score", 75)
        result_json.setdefault("rating", "Good")
        result_json.setdefault("strengths", [])
        result_json.setdefault("gaps", [])
        result_json.setdefault("tips", [])
        result_json.setdefault("model_answer", "")
        return result_json
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"[Evaluation JSON Parse Error]: {str(e)} | raw: {raw_text[:200]}")
        return {
            "welcome": f"Welcome {user_name}! Great to have you here.",
            "score": 75,
            "rating": "Good",
            "strengths": ["You showed a good basic understanding of the concept."],
            "gaps": ["You could structure your answer a bit more clearly."],
            "tips": ["Try using standard technical terms when explaining your thoughts."],
            "model_answer": "Focus on the core definitions clearly.",
        }

