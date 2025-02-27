# app.py
import os
import sys
from dotenv import load_dotenv

from speech_to_text import transcribe_audio
from emotion_analyzer import EmotionAnalyzer
from mental_health_chain import create_mental_health_chain_with_prompt


def main():
    load_dotenv()  # 如果你在 .env 文件中存储了OPENAI_API_KEY
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("请先在环境变量或 .env 文件中配置 OPENAI_API_KEY")
        sys.exit(1)

    # 创建情绪分析器
    analyzer = EmotionAnalyzer()

    # 创建对话链（心理健康Agent）
    chain = create_mental_health_chain_with_prompt(openai_api_key)

    print("=== 心理健康对话Agent ===")
    print("请输入音频文件路径(或直接输入文本)，输入 'exit' 退出。")

    while True:
        user_input = input(">>> ")
        if user_input.lower() == "exit":
            print("再见！祝你一切顺利。")
            break

        # 判断是文本还是音频文件路径
        if user_input.endswith(".wav") or user_input.endswith(".mp3"):
            # 做语音转文本
            try:
                text_content = transcribe_audio(user_input, model_name="base")
                print(f"[语音识别结果]: {text_content}")
            except Exception as e:
                print(f"音频转写失败: {e}")
                continue
        else:
            # 用户直接输入文本
            text_content = user_input

        # 情绪分析
        emotion_label = analyzer.analyze_emotion(text_content)
        print(f"[情绪分析]: {emotion_label}")

        # 使用对话Agent生成回复
        try:

            combined_input = f"emotion: {emotion_label}\n text: {text_content}"
            response = chain.invoke({"input": combined_input})

            print(f"AI回复: {response['text']}")

            print({"History: " + response['history']})
        except Exception as e:
            print(f"生成回复失败: {e}")


if __name__ == "__main__":
    main()
