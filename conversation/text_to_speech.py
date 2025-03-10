import os
import tempfile
from gtts import gTTS
from langdetect import detect
import platform
from io import BytesIO
from logger import Logger
import uuid

# Create logger instance
logger = Logger()

def text_to_speech(text, output_dir=None, slow=False):
    """
    Convert text to speech, automatically detect the text language, and return the audio file path for playback in Gradio UI.
    
    Parameters:
        text (str): The text content to be converted.
        output_dir (str, optional): Directory path to save the audio file (if provided).
        slow (bool): Whether to play at a slower speed, default is False (normal speed).

    Returns:
        str: The path of the generated audio file, which can be used directly with Gradio audio components.
    """
    # Automatically detect text language
    try:
        language = detect(text)
    except Exception as e:
        logger.log_error(f"Language detection failed, defaulting to English. Error: {e}")
        language = "en"

    # Create gTTS object
    tts = gTTS(text=text, lang=language, slow=slow)
    
    # Create a dedicated folder in the system's temp directory
    temp_dir = tempfile.gettempdir()
    audio_output_dir = os.path.join(temp_dir, "agent_audio_output")
    os.makedirs(audio_output_dir, exist_ok=True)
    
    # Create temporary file in the specified directory
    temp_file_path = os.path.join(audio_output_dir, f"{uuid.uuid4()}.mp3")
    
    # Save to temporary file
    tts.save(temp_file_path)
    
    logger.log(f"Audio file generated, saved at: {temp_file_path}")
    
    # Return file path, Gradio can use it directly
    return temp_file_path

# Example usage
if __name__ == "__main__":
    sample_text = "Hello, this is an example of converting text to speech using gTTS."
    audio_path = text_to_speech(sample_text)
    logger.log(f"Successfully generated audio file: {audio_path}")
