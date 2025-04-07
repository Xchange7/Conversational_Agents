import os
import json
import time
import streamlit as st
from datetime import datetime, timedelta
import tempfile
from pathlib import Path

# Set up paths
REPO_ROOT = Path(__file__).resolve().parent.parent
DIALOG_SAMPLE_DIR = REPO_ROOT / "dialog-sample"
HISTORY_JSON_PATH = DIALOG_SAMPLE_DIR / "history.json"
AUDIO_DIR = DIALOG_SAMPLE_DIR / "audio"

# Ensure the audio directory exists
if not AUDIO_DIR.exists():
    os.makedirs(AUDIO_DIR, exist_ok=True)

# Load dialogue history from JSON file
def load_dialogue_history():
    try:
        with open(HISTORY_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"Error loading dialogue history: {e}")
        return []

# Dummy User class to mimic the structure of the original app
class DummyUser:
    def __init__(self, name, age=30, problem="Demo mode"):
        self.user_name = name
        self.user_age = age
        self.user_problem = problem
        # 6 hours 36 minutes ago
        self.user_created_at = datetime.now() - timedelta(hours=6, minutes=36)
        self.user_id = "demo-user-123"

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None

if 'messages' not in st.session_state:
    st.session_state.messages = []
    
if 'response_index' not in st.session_state:
    st.session_state.response_index = 0
    
if 'dialogue_history' not in st.session_state:
    st.session_state.dialogue_history = load_dialogue_history()

def get_next_response():
    """Get the next AI response and human input from dialogue history."""
    # time.sleep(5)  # Simulate processing delay
    # if not st.session_state.dialogue_history:
    #     return "No dialogue history available.", None, "No human input available."
    
    if not st.session_state.dialogue_history:
        return "No dialogue history available.", None, "No human input available."
    # Get the next response and increment index
    idx = st.session_state.response_index
    dialogue = st.session_state.dialogue_history
    
    if idx >= len(dialogue):
        # If we've reached the end, loop back to the beginning
        st.session_state.response_index = 0
        idx = 0
    
    response_text = dialogue[idx].get('AI', "No response available.")
    human_input = dialogue[idx - 1].get('human', "No human input available.")
    
    # Get corresponding audio file if it exists
    audio_file = AUDIO_DIR / f"ai_response_{idx+1:02d}.mp3"
    audio_path = str(audio_file) if audio_file.exists() else None
    
    # Increment for next time
    st.session_state.response_index += 1
    
    return response_text, audio_path, human_input

def initialize_user(user_name):
    """Initialize demo user"""
    st.session_state.user = DummyUser(user_name)
    
    # Reset response index
    st.session_state.response_index = 0
    
    # Get the first AI greeting from dialogue history
    first_response, audio_path, _ = get_next_response()
    st.session_state.messages.append({"role": "assistant", "content": first_response, "audio": audio_path})
    
    return True

def register_new_user(user_name, user_age, user_problem):
    """Register a new demo user"""
    st.session_state.user = DummyUser(user_name, user_age, user_problem)
    
    # Reset response index
    st.session_state.response_index = 0
    
    # Get the first AI greeting from dialogue history
    first_response, audio_path, _ = get_next_response()
    st.session_state.messages.append({"role": "assistant", "content": first_response, "audio": audio_path})
    
    return True

def process_user_input(user_input, input_type="text"):
    """Process user input and get next response from history"""
    time.sleep(2.5)  # Simulate processing delay
    if not st.session_state.user:
        return "Please login first.", None
    
    # Get the next response from dialogue history
    response_text, audio_path, _ = get_next_response()
    
    return response_text, audio_path

def autoplay_audio(audio_path):
    """Play audio using Streamlit's native audio player"""
    if not audio_path:
        return
    
    try:
        # Check if it's a file path
        if isinstance(audio_path, str) and os.path.exists(audio_path):
            file_format = "audio/mp3" if audio_path.endswith(".mp3") else "audio/wav"
            with open(audio_path, "rb") as audio_file:
                audio_data = audio_file.read()
                
            # Add CSS to make audio player more compact
            st.markdown("""
            <style>
            .stAudio {
                width: 200px !important;
                transform: scale(0.8);
                margin-left: 0px;
                padding-left: 0px;
                margin-top: 0px;
                margin-bottom: 0px;
                padding: 0 !important;
            }
            .stAudio > div {
                padding: 0 !important;
                margin: 0 !important;
            }
            .stAudio > div > div {
                width: 200px !important;
                padding: 0 !important;
                margin: 0 !important;
            }
            audio {
                width: 200px !important;
                height: 30px !important;
            }
            </style>
            """, unsafe_allow_html=True)

            time.sleep(2)  # Small delay to ensure CSS is applied
            
            # Use Streamlit's native audio player
            st.audio(
                data=audio_data,
                format=file_format,
                start_time=0,
                autoplay=True
            )
            
    except Exception as e:
        st.error(f"Error in autoplay_audio: {e}")

def main():
    st.set_page_config(
        page_title="Conversational Agent",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="auto"
    )

    st.markdown("""
    <style>
        /* Fixed header styling */
        .fixed-header {
            position: fixed;
            top: 1px;
            left: 35%;
            width: 30%;
            background-color: white;
            padding: 0px 0;
            margin-bottom: 0px;
            padding-bottom: 0px;
            z-index: 99999999;
        }
        
        /* Add margin to main content */
        .main {
            margin-top: 80px;
        }
    </style>
    
    <div class="fixed-header">
        <h2 style="text-align: center;">Psychological Doctor Agent</h2>
    </div>
    
    <div class="main">
    """, unsafe_allow_html=True)
    
    # Login/Registration Section
    if not st.session_state.user:
        st.header("Login / Register")
        user_name = st.text_input("Username")
        
        if st.button("Login"):
            if initialize_user(user_name):
                st.success("Login successful!")
                time.sleep(5)  # Simulate processing delay
                st.rerun()
            else:
                st.warning("User not found. Please register.")
                st.session_state.show_registration = True
        
        if st.button("Register") or st.session_state.get('show_registration', False):
            st.session_state.show_registration = True
            with st.form("registration_form"):
                user_age = st.number_input("Age", min_value=0, max_value=120)
                user_problem = st.text_area("What brings you here today?")
                if st.form_submit_button("Complete Registration"):
                    if register_new_user(user_name, user_age, user_problem):
                        st.success("Registration successful!")
                        st.rerun()
                    else:
                        st.error("Registration failed. Please try again.")
    
    # Chat Interface
    else:
        # Create main layout - 4:1 split between chat and user info/video
        chat_col, info_col = st.columns([4, 1])
        
        # Left column (4/5) - Chat interface
        with chat_col:
            # Display conversation history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
                    if message.get("audio"):
                        autoplay_audio(message["audio"])
            
            # Input methods
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Use a form to control when the input is processed
                with st.form(key="text_input_form", clear_on_submit=True):
                    text_input = st.text_input("Type your message here", key="text_input")
                    submit_button = st.form_submit_button("Send")
                    
                    if submit_button and text_input:
                        response_text, audio_path = process_user_input(text_input, "text")
                        st.session_state.messages.append({"role": "user", "content": text_input})
                        st.session_state.messages.append({"role": "assistant", "content": response_text, "audio": audio_path})
                        st.rerun()
            
            with col2:
                st.markdown("<div style='text-align: center; margin-bottom: 10px;'>🎙️ Record Audio</div>", unsafe_allow_html=True)
                
                # Initialize audio processing state if not present
                if 'audio_processed' not in st.session_state:
                    st.session_state.audio_processed = False
                
                # Get audio input
                audio_input = st.audio_input("Speak", key="mic_input")
                
                # Process recorded audio
                if audio_input and not st.session_state.audio_processed:
                    st.session_state.last_audio_data = audio_input
                    st.session_state.audio_processed = True
                    
                    # Read the uploaded file content
                    audio_bytes = audio_input.read()
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                        tmp_file.write(audio_bytes)
                        tmp_file.flush()
                        
                        # In this demo, we don't actually transcribe the audio,
                        # but use the human input from our dialogue history JSON
                        _, _, human_text = get_next_response()
                        st.session_state.response_index -= 1  # Move back one step since we just want the text
                        
                        response_text, audio_path = process_user_input(human_text, "audio")
                        
                        # Update session state
                        st.session_state.messages.append({"role": "user", "content": human_text})
                        st.session_state.messages.append({"role": "assistant", "content": response_text, "audio": audio_path})
                        
                        st.rerun()
                elif not audio_input and st.session_state.audio_processed:
                    # Reset the processing flag when there's no audio input anymore
                    st.session_state.audio_processed = False
        
        # Right column (1/5) - User info and demo indicators
        with info_col:
            # User information section
            st.subheader("User Information")
            # st.markdown(f"""
            # **Name:** {st.session_state.user.user_name}
            # **Joined:** {st.session_state.user.user_created_at.strftime('%Y-%m-%d %H:%M')}
            # **Mode:** DEMO
            # """)

            st.info(f"""
                **Name:** {st.session_state.user.user_name}  
                **Joined:** {st.session_state.user.user_created_at.strftime('%Y-%m-%d %H:%M')}  
                **Mode:** Chatbot   
                **Camera:** Hidden  
                **Microphone:** Enabled
                """
            )
            
            st.markdown("---")
            
            # End Conversation Button
            if st.button("End Conversation", key="end_conversation", type="primary"):
                st.success("Conversation ended.")
                # Reset conversation but keep user logged in
                st.session_state.messages = []
                st.session_state.response_index = 0
                
                # Get the first response again
                first_response, audio_path, _ = get_next_response()
                st.session_state.messages.append({"role": "assistant", "content": first_response, "audio": audio_path})
                st.rerun()
            
            st.markdown("---")
            
            # Info about demo mode
            # st.subheader("Demo Mode Info")
            # st.info("""
            # **This is a demo mode**
            
            # Responses are pre-set from history.json and will cycle through sequentially.
            # No actual processing or AI backend is connected.
            # """)

if __name__ == "__main__":
    main()
