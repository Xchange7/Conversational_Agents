# speech_to_text.py
import whisper

def transcribe_audio(audio_file_path: str, model_name="base") -> str:
    """
    使用 OpenAI Whisper 将音频文件转换为文本。
    :param audio_file_path: 音频文件路径
    :param model_name: Whisper 模型名称（tiny, base, small, medium, large等）
    :return: 转写后的文本
    """
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_file_path)
    return result["text"]
