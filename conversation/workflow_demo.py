import os
from dotenv import load_dotenv
import argparse
from conversation_workflow import get_mental_health_workflow
from text_to_speech import text_to_speech
import tempfile
import time
from datetime import datetime
from db import DB

def demo_workflow():
    """Demo of using the LangGraph workflow directly"""
    load_dotenv()
    
    # Initialize workflow
    workflow = get_mental_health_workflow()
    print("Workflow initialized successfully")
    
    # First, just get the username
    print("\n=== User Authentication ===")
    name = input("Enter your name: ")
    
    # Check if user exists
    db = DB()
    existing_user = db.get_user_by_name(name)
    
    # Initialize state based on whether user exists
    state = {}
    if existing_user:
        print(f"Welcome back, {name}!")
        state = workflow.invoke({
            "user_name": name
        })
    else:
        print(f"New user registration for {name}")
        age = int(input("Enter your age: "))
        problem = input("Enter your problem: ")
        state = workflow.invoke({
            "user_name": name,
            "user_age": age,
            "user_problem": problem
        })
    
    if "error" in state:
        print(f"Error: {state['error']}")
        return
    
    # Main conversation loop
    print("\n=== Starting Conversation ===")
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Exit condition
        if user_input.lower() in ["exit", "quit", "goodbye", "bye"]:
            print("Ending conversation...")
            break
        
        # Update the state with user input
        state = workflow.invoke({
            "input": user_input,
            "input_type": "text"
        }, state)
        
        # Display the response
        print(f"\nAgent: {state.get('response', 'ERROR: No response from agent')}")
        
        # Optional: Convert response to speech
        try:
            speech_output = text_to_speech(state.get('response', ''))
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            with open(temp_file.name, "wb") as f:
                f.write(speech_output)
            print(f"Response saved as audio: {temp_file.name}")
        except Exception as e:
            print(f"Could not convert response to speech: {e}")

def demo_workflow_with_audio():
    """Demo using audio input with the workflow"""
    # This would require additional code for audio recording
    # For a complete implementation, you'd need to:
    # 1. Record audio from the microphone
    # 2. Transcribe it with speech_to_text
    # 3. Pass both the transcription and audio path to the workflow
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demo for Mental Health Workflow")
    parser.add_argument("--audio", action="store_true", help="Use audio input mode")
    args = parser.parse_args()
    
    if args.audio:
        print("Audio mode not fully implemented in this demo")
        # demo_workflow_with_audio()
    else:
        demo_workflow() 