from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from .models import UserProfile, get_db
from pydantic import BaseModel
from common.exceptions import NotFoundException
from typing import Optional

router = APIRouter()

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None

@router.get("/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise NotFoundException("Profile not found")
    return profile

@router.post("/{user_id}/upsert")
def upsert_profile(user_id: int, profile_data: ProfileUpdate, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if profile:
        if profile_data.full_name: profile.full_name = profile_data.full_name
        if profile_data.bio: profile.bio = profile_data.bio
    else:
        profile = UserProfile(user_id=user_id, full_name=profile_data.full_name, bio=profile_data.bio)
        db.add(profile)
    
    db.commit()
    db.refresh(profile)
    return profile
