from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    is_recruiter: bool = False

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_recruiter: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# Resume schemas
class ResumeCreate(BaseModel):
    pass  # Created via file upload

class ResumeResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    content: str
    metadata: Optional[Dict[str, Any]] = None
    owner_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ResumeListResponse(BaseModel):
    items: List[ResumeResponse]
    next_offset: Optional[int] = None
    total: int

# Job schemas
class JobCreate(BaseModel):
    title: str
    description: str
    requirements: List[str]
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    company: str

class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    requirements: List[str]
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    company: str
    owner_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class JobListResponse(BaseModel):
    items: List[JobResponse]
    next_offset: Optional[int] = None
    total: int

# RAG schemas
class AskRequest(BaseModel):
    query: str
    k: int = 5

class AskResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]  # List of source documents with snippets

# Matching schemas
class MatchRequest(BaseModel):
    top_n: int = 10

class MatchResponse(BaseModel):
    matches: List[Dict[str, Any]]  # List of matches with scores, evidence, etc.

# Error schemas
class ErrorDetail(BaseModel):
    code: str
    field: Optional[str] = None
    message: str

class ErrorResponse(BaseModel):
    error: ErrorDetail
