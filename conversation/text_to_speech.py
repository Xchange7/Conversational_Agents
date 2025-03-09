import os
from gtts import gTTS
from langdetect import detect
import platform

def text_to_speech(text, output_dir, slow=False):
    """
    将文本转换为语音，自动检测文本语言，并将生成的语音文件保存到指定目录下。
    文件会自动命名为 session_1.mp3, session_2.mp3, ...（避免重名）。

    参数:
        text (str): 待转换的文本内容。
        output_dir (str): 保存语音文件的目录路径。如果目录不存在，函数会自动创建。
        slow (bool): 是否以较慢的语速播放，默认为 False（正常语速）。

    返回:
        str: 成功保存后的完整文件路径。
    """
    # 如果输出目录不存在，则创建
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 自动检测文本语言
    try:
        language = detect(text)
    except Exception as e:
        print("语言检测失败，默认使用英文。错误信息:", e)
        language = "en"

    # 自动生成不重复的文件名：session_1.mp3, session_2.mp3, ...
    base_name = "session_"
    i = 1
    while True:
        file_name = f"{base_name}{i}.mp3"
        full_path = os.path.join(output_dir, file_name)
        if not os.path.exists(full_path):
            break
        i += 1

    # 创建 gTTS 对象并保存生成的语音
    tts = gTTS(text=text, lang=language, slow=slow)
    tts.save(full_path)
    print(f"语音文件已保存至: {full_path}")

    # **自动播放音频**
    system_name = platform.system()
    if system_name == "Windows":
        os.system(f'start {full_path}')  # Windows 默认播放器
    elif system_name == "Darwin":  # macOS
        os.system(f"afplay '{full_path}'")
    else:  # Linux
        os.system(f"mpg321 '{full_path}'")  # 需要安装 `mpg321`

    return full_path


# 示例用法
if __name__ == "__main__":
    sample_text = "你好，这是一个使用 gTTS 将文本转换为语音的示例。"
    # 指定保存音频文件的目录
    output_directory = "output"
    text_to_speech(sample_text, output_directory,True)
