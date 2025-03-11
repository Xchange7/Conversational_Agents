import os
import sys
from dotenv import load_dotenv
import gradio as gr

from speech_to_text import transcribe_audio
from emotion_analyzer import EmotionAnalyzer
from mental_health_chain import create_mental_health_chain_with_prompt
from text_to_speech import text_to_speech
from datetime import datetime
from pathlib import Path

# Import the database functions from db.py
from db import DB, User, Conversation
# Import the logger class from logger
from logger import Logger


def create_user_interface(db_instance, analyzer, chain, logger):
    current_user = None
    
    # Function to check login status
    def is_logged_in():
        return current_user is not None

    def respond_to_text(message, history=None):
        logger.log("-------------------Start RESPONDING TO TEXT-------------------")
        nonlocal current_user
        if current_user is None:
            return "Please initialize user first.", None, ""

        logger.log(f"[Text Input]: {message}")

        text_emotion_label = analyzer.analyze_text_emotion(message)
        facial_emotion_label = analyzer.analyze_face_emotion()
        
        logger.log(f"[Text Emotion]: {text_emotion_label}")
        logger.log(f"[Facial Emotion]: {facial_emotion_label}")

        # Use Conversational Agent to Generate Response
        try:
            combined_input = f"text emotion: {text_emotion_label}\nfacial emotion:{facial_emotion_label}\ntext: {message}"
            logger.log(f"[Combined Input]: {combined_input}")
            response = chain.invoke({"input": combined_input})

            logger.log(f"[AI Response to Text]: {response['text']}")

            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            one_conversation = Conversation(combined_input, response['text'], timestamp)
            # Update Conversation
            db_instance.update_conversation(current_user, one_conversation)

            try:
                # Generate audio directly for Gradio UI
                audio_data = text_to_speech(response['text'])
            except Exception as e:
                logger.log_error(f"Error during text-to-speech conversion: {e}")
                return f"Error: Text-to-speech failed: {e}", None, ""

            # Return response and empty value for text_input to clear it
            return response['text'], audio_data, ""
        except Exception as e:
            logger.log_error(f"Failed to generate response to text: {e}")
            return f"Error: {e}", None, ""

    def respond_to_audio(audio_input, history=None):
        logger.log("-------------------Start RESPONDING TO AUDIO-------------------")
        nonlocal current_user
        if current_user is None:
            return "Please initialize user first.", None, None

        if not audio_input:
            return "No audio detected. Please record your message.", None, None

        try:
            # Transcribe audio to text
            transcribed_text = transcribe_audio(audio_input, model_name="base")
            logger.log(f"[Audio Transcription]: {transcribed_text}")
            
            # Emotion Analysis for audio and transcribed text
            text_emotion_label = analyzer.analyze_text_emotion(transcribed_text)
            # Speech Emotion Analysis
            speech_emotion_label = analyzer.analyze_speech_emotion(audio_input)
            # Facial Emotion Analysis
            facial_emotion_label = analyzer.analyze_face_emotion()
            
            logger.log(f"[Text Emotion]: {text_emotion_label}")
            logger.log(f"[Speech Emotion]: {speech_emotion_label}")
            logger.log(f"[Facial Emotion]: {facial_emotion_label}")

            # Use Conversational Agent to Generate Response
            combined_input = f"text emotion: {text_emotion_label}\nfacial emotion:{facial_emotion_label}\nspeech emotion: {speech_emotion_label}\n text: {transcribed_text}"
            response = chain.invoke({"input": combined_input})

            logger.log(f"[AI Response to Audio]: {response['text']}")

            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            one_conversation = Conversation(combined_input, response['text'], timestamp)
            # Update Conversation
            db_instance.update_conversation(current_user, one_conversation)

            try:
                # Generate audio directly for Gradio UI
                audio_data = text_to_speech(response['text'])
            except Exception as e:
                logger.log_error(f"Error during text-to-speech conversion: {e}")
                return f"Error: Text-to-speech failed: {e}", None, None

            # Return response and clear audio input
            return response['text'], audio_data, None
        except Exception as e:
            logger.log_error(f"Failed to process audio: {e}")
            return f"Error processing audio: {e}", None, None

    def create_new_user(user_name_input, user_age_input, user_problem_input):
        nonlocal current_user
        # Check if the user already exists
        existing_user = db_instance.get_user_by_name(user_name_input)
        if existing_user:
            return f"User {user_name_input} already exists! Please log in instead.", gr.update(visible=False), gr.update(visible=True)

        new_user = User(user_name_input, user_age_input, user_problem_input)
        db_instance.init_user(new_user)
        if new_user.user_id:
            current_user = new_user
            return f"User {user_name_input} created successfully!", gr.update(visible=True), gr.update(visible=False)
        else:
            return f"Failed to create user {user_name_input}.", gr.update(visible=False), gr.update(visible=True)

    def login_user(user_name_input):
        nonlocal current_user
        # Check if the user exists
        existing_user = db_instance.get_user_by_name(user_name_input)
        if not existing_user:
            return "User not found. Please create a new user or check the username.", gr.update(visible=False), gr.update(visible=True)

        current_user = existing_user
        return f"User {user_name_input} logged in successfully!", gr.update(visible=True), gr.update(visible=False)
    
    def logout_user():
        nonlocal current_user
        current_user = None
        return "You have been logged out.", gr.update(visible=False), gr.update(visible=True), "", "", 0, ""

    def get_user_info():
        if current_user:
            return current_user.user_name, current_user.user_age, current_user.user_problem
        return "", 0, ""

    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# Psychological Doctor Agent")
        
        # Create tabs but hide Chat initially and select User Info by default
        with gr.Tabs(selected="user_info_tab") as tabs:
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

            with gr.Tab("User Info", id="user_info_tab") as user_info_tab:
                # Login/Register UI (visible when not logged in)
                with gr.Group(visible=True) as login_group:
                    with gr.Row():
                        user_mode = gr.Radio(["Login", "Create User"], label="Select Mode", value="Login")
                    name_input = gr.Textbox(label="Name")
                    age_input = gr.Number(label="Age", visible=False)
                    problem_input = gr.Textbox(label="Problem", visible=False)
                    submit_button = gr.Button("Submit")
                    user_output = gr.Textbox(label="User Status")

                # User Profile UI (visible when logged in)
                with gr.Group(visible=False) as profile_group:
                    gr.Markdown("## Your Profile")
                    display_name = gr.Textbox(label="Name", interactive=False)
                    display_age = gr.Number(label="Age", interactive=False)
                    display_problem = gr.Textbox(label="Problem", interactive=False)
                    logout_button = gr.Button("Logout")

                def toggle_visibility(mode):
                    is_create = mode == "Create User"
                    return {
                        age_input: gr.update(visible=is_create),
                        problem_input: gr.update(visible=is_create),
                    }

                user_mode.change(
                    toggle_visibility,
                    inputs=[user_mode],
                    outputs=[age_input, problem_input],
                )

                def submit_user_info(mode, name, age, problem):
                    if mode == "Create User":
                        message, chat_visible, login_visible = create_new_user(name, age, problem)
                        # Update profile display if login successful
                        if current_user:
                            return message, chat_visible, login_visible, current_user.user_name, current_user.user_age, current_user.user_problem
                        return message, chat_visible, login_visible, "", 0, ""
                    else:
                        message, chat_visible, login_visible = login_user(name)
                        # Update profile display if login successful
                        if current_user:
                            return message, chat_visible, login_visible, current_user.user_name, current_user.user_age, current_user.user_problem
                        return message, chat_visible, login_visible, "", 0, ""

                submit_button.click(
                    submit_user_info,
                    inputs=[user_mode, name_input, age_input, problem_input],
                    outputs=[user_output, chat_tab, login_group, display_name, display_age, display_problem],
                )

                logout_button.click(
                    logout_user,
                    outputs=[user_output, chat_tab, login_group, display_name, display_age, display_problem],
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

    # connect to MongoDB
    db_instance = DB()

    # Emotion Analyzer and Conversation Chain
    analyzer = EmotionAnalyzer()
    chain = create_mental_health_chain_with_prompt(openai_api_key)

    # Create Gradio Interface with fixed day theme
    ui = create_user_interface(db_instance, analyzer, chain, logger)

    if use_docker_for_conversation.lower() == "true":
        logger.log("Conversation service running in Docker mode")
        ui.launch(server_name="0.0.0.0", share=False)
    else:
        logger.log("Conversation service running in local mode")
        ui.launch(share=False)


if __name__ == "__main__":
    main()
