from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_recruiter = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    resumes = relationship("Resume", back_populates="owner")
    jobs = relationship("Job", back_populates="owner")

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embeddings = Column(JSON)  # Store vector embeddings
    metadata = Column(JSON)  # Store parsed metadata (skills, experience, etc.)
    idempotency_key = Column(String, unique=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="resumes")
    matches = relationship("Match", back_populates="resume")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(JSON)  # List of requirements
    location = Column(String)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    company = Column(String, nullable=False)
    embeddings = Column(JSON)  # Store vector embeddings
    idempotency_key = Column(String, unique=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="jobs")
    matches = relationship("Match", back_populates="job")

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    score = Column(Float, nullable=False)  # Match score (0-1)
    evidence = Column(JSON)  # Evidence supporting the match
    missing_requirements = Column(JSON)  # Missing requirements
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="matches")
    resume = relationship("Resume", back_populates="matches")
