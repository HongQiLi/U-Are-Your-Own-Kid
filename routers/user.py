# routers/user.py

from fastapi import APIRouter, HTTPException
from models.user_profile import UserProfile

router = APIRouter()

# In-memory fake user storage for demo purpose (replace with DB in production)
fake_user_db = {}

@router.post("/user/register")
def register_user(user: UserProfile):
    """
    Register a new user.
    Accepts a UserProfile object and stores it in the fake DB.
    """
    if user.user_id in fake_user_db:
        raise HTTPException(status_code=400, detail="User already exists.")
    fake_user_db[user.user_id] = user
    return {"message": "User registered successfully", "user_id": user.user_id}

@router.get("/user/{user_id}")
def get_user(user_id: str):
    """
    Retrieve a user's profile by their user_id.
    """
    user = fake_user_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user
