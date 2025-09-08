import os
from gtts import gTTS
import logging
from pydub import AudioSegment

# Configure logging
logging.basicConfig(level=logging.INFO)

CACHE_DIR = "tts_cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
    logging.info(f"Created TTS cache directory at: {CACHE_DIR}")

def speak_text_gtts(text: str) -> str:
    """
    Converts text to speech using gTTS, saves it as an MP3, and returns the file path.
    A simple hashing mechanism is used for caching.

    Args:
        text (str): The text to be converted to speech.

    Returns:
        str: The file path of the generated audio file. Returns None on failure.
    """
    try:
        # Create a simple, filename-safe hash of the text for caching
        filename = f"{hash(text)}.mp3"
        filepath = os.path.join(CACHE_DIR, filename)

        # If the file already exists in the cache, return its path
        if os.path.exists(filepath):
            logging.info(f"TTS audio found in cache: {filepath}")
            return filepath
        
        # Generate the audio file using gTTS
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filepath)
        
        # Optional: Convert to a different format or bitrate if needed using pydub
        # For example, to ensure compatibility or reduce file size.
        # sound = AudioSegment.from_mp3(filepath)
        # sound.export(filepath, format="mp3", bitrate="128k")

        logging.info(f"TTS audio generated and saved to: {filepath}")
        return filepath
    except Exception as e:
        logging.error(f"gTTS failed to generate audio: {e}")
        return None

# --- Pluggable Architecture ---
# You can easily swap the TTS engine by changing this function call in app.py.
# For example, to use OpenAI's TTS or ElevenLabs, create a function like
# speak_text_openai(text) and call that instead.

# Example for OpenAI TTS (requires `openai` library):
# from openai import OpenAI
# client = OpenAI()
# def speak_text_openai(text: str) -> str:
#     filename = f"{hash(text)}.mp3"
#     filepath = os.path.join(CACHE_DIR, filename)
#     if os.path.exists(filepath):
#         return filepath
#     response = client.audio.speech.create(
#         model="tts-1",
#         voice="alloy",
#         input=text
#     )
#     response.stream_to_file(filepath)
#     return filepath

# Set the default TTS function to use
speak_text = speak_text_gtts
