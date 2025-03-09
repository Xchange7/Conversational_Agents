# app.py
import os
import sys
from dotenv import load_dotenv

from speech_to_text import transcribe_audio
from emotion_analyzer import EmotionAnalyzer
from mental_health_chain import create_mental_health_chain_with_prompt
from text_to_speech import text_to_speech
from datetime import datetime
from pathlib import Path

# Import the database functions from db.py
from db import DB, User, Conversation


def main():
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Please set OPENAI_API_KEY in environment variables or .env file")
        sys.exit(1)

    # connect to MongoDB
    db_instance = DB()

    # Emotion Analyzer and Conversation Chain
    analyzer = EmotionAnalyzer()
    chain = create_mental_health_chain_with_prompt(openai_api_key)

    # Face Recognition and Create New User 
    User = face_recognize(db_instance)

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
            db_instance.update_conversation(User, one_conversation)

            # get current path with Pathlib
            current_path = Path(__file__).parent

            # text_to_speech( response['text'], "/Users/xchange/PycharmProjects/Conversational_Agents/conversation/output")
            # use current_path instead of hardcoding the path
            text_to_speech(response['text'], current_path / "output")
            
        except Exception as e:
            print(f"Failed to generate response: {e}")




def face_recognize(db_instance):


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

        db_instance.init_user(new_user)
        return new_user

def update_memory():

    return True


if __name__ == "__main__":
    main()
