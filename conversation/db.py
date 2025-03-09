import pymongo
import os
from dotenv import load_dotenv
from pymongo.results import InsertOneResult, UpdateResult


class User:
    def __init__(self, user_name, user_age, user_problem):
        self.user_id = None
        self.user_name = user_name
        self.user_age = user_age
        self.user_problem = user_problem


class Conversation:
    def __init__(self, user_input, AI_output, timestamp):
        self.user_input = user_input
        self.AI_output = AI_output
        self.timestamp = timestamp


class DB:
    def __init__(self):
        load_dotenv()
        mongo_uri = os.getenv("MONGO_URI", "mongodb://admin:password@mongo:27017/")
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client["conversations"]  # Database name
        self.users = self.db["users"]  # Collection for users
        self.conversations = self.db["user_conversations"]  # Collection for conversations

    def init_user(self, new_user) -> bool:
        """
        Construct a user document, where the conversations field is initialized to an empty list
        """
        user = {
            "name": new_user.user_name,
            "age": new_user.user_age,
            "problem": new_user.user_problem,
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
        conversation = {"timestamp": user_conversation.timestamp,
                        "user_input": user_conversation.user_input,
                        "AI_output": user_conversation.AI_output}
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
