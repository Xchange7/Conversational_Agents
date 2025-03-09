# app.py
import os
import sys
from dotenv import load_dotenv

from speech_to_text import transcribe_audio
from emotion_analyzer import EmotionAnalyzer
from mental_health_chain import create_mental_health_chain_with_prompt

from pymongo import MongoClient
from datetime import datetime

class User:
    def __init__(self, user_name,user_age, user_problem):
        self.user_id = None
        self.user_name = user_name
        self.user_age = user_age
        self.user_problem = user_problem


class Conversation:
    def __init__(self, user_input, AI_output, timestamp):
        self.user_input = user_input
        self.AI_output = AI_output
        self.timestamp = timestamp


def main():
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("请先在环境变量或 .env 文件中配置 OPENAI_API_KEY")
        sys.exit(1)

    # 从环境变量获取 MongoDB 连接 URI
    mongo_uri = os.getenv("MONGO_URI", "mongodb://admin:password@mongo:27017/")

    # 连接 MongoDB
    # client = MongoClient(mongo_uri)
    client = MongoClient("mongodb://admin:password@localhost:27017/admin")

    db = client["conversational_agent"]
    collection = db["users"]

    # 创建情绪分析器 和 对话链
    analyzer = EmotionAnalyzer()
    chain = create_mental_health_chain_with_prompt(openai_api_key)

    # 人脸识别 和 创建新用户
    User = face_recognize(collection)

    print("Hello " + User.user_name + " How is everything going?")
    print("请输入音频文件路径(或直接输入文本)，输入 'exit' 退出。")

    while True:
        user_input = input(">>> ")
        if user_input.lower() == "exit":
            print("See you! Hope you enjoy!")
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
            # Text
            text_content = user_input

        # Emotion Analysis
        emotion_label = analyzer.analyze_emotion(text_content)
        print(f"[情绪分析]: {emotion_label}")

        # Use Conversational Agent to Generate Response
        try:
            combined_input = f"emotion: {emotion_label}\n text: {text_content}"
            response = chain.invoke({"input": combined_input})

            print(f"AI回复: {response['text']}")

            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")  # 格式化为 "YYYY-MM-DD HH:MM:SS"
            one_conversation = Conversation(combined_input, response['text'], timestamp)
            # Update Conversation
            update_conversation(collection, User, one_conversation)
        except Exception as e:
            print(f"生成回复失败: {e}")




def init_user(collection, new_user):
    # 构造用户文档，其中 conversations 字段初始化为空列表
    user = {
        "name": new_user.user_name,
        "age": new_user.user_age,
        "problem": new_user.user_problem,
        "conversations": []
    }
    try:
        insert_result = collection.insert_one(user)
        print("Your User ID is : " + str(insert_result.inserted_id))
        new_user.user_id = insert_result.inserted_id
        return True

    except Exception as e:
        print(e)
        return False

def face_recognize(collection):


    # 加入人脸识别判断逻辑
    User_is_created = False
    if User_is_created:
        return User("Peng Xu",22,"Tortured by TU Delft")# User_id
    else:
        print("Nice to meet you! What is your name？")
        user_name_input = input(">>> ")
        print("Nice to meet you! " + user_name_input)
        print("Now I have to gather some import information from you, what is your age?")
        user_age_input = input(">>> ")
        print("Could you please tell me your problem?")
        user_problem_input = input(">>> ")

        new_user = User(user_name_input, user_age_input, user_problem_input)

        init_user(collection, new_user)
        return new_user

def update_memory():
    #调用数据库存储

    return True

def update_conversation(collection, user, user_conversation):
    conversation = {"timestamp": user_conversation.timestamp,
                    "user_input": user_conversation.user_input,
                    "AI_output": user_conversation.AI_output}
    try:
        result = collection.update_one(
            {"_id": user.user_id},
            {"$push": {"conversations": conversation}},
        )
        if result.modified_count ==1:
            print("Result of User is Updated")

    except Exception as e:
        print(e)

    return True


if __name__ == "__main__":
    main()
