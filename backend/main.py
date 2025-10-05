from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import os
from dotenv import load_dotenv

from database import get_db, engine, Base
from models import Resume, Job, User, Match
from schemas import (
    ResumeCreate, ResumeResponse, ResumeListResponse,
    JobCreate, JobResponse, JobListResponse,
    AskRequest, AskResponse,
    MatchRequest, MatchResponse,
    UserCreate, UserResponse, LoginRequest, TokenResponse
)
from services import (
    ResumeService, JobService, AuthService, 
    RAGService, MatchingService, FileProcessingService
)
from middleware import RateLimitMiddleware

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="ResumeRAG API",
    description="Resume Search & Job Match API",
    version="1.0.0"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open during judging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize services
resume_service = ResumeService()
job_service = JobService()
auth_service = AuthService()
rag_service = RAGService()
matching_service = MatchingService()
file_service = FileProcessingService()

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    user = auth_service.verify_token(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user

# Public endpoints (no auth required)
@app.post("/api/register", response_model=UserResponse)
@limiter.limit("10/minute")
async def register(request: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        user = auth_service.register(request, db)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    try:
        token = auth_service.login(request, db)
        return TokenResponse(access_token=token, token_type="bearer")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

# Resume endpoints
@app.post("/api/resumes", response_model=ResumeResponse)
@limiter.limit("60/minute")
async def upload_resume(
    file: UploadFile = File(...),
    idempotency_key: Optional[str] = Header(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a resume file (PDF, DOCX, TXT) or ZIP containing multiple resumes"""
    try:
        # Check idempotency
        if idempotency_key:
            existing = resume_service.get_by_idempotency_key(idempotency_key, db)
            if existing:
                return existing
        
        resume = await resume_service.upload_resume(file, current_user.id, idempotency_key, db)
        return resume
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/resumes", response_model=ResumeListResponse)
@limiter.limit("60/minute")
async def get_resumes(
    limit: int = 10,
    offset: int = 0,
    q: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get paginated list of resumes with optional search"""
    try:
        result = resume_service.get_resumes(limit, offset, q, current_user.id, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/resumes/{resume_id}", response_model=ResumeResponse)
@limiter.limit("60/minute")
async def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific resume by ID"""
    try:
        resume = resume_service.get_resume(resume_id, current_user.id, db, current_user)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        return resume
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

# Job endpoints
@app.post("/api/jobs", response_model=JobResponse)
@limiter.limit("60/minute")
async def create_job(
    job: JobCreate,
    idempotency_key: Optional[str] = Header(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new job posting"""
    try:
        # Check idempotency
        if idempotency_key:
            existing = job_service.get_by_idempotency_key(idempotency_key, db)
            if existing:
                return existing
        
        job_response = job_service.create_job(job, current_user.id, idempotency_key, db)
        return job_response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/jobs/{job_id}", response_model=JobResponse)
@limiter.limit("60/minute")
async def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific job by ID"""
    try:
        job = job_service.get_job(job_id, current_user.id, db)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

# RAG endpoints
@app.post("/api/ask", response_model=AskResponse)
@limiter.limit("60/minute")
async def ask_question(
    request: AskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask a question about resumes using RAG"""
    try:
        response = await rag_service.ask_question(request.query, request.k, current_user.id, db)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

# Matching endpoints
@app.post("/api/jobs/{job_id}/match", response_model=MatchResponse)
@limiter.limit("60/minute")
async def match_candidates(
    job_id: int,
    request: MatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Match candidates against a job posting"""
    try:
        # Verify job exists and user has access
        job = job_service.get_job(job_id, current_user.id, db)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        matches = await matching_service.match_candidates(job_id, request.top_n, current_user.id, db)
        return matches
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
