"""
MongoDB Database Module for Indian Sign Language (ISL) Translator
Handles User Authentication (Register/Login) and Saved Stories Storage
Compatible with MongoDB Compass (Default URI: mongodb://localhost:27017/)
"""

import os
import datetime
from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING
from werkzeug.security import generate_password_hash, check_password_hash

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "isl_translator_db"


class ISLDatabase:
    def __init__(self, uri=MONGO_URI, db_name=DB_NAME):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None
        self.users = None
        self.stories = None
        self.is_connected = False
        self.connect()

    def connect(self):
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=2500)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.users = self.db['users']
            self.stories = self.db['stories']

            # Ensure indexes
            self.users.create_index([("username", ASCENDING)], unique=True)
            self.stories.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])

            self.is_connected = True
            print(f"[MongoDB] Connected successfully to '{self.db_name}' at {self.uri}")
        except Exception as e:
            self.is_connected = False
            print(f"[MongoDB] Warning: Could not connect to MongoDB: {e}")

    # ================= USER AUTHENTICATION =================

    def register_user(self, username, password, email=""):
        if not self.is_connected:
            self.connect()
            if not self.is_connected:
                return {"success": False, "error": "Database is not connected. Please ensure MongoDB is running."}

        username = (username or "").strip()
        email = (email or "").strip().lower()
        password = password or ""

        if not username or len(username) < 3:
            return {"success": False, "error": "Username must be at least 3 characters long."}
        if not password or len(password) < 4:
            return {"success": False, "error": "Password must be at least 4 characters long."}

        # Check existing username
        existing = self.users.find_one({"username": {"$regex": f"^{username}$", "$options": "i"}})
        if existing:
            return {"success": False, "error": f"Username '{username}' is already taken."}

        password_hash = generate_password_hash(password)
        user_doc = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        }

        try:
            res = self.users.insert_one(user_doc)
            return {
                "success": True,
                "user_id": str(res.inserted_id),
                "username": username,
                "email": email
            }
        except Exception as e:
            return {"success": False, "error": f"Registration failed: {str(e)}"}

    def authenticate_user(self, username, password):
        if not self.is_connected:
            self.connect()
            if not self.is_connected:
                return {"success": False, "error": "Database is not connected."}

        username = (username or "").strip()
        user = self.users.find_one({"username": {"$regex": f"^{username}$", "$options": "i"}})
        if not user:
            return {"success": False, "error": "Invalid username or password."}

        if not check_password_hash(user["password_hash"], password):
            return {"success": False, "error": "Invalid username or password."}

        return {
            "success": True,
            "user_id": str(user["_id"]),
            "username": user["username"],
            "email": user.get("email", "")
        }

    def get_user_by_id(self, user_id):
        if not self.is_connected or not user_id:
            return None
        try:
            user = self.users.find_one({"_id": ObjectId(user_id)})
            if user:
                return {
                    "user_id": str(user["_id"]),
                    "username": user["username"],
                    "email": user.get("email", "")
                }
        except Exception:
            pass
        return None

    # ================= SAVED STORIES =================

    def save_story(self, user_id, username, title, story_data):
        if not self.is_connected:
            self.connect()
            if not self.is_connected:
                return {"success": False, "error": "Database is not connected."}

        if not user_id:
            return {"success": False, "error": "User must be logged in to save stories."}

        eng = (story_data.get("story_english") or "").strip()
        hi = (story_data.get("story_hindi") or "").strip()

        if not eng and not hi:
            return {"success": False, "error": "Story is empty. Cannot save empty story."}

        now_utc = datetime.datetime.now(datetime.timezone.utc)
        now_local_str = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")

        if not title or not title.strip():
            # Generate default title from first few words of English story or date
            first_words = " ".join(eng.split()[:5]) if eng else "Sign Story"
            title = f"{first_words}... ({now_local_str})"

        story_doc = {
            "user_id": str(user_id),
            "username": username,
            "title": title.strip(),
            "story_english": eng,
            "story_hindi": hi,
            "story_raw": story_data.get("story_raw", ""),
            "sentences": story_data.get("sentences", []),
            "sentence_count": int(story_data.get("sentence_count", len(story_data.get("sentences", [])))),
            "word_count": int(story_data.get("word_count", len(eng.split()))),
            "created_at": now_utc,
            "date_display": now_local_str
        }

        try:
            res = self.stories.insert_one(story_doc)
            return {
                "success": True,
                "story_id": str(res.inserted_id),
                "title": story_doc["title"],
                "date_display": now_local_str,
                "message": "Story saved successfully to MongoDB!"
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to save story: {str(e)}"}

    def get_user_stories(self, user_id):
        if not self.is_connected:
            self.connect()
            if not self.is_connected:
                return []

        try:
            cursor = self.stories.find({"user_id": str(user_id)}).sort("created_at", DESCENDING)
            results = []
            for doc in cursor:
                results.append({
                    "id": str(doc["_id"]),
                    "title": doc.get("title", "Untitled Story"),
                    "story_english": doc.get("story_english", ""),
                    "story_hindi": doc.get("story_hindi", ""),
                    "story_raw": doc.get("story_raw", ""),
                    "sentences": doc.get("sentences", []),
                    "sentence_count": doc.get("sentence_count", 0),
                    "word_count": doc.get("word_count", 0),
                    "date_display": doc.get("date_display", doc.get("created_at", "").strftime("%d %b %Y, %I:%M %p") if isinstance(doc.get("created_at"), datetime.datetime) else "")
                })
            return results
        except Exception as e:
            print(f"[MongoDB] Error fetching stories: {e}")
            return []

    def get_story(self, story_id, user_id):
        if not self.is_connected:
            return None
        try:
            doc = self.stories.find_one({"_id": ObjectId(story_id), "user_id": str(user_id)})
            if doc:
                return {
                    "id": str(doc["_id"]),
                    "title": doc.get("title", ""),
                    "story_english": doc.get("story_english", ""),
                    "story_hindi": doc.get("story_hindi", ""),
                    "story_raw": doc.get("story_raw", ""),
                    "sentences": doc.get("sentences", []),
                    "sentence_count": doc.get("sentence_count", 0),
                    "word_count": doc.get("word_count", 0),
                    "date_display": doc.get("date_display", "")
                }
        except Exception:
            pass
        return None

    def delete_story(self, story_id, user_id):
        if not self.is_connected:
            return {"success": False, "error": "Database is not connected."}
        try:
            res = self.stories.delete_one({"_id": ObjectId(story_id), "user_id": str(user_id)})
            if res.deleted_count > 0:
                return {"success": True, "message": "Story deleted successfully."}
            return {"success": False, "error": "Story not found or unauthorized."}
        except Exception as e:
            return {"success": False, "error": str(e)}


db = ISLDatabase()

