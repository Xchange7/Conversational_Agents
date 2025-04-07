import os
import streamlit as st
from dotenv import load_dotenv
import tempfile
import base64
from datetime import datetime
from audiorecorder import audiorecorder  # Add this import

from speech_to_text import transcribe_audio
from emotion_analyzer import EmotionAnalyzer
from text_to_speech import text_to_speech
from db import DB, User, Conversation
from logger import Logger
from conversation_workflow import get_mental_health_workflow

from rich.traceback import install

install(show_locals=True, width=200)  # width 可调，比如 150 或 200


# Load environment variables
load_dotenv()

# Initialize components
db = DB()
analyzer = EmotionAnalyzer()
logger = Logger()

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'conversation_manager' not in st.session_state:
    st.session_state.conversation_manager = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

def initialize_user(user_name):
    """Initialize user session by checking if user exists"""
    existing_user = db.get_user_by_name(user_name)
    if existing_user:
        st.session_state.user = existing_user
        # Initialize conversation manager with existing user
        st.session_state.conversation_manager = get_mental_health_workflow(
            user_name=existing_user.user_name,
            user_age=existing_user.user_age, 
            user_problem=existing_user.user_problem,
            is_new_user=False,
            user_id=str(existing_user.user_id)
        )
        
        # Get the greeting from the conversation manager
        greeting = st.session_state.conversation_manager.last_response
        st.session_state.messages.append({"role": "assistant", "content": greeting})
        return True
    else:
        return False

def register_new_user(user_name, user_age, user_problem):
    """Register a new user"""
    new_user = User(user_name, user_age, user_problem)
    success = db.init_user(new_user)
    
    if success:
        st.session_state.user = new_user
        # Initialize conversation manager with new user
        st.session_state.conversation_manager = get_mental_health_workflow(
            user_name=user_name,
            user_age=user_age,
            user_problem=user_problem,
            is_new_user=True,
            user_id=str(new_user.user_id)
        )
        
        # Get the greeting from the conversation manager
        greeting = st.session_state.conversation_manager.last_response
        st.session_state.messages.append({"role": "assistant", "content": greeting})
        return True
    return False

def process_text_input(text_input):
    """Process text input and generate response"""
    if not st.session_state.conversation_manager:
        return "Please login first."
    
    # Get response from conversation manager
    response_text = st.session_state.conversation_manager.process_input(
        user_input=text_input,
        input_type="text"
    )
    
    # Generate audio response
    try:
        audio_data = text_to_speech(response_text)
        return response_text, audio_data
    except Exception as e:
        logger.log_error(f"Error during text-to-speech conversion: {e}")
        return response_text, None

def process_audio_input(audio_file):
    """Process audio input and generate response"""
    if not st.session_state.conversation_manager:
        return "Please login first.", None
    
    try:
        # Transcribe audio to text
        transcribed_text = transcribe_audio(audio_file, model_name="base")
        
        # Get response from conversation manager
        response_text = st.session_state.conversation_manager.process_input(
            user_input=transcribed_text,
            input_type="audio",
            audio_path=audio_file
        )
        
        # Generate audio response
        try:
            audio_data = text_to_speech(response_text)
            return response_text, audio_data, transcribed_text
        except Exception as e:
            logger.log_error(f"Error during text-to-speech conversion: {e}")
            return response_text, None, transcribed_text
    except Exception as e:
        logger.log_error(f"Failed to process audio: {e}")
        return f"Error processing audio: {e}", None, None

def autoplay_audio(audio_data):
    """Play audio using Streamlit's native audio player"""
    try:
        # Log audio data details for debugging
        logger.log(f"Audio data type: {type(audio_data)}, size: {len(audio_data) if audio_data else 'None'}")
        
        # Check if it's a file path (string ending with .mp3 or .wav)
        if isinstance(audio_data, str) and (audio_data.endswith(".mp3") or ".wav" in audio_data):
            # It's a file path, read the content
            logger.log(f"Audio data is a file path: {audio_data}")
            file_format = "audio/mp3" if audio_data.endswith(".mp3") else "audio/wav"
            with open(audio_data, "rb") as audio_file:
                audio_data = audio_file.read()
        elif isinstance(audio_data, str):
            # If it's a string but not a path, it might be already encoded content
            audio_data = audio_data.encode()
            # Default to mp3 since that's what text_to_speech seems to generate
            file_format = "audio/mp3"
        else:
            # Binary data, try to detect format based on header
            if len(audio_data) >= 4 and audio_data[:4] == b"RIFF":  # WAV files start with "RIFF"
                file_format = "audio/wav"
            else:
                # Default to MP3 for other binary data
                file_format = "audio/mp3"
        
        if not audio_data or len(audio_data) == 0:
            logger.log_error("Empty audio data received, cannot play.")
            return
        
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
        
        # Use Streamlit's native audio player with the correct format
        logger.log(f"Playing audio with format: {file_format}")
        st.audio(
            data=audio_data,
            format=file_format,
            start_time=0,
            autoplay=True
        )
        
        logger.log("Audio playback started using Streamlit's audio player")
    except Exception as e:
        logger.log_error(f"Error in autoplay_audio: {e}")

def save_conversation_history():
    """Save the current conversation history to the database"""
    if not st.session_state.user or not st.session_state.messages:
        return False
    
    try:
        # Convert the messages to the format expected by the database
        for i in range(0, len(st.session_state.messages), 2):
            # Ensure we have both user and assistant messages
            if i+1 < len(st.session_state.messages):
                user_msg = st.session_state.messages[i]
                assistant_msg = st.session_state.messages[i+1]
                
                # Create a conversation object
                conversation = Conversation(
                    user_input=user_msg["content"],
                    AI_output=assistant_msg["content"],
                    timestamp=datetime.now()
                )
                
                # Save to database
                db.update_conversation(st.session_state.user, conversation)
        
        return True
    except Exception as e:
        logger.log_error(f"Error saving conversation history: {e}")
        return False

def main():

    st.set_page_config(
        page_title="Agent",
        page_icon="🚀",
        layout="wide",  # 默认宽屏模式
        initial_sidebar_state="auto"  # 可选：自动/展开/折叠
    )

    st.markdown("""
    <style>
        /* 固定标题栏并居中 */
        .fixed-header {
            position: fixed;
            top: 1px;
            left: 35%;  /* Added left position */
            
            width: 30%;
            background-color: white;
            padding: 0px 0;
            # bottom margin to 0
            margin-bottom: 0px;
            padding-bottom: 0px;
            # box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            z-index: 99999999;
        }
        
        /* 为内容添加上边距，防止被标题遮挡 */
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
                # Force Streamlit to refresh and display chat interface
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
                        # Force Streamlit to refresh and display chat interface
                        st.rerun()
                    else:
                        st.error("Registration failed. Please try again.")
    
    # Chat Interface
    else:
        # st.header("Chat with the Agent")
        
        # Create main layout - 4:1 split between chat and user info/video
        chat_col, info_col = st.columns([4, 1])
        
        # Left column (4/5) - Chat interface
        with chat_col:
            # Display conversation history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
                    if message.get("audio"):
                        logger.log(f"Playing audio for message")
                        autoplay_audio(message["audio"])
            
            # Input methods
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Use a form to control when the input is processed
                with st.form(key="text_input_form", clear_on_submit=True):
                    text_input = st.text_input("Type your message here", key="text_input")
                    submit_button = st.form_submit_button("Send")
                    
                    if submit_button and text_input:
                        response_text, audio_data = process_text_input(text_input)
                        st.session_state.messages.append({"role": "user", "content": text_input})
                        st.session_state.messages.append({"role": "assistant", "content": response_text, "audio": audio_data})
                        st.rerun()
            
            with col2:
                st.markdown("<div style='text-align: center; margin-bottom: 10px;'>🎙️ Record Audio</div>", unsafe_allow_html=True)
                
                # Initialize audio processing state if not present
                if 'audio_processed' not in st.session_state:
                    st.session_state.audio_processed = False
                
                # 使用 st.audio_input 获取音频输入
                audio_input = st.audio_input("Speak", key="mic_input")
                
                # 处理录制的音频
                if audio_input and not st.session_state.audio_processed:
                    st.session_state.last_audio_data = audio_input
                    st.session_state.audio_processed = True
                    
                    # 读取 UploadedFile 的内容
                    audio_bytes = audio_input.read()
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                        tmp_file.write(audio_bytes)  # 现在写入的是字节数据
                        tmp_file.flush()  # 确保数据写入磁盘
                        
                        # 处理音频文件
                        response_text, audio_data, transcribed_text = process_audio_input(tmp_file.name)
                        
                        # 更新会话状态
                        st.session_state.messages.append({"role": "user", "content": f"[Transcribed Audio] {transcribed_text}"})
                        st.session_state.messages.append({"role": "assistant", "content": response_text, "audio": audio_data})
                        
                        # Reset audio state and re-render page to clear the audio widget
                        st.rerun()
                elif not audio_input and st.session_state.audio_processed:
                    # Reset the processing flag when there's no audio input anymore
                    st.session_state.audio_processed = False
        
        # Right column (1/4) - User info and video feed
        with info_col:
            # User information section
            st.subheader("User Information")
            st.markdown(f"""
            **Name:** {st.session_state.user.user_name}  
            **Joined:** {st.session_state.user.user_created_at.strftime('%Y-%m-%d %H:%M')}
            """)
            
            st.markdown("---")
            
            # End Conversation Button
            if st.button("End Conversation", key="end_conversation", type="primary"):
                # Save conversation history
                if save_conversation_history():
                    st.success("Conversation ended. Your chat history has been saved!")
                    # Reset conversation but keep user logged in
                    st.session_state.messages = []
                    # Re-initialize conversation manager to get a fresh greeting
                    st.session_state.conversation_manager = get_mental_health_workflow(
                        user_name=st.session_state.user.user_name,
                        user_age=st.session_state.user.user_age, 
                        user_problem=st.session_state.user.user_problem,
                        is_new_user=False,
                        user_id=str(st.session_state.user.user_id)
                    )
                    # Get the greeting from the conversation manager
                    greeting = st.session_state.conversation_manager.last_response
                    st.session_state.messages.append({"role": "assistant", "content": greeting})
                    st.rerun()
                else:
                    st.error("Failed to save conversation history. Please try again.")
            
            st.markdown("---")
            
            # Video feed
            st.subheader("Emotion Analysis")
            st.markdown("""
                <div style="display: flex; justify-content: center;">
                    <img src="http://localhost:5005/video_feed" width="100%" 
                        style="border-radius: 10px; border: 2px solid #ccc;">
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()