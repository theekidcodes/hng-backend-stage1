from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProfileCreate(BaseModel):
    """Schema for creating a profile"""
    name: str = Field(..., min_length=1, description="Person's name")

    class Config:
        schema_extra = {
            "example": {"name": "ella"}
        }


class ProfileResponse(BaseModel):
    """Schema for full profile response (all fields)"""
    id: str
    name: str
    gender: Optional[str] = None
    gender_probability: Optional[float] = None
    sample_size: Optional[int] = None
    age: Optional[int] = None
    age_group: Optional[str] = None
    country_id: Optional[str] = None
    country_probability: Optional[float] = None
    created_at: str  # ISO 8601 format with Z suffix

    class Config:
        schema_extra = {
            "example": {
                "id": "b3f9c1e2-7d4a-4c91-9c2a-1f0a8e5b6d12",
                "name": "ella",
                "gender": "female",
                "gender_probability": 0.99,
                "sample_size": 1234,
                "age": 46,
                "age_group": "adult",
                "country_id": "DRC",
                "country_probability": 0.85,
                "created_at": "2026-04-01T12:00:00Z"
            }
        }


class ProfileListItem(BaseModel):
    """Schema for profile in list response (minimal fields)"""
    id: str
    name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    age_group: Optional[str] = None
    country_id: Optional[str] = None


class SuccessResponse(BaseModel):
    """Generic success response wrapper"""
    status: str = "success"
    data: Optional[dict] = None
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Generic error response wrapper"""
    status: str = "error"
    message: str


class CreateProfileResponse(BaseModel):
    """Response for POST /api/profiles"""
    status: str = "success"
    message: Optional[str] = None
    data: ProfileResponse


class GetProfileResponse(BaseModel):
    """Response for GET /api/profiles/{id}"""
    status: str = "success"
    data: ProfileResponse


class ListProfilesResponse(BaseModel):
    """Response for GET /api/profiles"""
    status: str = "success"
    count: int
    data: List[ProfileListItem]
