import whisper
import os
import shutil
from logger import Logger

# Initialize logger
logger = Logger()

def test_whisper_transcription(audio_path):
    """
    Test Whisper transcription on a specific audio file
    
    :param audio_path: Path to the audio file
    :return: Dictionary containing transcription result
    """
    file_exists = os.path.exists(audio_path)
    file_is_valid = os.path.isfile(audio_path)
    
    logger.log(f"Testing whisper transcription on: {audio_path}")
    logger.log(f"File exists: {file_exists}, is valid file: {file_is_valid}")
    
    if not file_exists or not file_is_valid:
        logger.log_error(f"Invalid audio file: exists={file_exists}, is_file={file_is_valid}")
        return {
            "success": False, 
            "error": f"Invalid audio file: exists={file_exists}, is_file={file_is_valid}"
        }
    
    try:
        logger.log("Loading whisper model (base)...")
        # Try to load the model, handling potential checksum errors
        try:
            model = whisper.load_model("base")
        except Exception as model_error:
            if "SHA256 checksum does not match" in str(model_error):
                # Delete the corrupted model files
                logger.log("Checksum error detected. Attempting to delete corrupted model files...")
                model_dir = os.path.expanduser("~/.cache/whisper")
                if os.path.exists(model_dir):
                    try:
                        shutil.rmtree(model_dir)
                        logger.log("Deleted corrupted model directory. Retrying download...")
                    except Exception as delete_error:
                        logger.log_error(f"Failed to delete model directory: {delete_error}")
                
                # Retry loading the model
                model = whisper.load_model("base")
            else:
                raise
        
        # Set explicit FFmpeg parameters
        logger.log("Transcribing audio...")
        result = model.transcribe(
            audio_path,
            fp16=False,  # Use float32 for better compatibility
            verbose=True  # Show detailed logs during transcription
        )
        
        logger.log(f"Transcription successful")
        return {"success": True, "result": result}
    except Exception as e:
        logger.log_error(f"Transcription failed: {str(e)}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    audio_path = r"<path_to_audio_file>"
    
    logger.log("Starting whisper test")
    result = test_whisper_transcription(audio_path)
    if result["success"]:
        logger.log(f"Result: {result['result']['text'][:100]}...")
    else:
        logger.log_error(f"Error: {result['error']}")
