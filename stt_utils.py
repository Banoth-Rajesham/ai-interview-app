import os
from openai import OpenAI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize OpenAI client from environment variable
try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except Exception as e:
    logging.error(f"Failed to initialize OpenAI client for STT: {e}")
    client = None

def transcribe_audio(audio_filepath: str) -> str:
    """
    Transcribes audio from a given file path using the OpenAI Whisper API.

    Args:
        audio_filepath (str): The path to the audio file to be transcribed.

    Returns:
        str: The transcribed text. Returns an empty string on failure.
    """
    if not client:
        logging.error("OpenAI client not initialized. Transcription failed.")
        return ""
        
    if not os.path.exists(audio_filepath):
        logging.error(f"Audio file not found at: {audio_filepath}")
        return ""

    try:
        with open(audio_filepath, "rb") as audio_file:
            # Call the Whisper API for transcription
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        logging.info("Audio transcribed successfully.")
        return transcription.text
    except Exception as e:
        logging.error(f"An error occurred during audio transcription: {e}")
        return ""
