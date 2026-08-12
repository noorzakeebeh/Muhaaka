import os
import io
import streamlit as st
from dotenv import load_dotenv
from groq import Groq, APITimeoutError, APIError

load_dotenv()

PRIMARY_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
SECONDARY_KEY = st.secrets.get("GROQ_API_KEY_SECONDARY") or os.environ.get("GROQ_API_KEY_SECONDARY")

GROQ_API_KEY = PRIMARY_KEY or SECONDARY_KEY

client = Groq(api_key=GROQ_API_KEY, timeout=8.0, max_retries=1)


class TranscriptionError(Exception):
    """Raised when audio transcription fails."""
    pass


def transcribe_audio_bytes(audio_bytes, filename="audio.wav"):
    """
    Transcribes audio bytes directly received from Streamlit's audio recorder
    component into clean text using Groq's Whisper-large-v3 model.
    """
    if not audio_bytes or len(audio_bytes) == 0:
        return ""

    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename

        transcription = client.audio.transcriptions.create(
            file=(audio_file.name, audio_file.read()),
            model="whisper-large-v3",
            prompt=(
                "This is a candidate answering technical job interview "
                "questions in Arabic or English for Muhaaka. Please "
                "transcribe all spoken words verbatim without missing any "
                "initial or trailing phrases."
            ),
            response_format="json",
            temperature=0.0,
        )

        return transcription.text.strip()

    except (APITimeoutError, APIError) as e:
        global client
        if SECONDARY_KEY and client.api_key != SECONDARY_KEY:
            client = Groq(api_key=SECONDARY_KEY, timeout=8.0, max_retries=1)
            return transcribe_audio_bytes(audio_bytes, filename=filename)

        print(f"[Audio Processing Error]: {str(e)}")
        raise TranscriptionError(
            "Could not transcribe the audio right now. Please try again."
        ) from e

    except Exception as e:
        print(f"[Audio Processing Error]: {str(e)}")
        raise TranscriptionError(
            "Something went wrong while processing the audio."
        ) from e
