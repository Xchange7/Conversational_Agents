import pymongo
import os
from dotenv import load_dotenv
from pymongo.results import InsertOneResult, UpdateResult
from datetime import datetime


class User:
    def __init__(self, user_name, user_age, user_problem):
        self.user_id = None
        self.user_name = user_name
        self.user_age = user_age
        self.user_problem = user_problem
        self.user_created_at = datetime.now()  # Add creation timestamp


class Conversation:
    def __init__(self, user_input, AI_output, timestamp, emotion_data=None):
        self.user_input = user_input
        self.AI_output = AI_output
        self.timestamp = timestamp
        self.emotion_data = emotion_data or {}  # Store emotion analysis data


class DB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DB, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        load_dotenv()
        use_docker_for_conversation = os.getenv("USE_DOCKER_FOR_CONVERSATION", "True")
        if use_docker_for_conversation.lower() == "True":
            # run conversation inside docker
            mongo_uri = os.getenv("MONGO_URI", "mongodb://admin:password@mongo:27017/")
        else:
            # run conversation locally
            mongo_uri = os.getenv("MONGO_URI", "mongodb://admin:password@localhost:27017/")

        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client["conversations"]  # Database name
        self.users = self.db["users"]  # Collection for users
        self.conversations = self.db["user_conversations"]  # Collection for conversations
        self._initialized = True

    def init_user(self, new_user) -> bool:
        """
        Construct a user document, where the conversations field is initialized to an empty list
        """
        user = {
            "name": new_user.user_name,
            "age": new_user.user_age,
            "problem": new_user.user_problem,
            "created_at": new_user.user_created_at,  # Save creation time to database
            "conversations": []
        }
        try:
            insert_result: InsertOneResult = self.users.insert_one(user)
            print("Your User ID is : " + str(insert_result.inserted_id))
            new_user.user_id = insert_result.inserted_id
            return True

        except Exception as e:
            print(e)
            return False

    def update_conversation(self, user, user_conversation) -> bool:
        """Updates the user's conversation history in the database."""
        conversation = {
            "timestamp": user_conversation.timestamp,
            "user_input": user_conversation.user_input,
            "AI_output": user_conversation.AI_output
        }
        
        # Add emotion data if available
        if hasattr(user_conversation, 'emotion_data') and user_conversation.emotion_data:
            conversation["emotion_data"] = user_conversation.emotion_data
            
        try:
            result: UpdateResult = self.users.update_one(
                {"_id": user.user_id},
                {"$push": {"conversations": conversation}},
            )
            if result.modified_count == 1:
                print("Result of User is Updated")

        except Exception as e:
            print(e)

        return True

    def get_user_by_name(self, user_name: str):
        """Retrieves a user from the database by their name."""
        try:
            user = self.users.find_one({"name": user_name})
            if user:
                retrieved_user = User(user["name"], user["age"], user["problem"])
                retrieved_user.user_id = user["_id"]
                # Load the creation time if available, otherwise use current time
                retrieved_user.user_created_at = user.get("created_at", datetime.now())
                return retrieved_user
            else:
                return None
        except Exception as e:
            print(e)
            return None

    def get_conversation_history(self, user_id, limit=5):
        """Retrieves the user's recent conversation history from the database."""
        try:
            user = self.users.find_one({"_id": user_id})
            if user and "conversations" in user:
                # Return the most recent conversations, limited by the specified amount
                return user["conversations"][-limit:] if len(user["conversations"]) > limit else user["conversations"]
            return []
        except Exception as e:
            print(f"Error retrieving conversation history: {e}")
            return []
    
    def store_emotion_conflict(self, user_id, emotion_data, timestamp):
        """Stores an emotion conflict record in the database for later analysis."""
        try:
            emotion_record = {
                "user_id": user_id,
                "timestamp": timestamp,
                "emotion_data": emotion_data,
                "is_conflict": True
            }
            
            # Create a new collection for emotion data if it doesn't exist
            if "emotion_conflicts" not in self.db.list_collection_names():
                self.db.create_collection("emotion_conflicts")
                
            self.db.emotion_conflicts.insert_one(emotion_record)
            return True
        except Exception as e:
            print(f"Error storing emotion conflict: {e}")
            return False