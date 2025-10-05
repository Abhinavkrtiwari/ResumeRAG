from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
import os
import uuid
from datetime import datetime

from models import Resume, User
from schemas import ResumeResponse, ResumeListResponse
from services.file_processing_service import FileProcessingService
from services.pii_service import PIIService

class ResumeService:
    def __init__(self):
        self.file_service = FileProcessingService()
        self.pii_service = PIIService()
    
    def get_by_idempotency_key(self, idempotency_key: str, db: Session) -> Optional[ResumeResponse]:
        """Get resume by idempotency key"""
        resume = db.query(Resume).filter(Resume.idempotency_key == idempotency_key).first()
        if resume:
            return ResumeResponse.from_orm(resume)
        return None
    
    async def upload_resume(self, file, owner_id: int, idempotency_key: Optional[str], db: Session) -> ResumeResponse:
        """Upload and process a resume file"""
        # Generate idempotency key if not provided
        if not idempotency_key:
            idempotency_key = str(uuid.uuid4())
        
        # Check if already exists
        existing = self.get_by_idempotency_key(idempotency_key, db)
        if existing:
            return existing
        
        # Save file
        file_path = await self.file_service.save_file(file)
        
        # Process file content
        content, metadata = await self.file_service.process_resume_file(file_path)
        
        # Generate embeddings (simplified for demo)
        embeddings = None
        
        # Create resume record
        resume = Resume(
            filename=os.path.basename(file_path),
            original_filename=file.filename,
            file_path=file_path,
            file_size=file.size,
            content=content,
            embeddings=embeddings,
            metadata=metadata,
            idempotency_key=idempotency_key,
            owner_id=owner_id
        )
        
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        return ResumeResponse.from_orm(resume)
    
    def get_resumes(self, limit: int, offset: int, query: Optional[str], owner_id: int, db: Session) -> ResumeListResponse:
        """Get paginated list of resumes with optional search"""
        # Build query
        db_query = db.query(Resume).filter(Resume.owner_id == owner_id)
        
        # Add search filter if provided
        if query:
            db_query = db_query.filter(
                or_(
                    Resume.content.ilike(f"%{query}%"),
                    Resume.original_filename.ilike(f"%{query}%")
                )
            )
        
        # Get total count
        total = db_query.count()
        
        # Apply pagination
        resumes = db_query.offset(offset).limit(limit).all()
        
        # Calculate next offset
        next_offset = offset + limit if offset + limit < total else None
        
        return ResumeListResponse(
            items=[ResumeResponse.from_orm(resume) for resume in resumes],
            next_offset=next_offset,
            total=total
        )
    
    def get_resume(self, resume_id: int, owner_id: int, db: Session, user: User = None) -> Optional[ResumeResponse]:
        """Get a specific resume by ID with PII redaction"""
        resume = db.query(Resume).filter(
            and_(Resume.id == resume_id, Resume.owner_id == owner_id)
        ).first()
        
        if resume:
            resume_response = ResumeResponse.from_orm(resume)
            
            # Apply PII redaction if user is not a recruiter
            if user:
                resume_response.content = self.pii_service.redact_pii(resume_response.content, user)
                if resume_response.metadata:
                    resume_response.metadata = self.pii_service.redact_metadata(resume_response.metadata, user)
            
            return resume_response
        return None
