from datetime import datetime, timedelta, timezone
from typing import List, Optional
import jwt
from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, EmailStr, Field

from app.core.config import settings
from app.core.logging import logger
from app.database.mongodb import (
    get_mongodb,
    hash_password,
    verify_password
)

router = APIRouter(prefix="/auth", tags=["Authentication & Profile"])

JWT_SECRET = getattr(settings, "JWT_SECRET", "runwayoptx-super-secret-command-center-key-2026")
JWT_ALGORITHM = getattr(settings, "JWT_ALGORITHM", "HS256")
JWT_EXPIRES_MINUTES = getattr(settings, "JWT_EXPIRES_MINUTES", 1440)


# -------------------------------------------------------------
# Pydantic Schemas
# -------------------------------------------------------------
class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    role: Optional[str] = "Gate Controller"
    airport: Optional[str] = "DEL - Indira Gandhi International Airport"
    department: Optional[str] = "Air Traffic Management"
    badge_id: Optional[str] = None
    phone: Optional[str] = None


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    airport: Optional[str] = None
    department: Optional[str] = None
    security_clearance: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    two_factor_enabled: Optional[bool] = None
    theme_preference: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)


class ActivityLogEntry(BaseModel):
    action: str
    details: Optional[str] = None


# -------------------------------------------------------------
# JWT Helpers
# -------------------------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=JWT_EXPIRES_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def sanitize_user(user: dict) -> dict:
    return {
        "id": str(user.get("_id", "")),
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "role": user.get("role", "Gate Controller"),
        "badge_id": user.get("badge_id", "RO-89102"),
        "department": user.get("department", "Operations"),
        "airport": user.get("airport", "DEL - Indira Gandhi International Airport"),
        "security_clearance": user.get("security_clearance", "Level 3 - Operations Access"),
        "phone": user.get("phone", ""),
        "notifications_enabled": user.get("notifications_enabled", True),
        "theme_preference": user.get("theme_preference", "aviation-dark"),
        "two_factor_enabled": user.get("two_factor_enabled", False),
        "permissions": user.get("permissions", ["gate_override", "solver_execute", "delay_override"]),
        "created_at": user.get("created_at", ""),
        "last_login": user.get("last_login", ""),
        "activity_logs": (user.get("activity_logs", []))[-20:]
    }


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication token header."
        )
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject.")
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token verification error: {str(e)}")

    db = get_mongodb()
    user = db["users"].find_one({"email": email})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account not found.")
    return user


# -------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------
@router.post("/register", summary="Register a new RunwayOptx operator")
def register_user(req: UserRegisterRequest):
    db = get_mongodb()
    users = db["users"]
    
    if users.find_one({"email": req.email.lower()}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    now = datetime.now(timezone.utc).isoformat()
    badge = req.badge_id or f"RO-{int(datetime.now().timestamp()) % 100000:05d}"
    
    # Assign default permissions based on role
    role_permissions = {
        "Operations Director": ["gate_override", "solver_execute", "delay_override", "flight_dispatch", "audit_export", "user_manage"],
        "Gate Controller": ["gate_override", "solver_execute", "delay_override"],
        "Air Traffic Analyst": ["delay_override", "audit_export"],
        "Flight Dispatcher": ["flight_dispatch", "audit_export"]
    }
    permissions = role_permissions.get(req.role, ["gate_override", "solver_execute"])

    new_user = {
        "name": req.name,
        "email": req.email.lower(),
        "password_hash": hash_password(req.password),
        "role": req.role or "Gate Controller",
        "badge_id": badge,
        "department": req.department or "Air Traffic Control",
        "airport": req.airport or "DEL - Indira Gandhi International Airport",
        "security_clearance": "Level 3 - Operations Access",
        "phone": req.phone or "",
        "notifications_enabled": True,
        "theme_preference": "aviation-dark",
        "two_factor_enabled": False,
        "permissions": permissions,
        "created_at": now,
        "last_login": now,
        "activity_logs": [
            {
                "action": "Operator Account Registered",
                "details": f"Registered as {req.role} with badge {badge}",
                "timestamp": now
            }
        ]
    }

    result = users.insert_one(new_user)
    new_user["_id"] = result.inserted_id

    access_token = create_access_token(data={"sub": new_user["email"], "role": new_user["role"]})
    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "user": sanitize_user(new_user)
    }


@router.post("/login", summary="Authenticate RunwayOptx operator")
def login_user(req: UserLoginRequest):
    db = get_mongodb()
    users = db["users"]
    user = users.find_one({"email": req.email.lower()})

    if not user or not verify_password(req.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials."
        )

    now = datetime.now(timezone.utc).isoformat()
    login_activity = {
        "action": "Operator Login",
        "details": "Authenticated to RunwayOptx Command Center",
        "timestamp": now
    }
    
    users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"last_login": now},
            "$push": {"activity_logs": login_activity}
        }
    )
    user["last_login"] = now
    if "activity_logs" not in user:
        user["activity_logs"] = []
    user["activity_logs"].append(login_activity)

    access_token = create_access_token(data={"sub": user["email"], "role": user.get("role", "Gate Controller")})
    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "user": sanitize_user(user)
    }


@router.get("/me", summary="Get currently authenticated operator profile")
def get_current_user_profile(user: dict = Depends(get_current_user)):
    return {
        "success": True,
        "user": sanitize_user(user)
    }


@router.put("/profile", summary="Update profile details in MongoDB")
def update_profile(req: ProfileUpdateRequest, user: dict = Depends(get_current_user)):
    db = get_mongodb()
    users = db["users"]
    
    update_fields = {}
    if req.name is not None: update_fields["name"] = req.name
    if req.phone is not None: update_fields["phone"] = req.phone
    if req.role is not None: update_fields["role"] = req.role
    if req.airport is not None: update_fields["airport"] = req.airport
    if req.department is not None: update_fields["department"] = req.department
    if req.security_clearance is not None: update_fields["security_clearance"] = req.security_clearance
    if req.notifications_enabled is not None: update_fields["notifications_enabled"] = req.notifications_enabled
    if req.two_factor_enabled is not None: update_fields["two_factor_enabled"] = req.two_factor_enabled
    if req.theme_preference is not None: update_fields["theme_preference"] = req.theme_preference

    now = datetime.now(timezone.utc).isoformat()
    activity_entry = {
        "action": "Profile Configuration Updated",
        "details": f"Updated fields: {', '.join(update_fields.keys())}",
        "timestamp": now
    }

    users.update_one(
        {"_id": user["_id"]},
        {
            "$set": update_fields,
            "$push": {"activity_logs": activity_entry}
        }
    )

    updated_user = users.find_one({"_id": user["_id"]})
    return {
        "success": True,
        "message": "Profile updated successfully.",
        "user": sanitize_user(updated_user)
    }


@router.put("/password", summary="Update account password")
def change_password(req: PasswordChangeRequest, user: dict = Depends(get_current_user)):
    db = get_mongodb()
    users = db["users"]

    if not verify_password(req.current_password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password verification failed."
        )

    now = datetime.now(timezone.utc).isoformat()
    users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"password_hash": hash_password(req.new_password)},
            "$push": {
                "activity_logs": {
                    "action": "Security Credentials Changed",
                    "details": "Password successfully rotated.",
                    "timestamp": now
                }
            }
        }
    )

    return {
        "success": True,
        "message": "Password changed successfully."
    }


@router.get("/activity", summary="Fetch operational activity audit trail")
def get_user_activity(user: dict = Depends(get_current_user)):
    return {
        "success": True,
        "activity_logs": user.get("activity_logs", [])
    }


@router.post("/activity", summary="Log operational action from frontend")
def log_user_activity(req: ActivityLogEntry, user: dict = Depends(get_current_user)):
    db = get_mongodb()
    users = db["users"]
    now = datetime.now(timezone.utc).isoformat()

    entry = {
        "action": req.action,
        "details": req.details or "",
        "timestamp": now
    }

    users.update_one(
        {"_id": user["_id"]},
        {"$push": {"activity_logs": entry}}
    )

    return {"success": True, "logged": entry}
