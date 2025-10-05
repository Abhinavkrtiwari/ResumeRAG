from sqlalchemy.orm import Session
from typing import List, Dict, Any
import re

from models import Job, Resume, Match
from schemas import MatchResponse
from services.embedding_service import EmbeddingService

class MatchingService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
    
    async def match_candidates(self, job_id: int, top_n: int, user_id: int, db: Session) -> MatchResponse:
        """Match candidates against a job posting"""
        # Get the job
        job = db.query(Job).filter(Job.id == job_id, Job.owner_id == user_id).first()
        if not job:
            raise ValueError("Job not found")
        
        # Get all resumes for the user
        resumes = db.query(Resume).filter(Resume.owner_id == user_id).all()
        
        if not resumes:
            return MatchResponse(matches=[])
        
        # Prepare job text for matching
        job_text = f"{job.title} {job.description} {' '.join(job.requirements)}"
        job_embedding = self.embedding_service.generate_embeddings(job_text)
        
        # Calculate matches
        matches = []
        for resume in resumes:
            if resume.embeddings:
                # Calculate similarity score
                similarity = self.embedding_service.calculate_similarity(
                    job_embedding, resume.embeddings
                )
                
                # Extract evidence and missing requirements
                evidence = self._extract_evidence(job, resume)
                missing_requirements = self._find_missing_requirements(job, resume)
                
                matches.append({
                    'resume_id': resume.id,
                    'filename': resume.original_filename,
                    'score': similarity,
                    'evidence': evidence,
                    'missing_requirements': missing_requirements
                })
        
        # Sort by score (descending)
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top N matches
        top_matches = matches[:top_n]
        
        return MatchResponse(matches=top_matches)
    
    def _extract_evidence(self, job: Job, resume: Resume) -> List[Dict[str, Any]]:
        """Extract evidence supporting the match"""
        evidence = []
        
        # Check for required skills
        job_requirements = job.requirements
        resume_content = resume.content.lower()
        
        for requirement in job_requirements:
            requirement_lower = requirement.lower()
            
            # Check if requirement is mentioned in resume
            if requirement_lower in resume_content:
                # Find the context around the requirement
                context = self._find_context(requirement_lower, resume.content)
                evidence.append({
                    'requirement': requirement,
                    'evidence': context,
                    'type': 'skill_match'
                })
        
        # Check for experience level
        experience_evidence = self._check_experience_match(job, resume)
        if experience_evidence:
            evidence.extend(experience_evidence)
        
        # Check for education requirements
        education_evidence = self._check_education_match(job, resume)
        if education_evidence:
            evidence.extend(education_evidence)
        
        return evidence
    
    def _find_missing_requirements(self, job: Job, resume: Resume) -> List[str]:
        """Find missing requirements for the job"""
        missing = []
        
        job_requirements = job.requirements
        resume_content = resume.content.lower()
        
        for requirement in job_requirements:
            requirement_lower = requirement.lower()
            
            # Check if requirement is mentioned in resume
            if requirement_lower not in resume_content:
                # Check for similar terms
                if not self._has_similar_term(requirement_lower, resume_content):
                    missing.append(requirement)
        
        return missing
    
    def _find_context(self, term: str, content: str) -> str:
        """Find context around a term in the content"""
        # Find the position of the term
        pos = content.lower().find(term)
        if pos == -1:
            return ""
        
        # Extract context (100 chars before and after)
        start = max(0, pos - 100)
        end = min(len(content), pos + len(term) + 100)
        
        context = content[start:end]
        
        # Clean up the context
        context = re.sub(r'\s+', ' ', context).strip()
        
        return context
    
    def _has_similar_term(self, requirement: str, content: str) -> bool:
        """Check if content has similar terms to the requirement"""
        # Simple similarity check - look for key words
        requirement_words = requirement.split()
        
        for word in requirement_words:
            if len(word) > 3:  # Only check meaningful words
                if word in content:
                    return True
        
        return False
    
    def _check_experience_match(self, job: Job, resume: Resume) -> List[Dict[str, Any]]:
        """Check for experience level matches"""
        evidence = []
        
        # Look for experience indicators in job description
        job_text = job.description.lower()
        resume_content = resume.content.lower()
        
        # Check for years of experience
        years_pattern = r'(\d+)\s*years?\s*(?:of\s*)?experience'
        job_years = re.findall(years_pattern, job_text)
        
        if job_years:
            required_years = int(job_years[0])
            
            # Look for experience in resume
            resume_years = re.findall(years_pattern, resume_content)
            if resume_years:
                candidate_years = int(resume_years[0])
                
                if candidate_years >= required_years:
                    evidence.append({
                        'requirement': f"{required_years} years of experience",
                        'evidence': f"Candidate has {candidate_years} years of experience",
                        'type': 'experience_match'
                    })
        
        return evidence
    
    def _check_education_match(self, job: Job, resume: Resume) -> List[Dict[str, Any]]:
        """Check for education matches"""
        evidence = []
        
        # Look for education requirements in job description
        job_text = job.description.lower()
        resume_content = resume.content.lower()
        
        # Common education terms
        education_terms = ['bachelor', 'master', 'phd', 'degree', 'university', 'college']
        
        for term in education_terms:
            if term in job_text:
                if term in resume_content:
                    context = self._find_context(term, resume.content)
                    evidence.append({
                        'requirement': f"Education: {term}",
                        'evidence': context,
                        'type': 'education_match'
                    })
        
        return evidence
