import os
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

from db import DB, User, Conversation
from emotion_analyzer import EmotionAnalyzer

# Import prompts
from prompts import (
    MENTAL_HEALTH_SYSTEM_TEMPLATE, 
    GREETING_PROMPT,
    EMOTION_CONSISTENCY_PROMPT,
    DOMINANT_EMOTION_PROMPT,
    CONTINUE_DIALOGUE_PROMPT
)

load_dotenv()

# Initialize LLM just once at module level
try:
    llm = HuggingFaceEndpoint(
        repo_id="microsoft/Phi-3-mini-4k-instruct",
        task="text-generation",
        max_new_tokens=512,
        do_sample=False,
        repetition_penalty=1.03,
    )
    llm = ChatHuggingFace(llm=llm)
    print("HuggingFaceEndpoint initialized successfully.")
except Exception as e:
    # Fallback to OpenAI if HuggingFace fails
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7
    )
    print("HuggingFaceEndpoint initialization failed, using OpenAI instead.")

class ConversationManager:
    """Manages conversations with users, storing history and generating responses"""
    
    def __init__(self, user_name=None, user_age=None, user_problem=None, is_new_user=False, user_id=None):
        """Initialize the conversation manager with user information"""
        self.messages = []
        self.current_emotion = {}
        self.initialized = False
        
        # Initialize user information if provided
        if user_name:
            self.user = {
                "name": user_name,
                "age": user_age,
                "problem": user_problem,
                "user_id": user_id
            }
            self.is_new_user = is_new_user
            
            # Initialize the conversation with a greeting
            self._initialize_conversation()
        else:
            self.user = {}
            self.is_new_user = False
    
    def _initialize_conversation(self):
        """Initialize the conversation with a greeting"""
        db = DB()
        
        # Get conversation history from database
        conversation_history = []
        if self.user.get("user_id"):
            db_history = db.get_conversation_history(self.user["user_id"], limit=3)
            if db_history:
                for conv in db_history:
                    conversation_history.append(f"User: {conv.get('user_input', '')}")
                    conversation_history.append(f"AI: {conv.get('AI_output', '')}")
        
        # Create initial system message with user info
        system_message = SystemMessage(content=MENTAL_HEALTH_SYSTEM_TEMPLATE.format(
            user_info=self.user,
            emotion_state="neutral",
            context=f"Previous conversation history: {conversation_history if conversation_history else 'None'}"
        ))
        
        # Generate greeting based on user info
        greeting_prompt = GREETING_PROMPT.format(
            user_name=self.user["name"],
            user_info=self.user,
            user_problem=self.user.get("problem", "")
        )
        
        greeting_response = llm.invoke(greeting_prompt)
        greeting_text = greeting_response.content
        
        # Initialize messages with system message and AI greeting
        self.messages = [system_message, AIMessage(content=greeting_text)]
        self.initialized = True
        self.last_response = greeting_text
    
    def process_input(self, user_input, input_type="text", audio_path=None):
        """Process user input and generate a response"""
        analyzer = EmotionAnalyzer()
        emotion_results = {}
        
        # Process based on input type
        if input_type == "text":
            text_emotion = analyzer.analyze_text_emotion(user_input)
            facial_emotion = analyzer.analyze_face_emotion()
            emotion_results = {
                "text_emotion": text_emotion,
                "facial_emotion": facial_emotion
            }
        elif input_type == "audio" and audio_path:
            text_emotion = analyzer.analyze_text_emotion(user_input)
            speech_emotion = analyzer.analyze_speech_emotion(audio_path)
            facial_emotion = analyzer.analyze_face_emotion()
            emotion_results = {
                "text_emotion": text_emotion,
                "speech_emotion": speech_emotion,
                "facial_emotion": facial_emotion
            }
        
        # Update current emotion
        self.current_emotion = emotion_results
        
        # Check emotion consistency
        emotion_consistent = self._check_emotion_consistency()
        
        # Handle emotion inconsistency if needed
        if not emotion_consistent:
            self._handle_emotion_conflict()
        
        # Add user message to history
        self.messages.append(HumanMessage(content=user_input))
        
        # Retrieve context from memory
        context = self._retrieve_from_memory(user_input)
        
        # Generate response
        response_text = self._generate_response(user_input, context)
        
        # Store the conversation
        self._store_conversation(user_input, response_text)
        
        # Return the response
        return response_text
    
    def _check_emotion_consistency(self):
        """Check if the emotions from different sources are consistent"""
        emotions = self.current_emotion
        
        # If fewer than 2 emotions, can't do a comparison
        if len(emotions) < 2:
            return True
        
        # Use LLM to check consistency
        prompt = EMOTION_CONSISTENCY_PROMPT.format(emotions=emotions)
        response = llm.invoke(prompt)
        result = response.content.strip().lower()
        
        return "inconsistent" not in result
    
    def _handle_emotion_conflict(self):
        """Handle inconsistent emotions by saving conflict to episodic memory"""
        emotions = self.current_emotion
        user_id = self.user.get("user_id")
        
        # Determine the dominant emotion with LLM
        prompt = DOMINANT_EMOTION_PROMPT.format(emotions=emotions)
        response = llm.invoke(prompt)
        dominant_emotion = response.content.strip().lower()
        
        # Store the emotion conflict in episodic memory
        if user_id:
            db = DB()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.store_emotion_conflict(user_id, emotions, timestamp)
            print(f"Emotion conflict detected for user {user_id}: {emotions}")
        
        self.resolved_emotion = dominant_emotion
    
    def _retrieve_from_memory(self, user_input):
        """Retrieve relevant information from semantic and episodic memory"""
        emotions = self.current_emotion
        user_id = self.user.get("user_id")
        
        context = f"User profile: {self.user}\n"
        context += f"Current emotional state: {emotions}\n"
        
        # Retrieve conversation history from episodic memory (MongoDB)
        if user_id:
            db = DB()
            conversation_history = db.get_conversation_history(user_id, limit=5)
            if conversation_history:
                context += "Recent conversation history:\n"
                for conv in conversation_history:
                    context += f"User: {conv.get('user_input', '')}\n"
                    context += f"AI: {conv.get('AI_output', '')}\n"
        
        # Extract dominant emotion for simplicity
        dominant_emotion = list(emotions.values())[0] if emotions else "neutral"
        
        # Simple keyword-based mock responses
        responses = {
            "angry": "Research shows that anger is often a secondary emotion, masking more vulnerable feelings like hurt, fear, or disappointment. Therapeutic approaches include cognitive reframing, mindfulness, and exploring underlying triggers.",
            "sad": "Sadness is a natural response to loss or disappointment. Studies indicate that expressing sadness through talking or writing can be therapeutic. Cognitive-behavioral techniques and behavioral activation are evidence-based approaches.",
            "happy": "Positive emotions like happiness broaden our thought-action repertoires and build resources. Savoring positive experiences and practicing gratitude can help maintain positive emotional states.",
            "fearful": "Fear activates the body's fight-or-flight response. Exposure therapy, which gradually confronts feared situations, has strong empirical support for treating anxiety disorders.",
            "surprised": "Surprise indicates a mismatch between expectations and reality. This presents an opportunity for learning and adaptation. Helping clients integrate surprising information can lead to cognitive restructuring.",
            "neutral": "When clients present with flat affect, it's important to explore whether this represents emotional regulation, alexithymia, or potential emotional suppression."
        }
        
        # Extract the emotion from string like "5-star sentiment" or "angry"
        emotion_key = "neutral"
        for key in responses.keys():
            if key in dominant_emotion.lower():
                emotion_key = key
                break
        
        semantic_results = responses.get(emotion_key, "No relevant information found")
        
        if semantic_results:
            context += "\nRelevant psychological information:\n"
            context += semantic_results
        
        return context
    
    def _generate_response(self, user_input, context):
        """Generate response using LLM with context from memories"""
        # Generate response using the LLM
        response = llm.invoke(self.messages)
        response_text = response.content
        
        # Add response to messages
        self.messages.append(AIMessage(content=response_text))
        self.last_response = response_text
        
        return response_text
    
    def _store_conversation(self, user_input, response_text):
        """Store conversation in episodic memory"""
        user_id = self.user.get("user_id")
        
        if user_id:
            db = DB()
            # Create User object for DB operations
            user = User(self.user.get("name", ""), self.user.get("age", 0), self.user.get("problem", ""))
            user.user_id = user_id
            
            # Store conversation with emotion data
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conversation = Conversation(user_input, response_text, timestamp, emotion_data=self.current_emotion)
            db.update_conversation(user, conversation)
            print(f"Stored conversation for user {user_id}")

def get_mental_health_workflow(user_name=None, user_age=None, user_problem=None, is_new_user=False, user_id=None):
    """Create and initialize a conversation manager"""
    # Create a new conversation manager with the user information
    conversation_manager = ConversationManager(
        user_name=user_name,
        user_age=user_age,
        user_problem=user_problem,
        is_new_user=is_new_user,
        user_id=user_id
    )
    
    # Return the conversation manager
    return conversation_manager