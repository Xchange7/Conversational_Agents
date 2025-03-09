# app.py
import os
import sys
from dotenv import load_dotenv

from speech_to_text import transcribe_audio
from emotion_analyzer import EmotionAnalyzer
from mental_health_chain import create_mental_health_chain_with_prompt

from pymongo import MongoClient
from datetime import datetime
from text_to_speech import text_to_speech


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
        print("Please set OPENAI_API_KEY in environment variables or .env file")
        sys.exit(1)

    # get the MongoDB connection URI from the environment variables
    mongo_uri = os.getenv("MONGO_URI", "mongodb://admin:password@mongo:27017/")

    # connect to MongoDB
    # client = MongoClient(mongo_uri)
    client = MongoClient("mongodb://admin:password@localhost:27017/admin")
    db = client["conversational_agent"]
    collection = db["users"]

    # Emotion Analyzer and Conversation Chain
    analyzer = EmotionAnalyzer()
    chain = create_mental_health_chain_with_prompt(openai_api_key)

    # Face Recognition and Create New User 
    User = face_recognize(collection)

    print("Hello " + User.user_name + " How is everything going?")
    print("Please enter the audio file path (or enter text directly), enter 'exit' to exit.")

    while True:
        user_input = input(">>> ")
        if user_input.lower() == "exit":
            print("See you! Hope you enjoy!")
            break

        # Determine whether it is a text or an audio file path
        if user_input.endswith(".wav") or user_input.endswith(".mp3"):
            # transcribe audio to text
            try:
                text_content = transcribe_audio(user_input, model_name="base")
                print(f"[Transcription Result]: {text_content}")
            except Exception as e:
                print(f"Audio transcription failed: {e}")
                continue
        else:
            # Text
            text_content = user_input

        # Emotion Analysis
        emotion_label = analyzer.analyze_emotion(text_content)
        print(f"[emotion_label]: {emotion_label}")

        # Use Conversational Agent to Generate Response
        try:
            combined_input = f"emotion: {emotion_label}\n text: {text_content}"
            response = chain.invoke({"input": combined_input})

            print(f"AI response: {response['text']}") 

            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")  # format as "YYYY-MM-DD HH:MM:SS"
            one_conversation = Conversation(combined_input, response['text'], timestamp)
            # Update Conversation
            update_conversation(collection, User, one_conversation)

            text_to_speech( response['text'], "/Users/xchange/PycharmProjects/Conversational_Agents/conversation/output")
        except Exception as e:
            print(f"Failed to generate response: {e}")




def init_user(collection, new_user):
    # Construct a user document, where the conversations field is initialized to an empty list
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


    # Add face recognition judgment logic
    User_is_created = False
    if User_is_created:
        return User("Peng Xu",22,"Tortured by TU Delft") # User_id
    else:
        print("Nice to meet you! What is your name?")
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
