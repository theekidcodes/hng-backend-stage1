from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid7 import uuid7
from datetime import datetime

from database import Profile, get_db, engine, Base
from schemas import (
    ProfileCreate, ProfileResponse, ProfileListItem,
    CreateProfileResponse, GetProfileResponse, ListProfilesResponse
)
from external_api import ExternalAPIService

# Initialize FastAPI app
app = FastAPI(
    title="Backend Wizards Stage 1 API",
    description="Data Persistence & API Design Assessment",
    version="1.0.0"
)

# Create tables
Base.metadata.create_all(bind=engine)


# ============= MIDDLEWARE =============
@app.middleware("http")
async def add_cors_header(request, call_next):
    """Add CORS header to all responses"""
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


# ============= ENDPOINTS =============

@app.post("/api/profiles", response_model=CreateProfileResponse, status_code=201)
async def create_profile(
    profile_data: ProfileCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new profile by calling external APIs.
    
    If a profile with the same name already exists, return the existing one.
    If any external API returns invalid data, return 502 error.
    """
    
    # Validate input
    if not profile_data.name or not profile_data.name.strip():
        raise HTTPException(
            status_code=400,
            detail="Name is required and cannot be empty"
        )
    
    name = profile_data.name.strip()
    
    # Check if profile already exists
    existing_profile = db.query(Profile).filter(
        func.lower(Profile.name) == func.lower(name)
    ).first()
    
    if existing_profile:
        return CreateProfileResponse(
            status="success",
            message="Profile already exists",
            data=ProfileResponse(
                id=existing_profile.id,
                name=existing_profile.name,
                gender=existing_profile.gender,
                gender_probability=existing_profile.gender_probability,
                sample_size=existing_profile.sample_size,
                age=existing_profile.age,
                age_group=existing_profile.age_group,
                country_id=existing_profile.country_id,
                country_probability=existing_profile.country_probability,
                created_at=existing_profile.created_at.isoformat() + "Z"
            )
        )
    
    # Call external APIs
    api_data = await ExternalAPIService.get_all_data(name)
    
    if api_data is None:
        # One of the APIs returned invalid data
        # We need to determine which one and return 502
        # Try each API individually to identify which one failed
        try:
            await ExternalAPIService.get_gender(name)
        except:
            raise HTTPException(
                status_code=502,
                detail="Genderize returned an invalid response"
            )
        
        try:
            await ExternalAPIService.get_age(name)
        except:
            raise HTTPException(
                status_code=502,
                detail="Agify returned an invalid response"
            )
        
        try:
            await ExternalAPIService.get_nationality(name)
        except:
            raise HTTPException(
                status_code=502,
                detail="Nationalize returned an invalid response"
            )
    
    # Create new profile
    new_profile = Profile(
        id=str(uuid7()),
        name=name,
        gender=api_data["gender"],
        gender_probability=api_data["gender_probability"],
        sample_size=api_data["sample_size"],
        age=api_data["age"],
        age_group=api_data["age_group"],
        country_id=api_data["country_id"],
        country_probability=api_data["country_probability"],
        created_at=datetime.utcnow()
    )
    
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    
    return CreateProfileResponse(
        status="success",
        data=ProfileResponse(
            id=new_profile.id,
            name=new_profile.name,
            gender=new_profile.gender,
            gender_probability=new_profile.gender_probability,
            sample_size=new_profile.sample_size,
            age=new_profile.age,
            age_group=new_profile.age_group,
            country_id=new_profile.country_id,
            country_probability=new_profile.country_probability,
            created_at=new_profile.created_at.isoformat() + "Z"
        )
    )


@app.get("/api/profiles/{profile_id}", response_model=GetProfileResponse)
async def get_profile(profile_id: str, db: Session = Depends(get_db)):
    """Get a single profile by ID"""
    
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )
    
    return GetProfileResponse(
        status="success",
        data=ProfileResponse(
            id=profile.id,
            name=profile.name,
            gender=profile.gender,
            gender_probability=profile.gender_probability,
            sample_size=profile.sample_size,
            age=profile.age,
            age_group=profile.age_group,
            country_id=profile.country_id,
            country_probability=profile.country_probability,
            created_at=profile.created_at.isoformat() + "Z"
        )
    )


@app.get("/api/profiles", response_model=ListProfilesResponse)
async def list_profiles(
    gender: str = Query(None, description="Filter by gender"),
    country_id: str = Query(None, description="Filter by country_id"),
    age_group: str = Query(None, description="Filter by age_group"),
    db: Session = Depends(get_db)
):
    """
    Get all profiles with optional filtering.
    
    Query parameters are case-insensitive.
    """
    
    query = db.query(Profile)
    
    # Apply filters (case-insensitive)
    if gender:
        query = query.filter(
            func.lower(Profile.gender) == func.lower(gender)
        )
    
    if country_id:
        query = query.filter(
            func.lower(Profile.country_id) == func.lower(country_id)
        )
    
    if age_group:
        query = query.filter(
            func.lower(Profile.age_group) == func.lower(age_group)
        )
    
    profiles = query.all()
    
    return ListProfilesResponse(
        status="success",
        count=len(profiles),
        data=[
            ProfileListItem(
                id=p.id,
                name=p.name,
                gender=p.gender,
                age=p.age,
                age_group=p.age_group,
                country_id=p.country_id
            )
            for p in profiles
        ]
    )


@app.delete("/api/profiles/{profile_id}", status_code=204)
async def delete_profile(profile_id: str, db: Session = Depends(get_db)):
    """Delete a profile by ID"""
    
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )
    
    db.delete(profile)
    db.commit()
    
    return None


# ============= ERROR HANDLING =============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom error response format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail
        }
    )


# ============= HEALTH CHECK =============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
