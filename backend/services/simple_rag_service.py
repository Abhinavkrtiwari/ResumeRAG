from sqlalchemy.orm import Session
from typing import List, Dict, Any
import re

from models import Resume
from schemas import AskResponse

class SimpleRAGService:
    def __init__(self):
        pass
    
    async def ask_question(self, query: str, k: int, user_id: int, db: Session) -> AskResponse:
        """Answer a question about resumes using simple text matching"""
        # Get all resumes for the user
        resumes = db.query(Resume).filter(Resume.owner_id == user_id).all()
        
        if not resumes:
            return AskResponse(
                answer="No resumes found. Please upload some resumes first.",
                sources=[]
            )
        
        # Simple text matching based on query keywords
        query_lower = query.lower()
        query_words = query_lower.split()
        
        # Find relevant resumes
        relevant_resumes = []
        for resume in resumes:
            content_lower = resume.content.lower()
            score = 0
            
            # Count matching words
            for word in query_words:
                if word in content_lower:
                    score += 1
            
            if score > 0:
                relevant_resumes.append({
                    'resume': resume,
                    'score': score
                })
        
        # Sort by score
        relevant_resumes.sort(key=lambda x: x['score'], reverse=True)
        
        # Take top k
        top_resumes = relevant_resumes[:k]
        
        # Generate answer
        answer = self._generate_simple_answer(query, top_resumes)
        
        # Prepare sources
        sources = []
        for item in top_resumes:
            resume = item['resume']
            score = item['score']
            
            # Extract relevant snippets
            snippets = self._extract_snippets(query, resume.content)
            
            sources.append({
                'resume_id': resume.id,
                'filename': resume.original_filename,
                'similarity_score': score / len(query_words),  # Normalize score
                'snippets': snippets
            })
        
        return AskResponse(
            answer=answer,
            sources=sources
        )
    
    def _generate_simple_answer(self, query: str, relevant_resumes: List[Dict[str, Any]]) -> str:
        """Generate a simple answer based on relevant resumes"""
        if not relevant_resumes:
            return "I couldn't find relevant information in the uploaded resumes."
        
        query_lower = query.lower()
        
        # Simple answer generation based on query type
        if any(word in query_lower for word in ['skill', 'skills', 'technology', 'technologies']):
            return self._generate_skills_answer(relevant_resumes)
        elif any(word in query_lower for word in ['experience', 'work', 'job', 'career']):
            return self._generate_experience_answer(relevant_resumes)
        elif any(word in query_lower for word in ['education', 'degree', 'university', 'college']):
            return self._generate_education_answer(relevant_resumes)
        elif any(word in query_lower for word in ['contact', 'email', 'phone', 'linkedin']):
            return self._generate_contact_answer(relevant_resumes)
        else:
            return self._generate_general_answer(query, relevant_resumes)
    
    def _generate_skills_answer(self, relevant_resumes: List[Dict[str, Any]]) -> str:
        """Generate answer about skills"""
        all_skills = set()
        
        for item in relevant_resumes:
            resume = item['resume']
            content = resume.content.lower()
            
            # Extract skills from content
            skills = self._extract_skills_from_text(content)
            all_skills.update(skills)
        
        if all_skills:
            skills_list = list(all_skills)[:10]  # Top 10 skills
            return f"Based on the uploaded resumes, I found these skills: {', '.join(skills_list)}."
        else:
            return "I couldn't find specific skills mentioned in the resumes."
    
    def _generate_experience_answer(self, relevant_resumes: List[Dict[str, Any]]) -> str:
        """Generate answer about work experience"""
        experiences = []
        
        for item in relevant_resumes:
            resume = item['resume']
            content = resume.content
            
            # Extract experience information
            exp_info = self._extract_experience_from_text(content)
            if exp_info:
                experiences.extend(exp_info)
        
        if experiences:
            return f"Based on the resumes, I found work experience at: {', '.join(experiences[:5])}."
        else:
            return "I couldn't find specific work experience details in the resumes."
    
    def _generate_education_answer(self, relevant_resumes: List[Dict[str, Any]]) -> str:
        """Generate answer about education"""
        education_info = []
        
        for item in relevant_resumes:
            resume = item['resume']
            content = resume.content
            
            # Extract education information
            edu_info = self._extract_education_from_text(content)
            if edu_info:
                education_info.extend(edu_info)
        
        if education_info:
            return f"Based on the resumes, I found education information: {', '.join(education_info[:3])}."
        else:
            return "I couldn't find specific education details in the resumes."
    
    def _generate_contact_answer(self, relevant_resumes: List[Dict[str, Any]]) -> str:
        """Generate answer about contact information"""
        contact_info = []
        
        for item in relevant_resumes:
            resume = item['resume']
            content = resume.content
            
            # Extract contact information
            contact = self._extract_contact_from_text(content)
            if contact:
                contact_info.extend(contact)
        
        if contact_info:
            return f"Based on the resumes, I found contact information: {', '.join(contact_info[:3])}."
        else:
            return "I couldn't find specific contact information in the resumes."
    
    def _generate_general_answer(self, query: str, relevant_resumes: List[Dict[str, Any]]) -> str:
        """Generate a general answer based on query and relevant resumes"""
        if not relevant_resumes:
            return "I couldn't find relevant information to answer your question."
        
        # Get the most relevant resume
        most_relevant = relevant_resumes[0]
        content = most_relevant['resume'].content
        
        # Extract relevant snippets
        snippets = self._extract_snippets(query, content)
        
        if snippets:
            return f"Based on the most relevant resume, here's what I found: {' '.join(snippets[:2])}"
        else:
            return "I found some relevant resumes but couldn't extract specific information to answer your question."
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from text"""
        skills_keywords = [
            'python', 'javascript', 'java', 'react', 'node.js', 'sql', 'aws', 'docker',
            'kubernetes', 'git', 'html', 'css', 'typescript', 'angular', 'vue', 'django',
            'flask', 'fastapi', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'machine learning', 'ai', 'data science', 'analytics', 'project management',
            'agile', 'scrum', 'leadership', 'communication', 'problem solving'
        ]
        
        found_skills = []
        for skill in skills_keywords:
            if skill in text:
                found_skills.append(skill)
        
        return found_skills
    
    def _extract_experience_from_text(self, text: str) -> List[str]:
        """Extract experience information from text"""
        # Look for company names
        companies = re.findall(r'([A-Z][a-zA-Z\s&]+(?:Inc|Corp|LLC|Ltd|Company|Technologies|Systems))', text)
        return companies[:5]
    
    def _extract_education_from_text(self, text: str) -> List[str]:
        """Extract education information from text"""
        # Look for degree information
        degrees = re.findall(r'(?i)(bachelor|master|phd|mba|bs|ms|phd)\s+[a-zA-Z\s]+', text)
        return degrees[:3]
    
    def _extract_contact_from_text(self, text: str) -> List[str]:
        """Extract contact information from text"""
        contact_info = []
        
        # Email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if email_match:
            contact_info.append(f"Email: {email_match.group()}")
        
        # Phone
        phone_match = re.search(r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})', text)
        if phone_match:
            contact_info.append(f"Phone: {phone_match.group()}")
        
        return contact_info
    
    def _extract_snippets(self, query: str, content: str) -> List[str]:
        """Extract relevant snippets from content based on query"""
        # Simple snippet extraction - look for sentences containing query words
        query_words = query.lower().split()
        sentences = re.split(r'[.!?]+', content)
        
        relevant_snippets = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(word in sentence_lower for word in query_words):
                # Clean and truncate snippet
                snippet = sentence.strip()[:200]  # Limit to 200 chars
                if len(snippet) > 50:  # Only include substantial snippets
                    relevant_snippets.append(snippet)
        
        return relevant_snippets[:3]  # Return top 3 snippets
