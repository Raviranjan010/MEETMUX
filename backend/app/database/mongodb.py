import os
from datetime import datetime, timezone
import bcrypt
from pymongo import MongoClient, ASCENDING
from app.core.config import settings
from app.core.logging import logger

MONGODB_URL = getattr(settings, "MONGODB_URL", "mongodb://127.0.0.1:27017")
MONGODB_DB_NAME = getattr(settings, "MONGODB_DB_NAME", "runwayoptx_db")

_client = None
_db = None


def get_mongodb():
    global _client, _db
    if _db is None:
        try:
            _client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=3000)
            _db = _client[MONGODB_DB_NAME]
            init_mongodb(_db)
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB at {MONGODB_URL}: {e}")
            raise e
    return _db


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def init_mongodb(db):
    try:
        users = db["users"]
        users.create_index([("email", ASCENDING)], unique=True)
        
        # Check if default operations controller exists
        existing_user = users.find_one({"email": "controller@runwayoptx.com"})
        if not existing_user:
            now = datetime.now(timezone.utc).isoformat()
            default_user = {
                "name": "Captain Ravi Ranjan",
                "email": "controller@runwayoptx.com",
                "password_hash": hash_password("RunwayOptx2026!"),
                "role": "Operations Director",
                "badge_id": "RO-77291",
                "department": "Air Traffic Control & Gate Management",
                "airport": "DEL - Indira Gandhi International Airport",
                "security_clearance": "Level 4 - Executive Command",
                "phone": "+91 98765 43210",
                "notifications_enabled": True,
                "theme_preference": "aviation-dark",
                "two_factor_enabled": True,
                "permissions": [
                    "gate_override",
                    "solver_execute",
                    "delay_override",
                    "flight_dispatch",
                    "audit_export",
                    "user_manage"
                ],
                "created_at": now,
                "last_login": now,
                "activity_logs": [
                    {
                        "action": "RunwayOptx System Initialization",
                        "details": "MongoDB operations database initialized with role-based access control.",
                        "timestamp": now
                    },
                    {
                        "action": "MILP Gate Allocation Executed",
                        "details": "Triggered optimization run for 428 active flights with zero gate conflicts.",
                        "timestamp": now
                    },
                    {
                        "action": "Air Traffic Delay Model Synchronized",
                        "details": "Calibrated ML Gradient Boosting regressor with arrival taxi features.",
                        "timestamp": now
                    }
                ]
            }
            users.insert_one(default_user)
            logger.info("Initialized default RunwayOptx controller user in MongoDB.")
    except Exception as e:
        logger.warning(f"MongoDB initialization warning: {e}")
