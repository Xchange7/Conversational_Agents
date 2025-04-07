import os
import sys
from dotenv import load_dotenv
import gradio as gr

from speech_to_text import transcribe_audio
from emotion_analyzer import EmotionAnalyzer
from text_to_speech import text_to_speech
from datetime import datetime
from pathlib import Path

# Import the database functions from db.py
from db import DB, User, Conversation
# Import the logger class from logger
from logger import Logger

# Import the LangGraph workflow
from conversation_workflow import get_mental_health_workflow


def create_user_interface(db_instance, analyzer, logger):
    current_user = None
    workflow = None
    
    # Function to check login status
    def is_logged_in():
        return current_user is not None

    def initialize_user(user_name):
        """Initialize user session by checking if user exists"""
        nonlocal current_user, workflow
        
        # Check if user exists
        existing_user = db_instance.get_user_by_name(user_name)
        if existing_user:
            current_user = existing_user
            # Initialize workflow with existing user
            workflow = get_mental_health_workflow(
                user_name=existing_user.user_name,
                user_age=existing_user.user_age, 
                user_problem=existing_user.user_problem,
                is_new_user=False,
                user_id=str(existing_user.user_id)
            )
            
            # Start conversation to get greeting
            initial_state = workflow.invoke({})
            greeting = initial_state.get('response', f"Welcome back, {user_name}!")
            
            return greeting, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
        else:
            # Show registration form for new users
            return f"New user registration for {user_name}", gr.update(visible=False), gr.update(visible=True), gr.update(visible=True)

    def register_new_user(user_name, user_age, user_problem):
        """Register a new user"""
        nonlocal current_user, workflow
        
        # Create new user
        new_user = User(user_name, user_age, user_problem)
        success = db_instance.init_user(new_user)
        
        if success:
            current_user = new_user
            # Initialize workflow with new user
            workflow = get_mental_health_workflow(
                user_name=user_name,
                user_age=user_age,
                user_problem=user_problem,
                is_new_user=True,
                user_id=str(new_user.user_id)
            )
            
            # Start conversation to get greeting
            initial_state = workflow.invoke({})
            greeting = initial_state.get('response', f"Welcome, {user_name}! How can I help you today?")
            
            return greeting, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
        else:
            return "Registration failed. Please try again.", gr.update(visible=False), gr.update(visible=True), gr.update(visible=True)

    def respond_to_text(message, history=None):
        logger.log("-------------------Start RESPONDING TO TEXT-------------------")
        nonlocal current_user, workflow
        if current_user is None or workflow is None:
            return "Please initialize user first.", None, ""

        logger.log(f"[Text Input]: {message}")

        # Analyze emotions
        analyzer = EmotionAnalyzer()
        text_emotion = analyzer.analyze_text_emotion(message)
        facial_emotion = analyzer.analyze_face_emotion()
        
        # Update the state with user input
        state = workflow.invoke({
            "input": message,
            "input_type": "text",
            "current_emotion": {
                "text_emotion": text_emotion,
                "facial_emotion": facial_emotion
            }
        })

        # Get the response from the state
        response_text = state.get('response', 'ERROR: No response from agent')
        logger.log(f"[AI Response to Text]: {response_text}")

        try:
            # Generate audio directly for Gradio UI
            audio_data = text_to_speech(response_text)
        except Exception as e:
            logger.log_error(f"Error during text-to-speech conversion: {e}")
            return f"Error: Text-to-speech failed: {e}", None, ""

        # Return response and empty value for text_input to clear it
        return response_text, audio_data, ""

    def respond_to_audio(audio_input, history=None):
        logger.log("-------------------Start RESPONDING TO AUDIO-------------------")
        nonlocal current_user, workflow
        if current_user is None or workflow is None:
            return "Please initialize user first.", None, None

        if not audio_input:
            return "No audio detected. Please record your message.", None, None

        try:
            # Transcribe audio to text
            transcribed_text = transcribe_audio(audio_input, model_name="base")
            logger.log(f"[Audio Transcription]: {transcribed_text}")
            
            # Analyze emotions
            analyzer = EmotionAnalyzer()
            text_emotion = analyzer.analyze_text_emotion(transcribed_text)
            speech_emotion = analyzer.analyze_speech_emotion(audio_input)
            facial_emotion = analyzer.analyze_face_emotion()
            
            # Update the state with transcribed text and emotions
            state = workflow.invoke({
                "input": transcribed_text,
                "input_type": "audio",
                "audio_path": audio_input,
                "current_emotion": {
                    "text_emotion": text_emotion,
                    "speech_emotion": speech_emotion,
                    "facial_emotion": facial_emotion
                }
            })

            # Get the response from the state
            response_text = state.get('response', 'ERROR: No response from agent')
            logger.log(f"[AI Response to Audio]: {response_text}")

            try:
                # Generate audio directly for Gradio UI
                audio_data = text_to_speech(response_text)
            except Exception as e:
                logger.log_error(f"Error during text-to-speech conversion: {e}")
                return f"Error: Text-to-speech failed: {e}", None, None

            # Return response and clear audio input
            return response_text, audio_data, None
        except Exception as e:
            logger.log_error(f"Failed to process audio: {e}")
            return f"Error processing audio: {e}", None, None

    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# Psychological Doctor Agent")
        
        with gr.Tabs(selected="user_info_tab") as tabs:
            with gr.Tab("User Info", id="user_info_tab"):
                # Initial login form
                with gr.Row():
                    user_name_input = gr.Textbox(label="Username")
                    login_button = gr.Button("Login/Register")
                
                # Registration form (initially hidden)
                with gr.Row(visible=False) as registration_form:
                    user_age_input = gr.Number(label="Age")
                    user_problem_input = gr.Textbox(label="What brings you here today?")
                    register_button = gr.Button("Complete Registration")
                
                # Status message
                status_message = gr.Textbox(label="Status", interactive=False)
            
            with gr.Tab("Chat", visible=False, id="chat_tab") as chat_tab:
                # Reorganize layout with video feed on the right
                with gr.Row():
                    # Left side - inputs
                    with gr.Column(scale=2):
                        # First row on the left - audio input
                        with gr.Row():
                            audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Speak to the agent", scale=4)
                            audio_submit = gr.Button("Submit Audio", scale=1)
                        
                        # Second row on the left - text input
                        with gr.Row():
                            text_input = gr.Textbox(label="Or enter text here", scale=4)
                            text_submit = gr.Button("Submit Text", scale=1)
                    
                    # Right side - video feed
                    with gr.Column(scale=1):
                        # Add video feed display
                        video_display = gr.HTML(
                            """
                            <div style="display: flex; justify-content: center;">
                                <img src="http://localhost:5005/video_feed" width="320" height="240" 
                                    style="border-radius: 10px; border: 2px solid #ccc;">
                            </div>
                            """, 
                            label="Camera Feed"
                        )
                
                # Output area stays the same
                state = gr.State([])
                output_text = gr.Textbox(label="Response")
                output_audio = gr.Audio(label="Agent's Speech", autoplay=True)

                # Connect text input to respond_to_text function
                text_submit.click(
                    respond_to_text, 
                    inputs=[text_input], 
                    outputs=[output_text, output_audio, text_input]
                )
                text_input.submit(
                    respond_to_text, 
                    inputs=[text_input], 
                    outputs=[output_text, output_audio, text_input]
                )
                
                # Connect audio input to respond_to_audio function
                audio_submit.click(
                    respond_to_audio, 
                    inputs=[audio_input], 
                    outputs=[output_text, output_audio, audio_input]
                )

        # Connect the components
        login_button.click(
            initialize_user,
            inputs=[user_name_input],
            outputs=[status_message, chat_tab, registration_form]
        )
        
        register_button.click(
            register_new_user,
            inputs=[user_name_input, user_age_input, user_problem_input],
            outputs=[status_message, chat_tab, registration_form]
        )

    return demo


def main():
    # Initialize logger
    logger = Logger()
    load_dotenv()
    use_docker_for_conversation = os.getenv("USE_DOCKER_FOR_CONVERSATION", "true")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.log_error("Please set OPENAI_API_KEY in environment variables or .env file")
        sys.exit(1)

    try:
        # Initialize database
        db_instance = DB()
        logger.log("Database initialized successfully")
    except Exception as e:
        logger.log_error(f"Database initialization failed: {e}")
        sys.exit(1)

    try:
        # Initialize emotion analyzer
        analyzer = EmotionAnalyzer()
        logger.log("Emotion Analyzer initialized successfully")
    except Exception as e:
        logger.log_error(f"Emotion Analyzer initialization failed: {e}")
        sys.exit(1)

    # Create and launch the interface
    interface = create_user_interface(db_instance, analyzer, logger)
    interface.launch(server_name="0.0.0.0")


if __name__ == "__main__":
    main()
