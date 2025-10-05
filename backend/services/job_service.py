from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
import uuid

from models import Job, User
from schemas import JobCreate, JobResponse
# from services.embedding_service import EmbeddingService

class JobService:
    def __init__(self):
        # self.embedding_service = EmbeddingService()
        pass
    
    def get_by_idempotency_key(self, idempotency_key: str, db: Session) -> Optional[JobResponse]:
        """Get job by idempotency key"""
        job = db.query(Job).filter(Job.idempotency_key == idempotency_key).first()
        if job:
            return JobResponse.from_orm(job)
        return None
    
    def create_job(self, job_create: JobCreate, owner_id: int, idempotency_key: Optional[str], db: Session) -> JobResponse:
        """Create a new job posting"""
        # Generate idempotency key if not provided
        if not idempotency_key:
            idempotency_key = str(uuid.uuid4())
        
        # Check if already exists
        existing = self.get_by_idempotency_key(idempotency_key, db)
        if existing:
            return existing
        
        # Create job text for embedding
        job_text = f"{job_create.title} {job_create.description} {' '.join(job_create.requirements)}"
        
        # Generate embeddings (simplified for demo)
        embeddings = None  # self.embedding_service.generate_embeddings(job_text)
        
        # Create job record
        job = Job(
            title=job_create.title,
            description=job_create.description,
            requirements=job_create.requirements,
            location=job_create.location,
            salary_min=job_create.salary_min,
            salary_max=job_create.salary_max,
            company=job_create.company,
            embeddings=embeddings,
            idempotency_key=idempotency_key,
            owner_id=owner_id
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        return JobResponse.from_orm(job)
    
    def get_job(self, job_id: int, owner_id: int, db: Session) -> Optional[JobResponse]:
        """Get a specific job by ID"""
        job = db.query(Job).filter(
            and_(Job.id == job_id, Job.owner_id == owner_id)
        ).first()
        
        if job:
            return JobResponse.from_orm(job)
        return None
