# speech_to_text.py
import whisper
import os
import shutil
import tempfile
from logger import Logger
from pathlib import Path
from test_whisper import test_whisper_transcription  # Import the encapsulated function

# Initialize logger
logger = Logger()

def transcribe_audio(audio_input, model_name="base") -> str:
    """
    Transcribe audio to text using OpenAI Whisper.
    
    :param audio_input: Audio input from Gradio's Audio component (gr.Audio with type="filepath")
    :param model_name: Whisper model name (tiny, base, small, medium, large, etc.)
    :return: Transcribed text
    """
    temp_file = None
    
    try:
        if not audio_input:
            logger.log_error("No audio input provided")
            raise ValueError("No audio input provided")
        
        # Convert to absolute path and normalize it
        if not os.path.isabs(audio_input):
            audio_input = os.path.abspath(audio_input)
        
        # Convert to Path object for more reliable path handling
        audio_path = Path(audio_input)
        logger.log(f"Original audio path: {audio_path}")
        
        # Ensure audio_input is a valid file path
        if not audio_path.exists():
            logger.log_error(f"Audio file not found at: {audio_path}")
            raise FileNotFoundError(f"Audio file not found at: {audio_path}")
        
        # Check if file is readable and has content
        if audio_path.stat().st_size == 0:
            logger.log_error(f"Audio file exists but is empty: {audio_path}")
            raise ValueError(f"Audio file exists but is empty: {audio_path}")
        
        # Create a temporary copy of the file with a .wav extension to ensure compatibility
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"whisper_audio_{os.getpid()}.wav")
        logger.log(f"Creating temporary audio file at: {temp_file}")
        
        # Copy the file to ensure we have a stable file that won't be deleted
        shutil.copy2(audio_path, temp_file)
        
        if not os.path.exists(temp_file):
            logger.log_error(f"Failed to create temporary file at: {temp_file}")
            raise IOError(f"Failed to create temporary file at: {temp_file}")
            
        logger.log(f"Temporary file created successfully, size: {os.path.getsize(temp_file)} bytes")
        
        # Call the test_whisper_transcription function instead of using whisper directly
        logger.log(f"Calling test_whisper_transcription function")
        result = test_whisper_transcription(temp_file)
        
        if result["success"]:
            transcribed_text = result["result"]["text"]
            logger.log(f"Successfully transcribed audio: {transcribed_text[:50]}...")
            return transcribed_text
        else:
            error_msg = f"Test whisper transcription failed: {result['error']}"
            logger.log_error(error_msg)
            raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"Error during transcription: {e}"
        logger.log_error(error_msg)
        raise RuntimeError(f"Failed to transcribe audio: {str(e)}")
    finally:
        # Clean up the temporary file
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                logger.log(f"Temporary file removed: {temp_file}")
            except Exception as e:
                logger.log_warning(f"Failed to remove temporary file: {e}")
