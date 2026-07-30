import os
import io
from dotenv import load_dotenv
from groq import Groq, APITimeoutError, APIError

# Load variables from a local .env file (never commit .env - see .gitignore)
load_dotenv()

# No hardcoded fallback key. The app fails loudly if the env var is missing,
# instead of silently using a leaked/burned key.
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

# Timeout keeps a single request from blowing past the 3-5s latency budget
# if the Groq API stalls. max_retries=1 avoids doubling that wait on failure.
client = Groq(api_key=GROQ_API_KEY, timeout=8.0, max_retries=1)


class TranscriptionError(Exception):
    """Raised when audio transcription fails, so callers can distinguish
    a real error from a normal (possibly empty) transcript string."""
    pass


def transcribe_audio_bytes(audio_bytes, filename="audio.wav"):
    """
    Transcribes audio bytes directly received from Streamlit's audio recorder
    component into clean text using Groq's Whisper-large-v3 model.

    Returns:
        str: the transcribed text (may be an empty string if no audio given).

    Raises:
        TranscriptionError: if the Groq API call fails or times out. Callers
        (the Streamlit UI layer) should catch this and show a friendly
        message instead of letting the app crash mid-demo.
    """
    # 1. Validation check: If no audio bytes provided
    if not audio_bytes or len(audio_bytes) == 0:
        return ""

    try:
        # 2. Convert raw audio bytes to an in-memory file object
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename

        # 3. Transcribe via Groq Whisper API
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

        # 4. Return clean text output
        return transcription.text.strip()

    except APITimeoutError as e:
        print(f"[Audio Processing Timeout]: {str(e)}")
        raise TranscriptionError(
            "Transcription timed out. Please try recording again."
        ) from e

    except APIError as e:
        print(f"[Audio Processing API Error]: {str(e)}")
        raise TranscriptionError(
            "Could not transcribe the audio right now. Please try again."
        ) from e

    except Exception as e:
        print(f"[Audio Processing Error]: {str(e)}")
        raise TranscriptionError(
            "Something went wrong while processing the audio."
        ) from e
