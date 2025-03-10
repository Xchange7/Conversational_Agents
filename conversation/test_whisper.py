import whisper
import os
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
        model = whisper.load_model("base")
        logger.log("Transcribing audio...")
        result = model.transcribe(audio_path)
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
