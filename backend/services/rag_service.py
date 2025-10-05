from sqlalchemy.orm import Session
from typing import List, Dict, Any
import re

from models import Resume
from schemas import AskResponse
from services.embedding_service import EmbeddingService

class RAGService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
    
    async def ask_question(self, query: str, k: int, user_id: int, db: Session) -> AskResponse:
        """Answer a question about resumes using RAG"""
        # Generate query embedding
        query_embedding = self.embedding_service.generate_embeddings(query)
        
        # Get all resumes for the user
        resumes = db.query(Resume).filter(Resume.owner_id == user_id).all()
        
        if not resumes:
            return AskResponse(
                answer="No resumes found. Please upload some resumes first.",
                sources=[]
            )
        
        # Prepare documents for similarity search
        documents = []
        for resume in resumes:
            if resume.embeddings:
                documents.append({
                    'id': resume.id,
                    'content': resume.content,
                    'filename': resume.original_filename,
                    'embeddings': resume.embeddings
                })
        
        # Find similar documents
        similar_docs = self.embedding_service.find_similar_documents(
            query_embedding, documents, top_k=k
        )
        
        # Generate answer based on similar documents
        answer = self._generate_answer(query, similar_docs)
        
        # Prepare sources
        sources = []
        for doc_info in similar_docs:
            doc = doc_info['document']
            similarity = doc_info['similarity']
            
            # Extract relevant snippets
            snippets = self._extract_relevant_snippets(query, doc['content'])
            
            sources.append({
                'resume_id': doc['id'],
                'filename': doc['filename'],
                'similarity_score': similarity,
                'snippets': snippets
            })
        
        return AskResponse(
            answer=answer,
            sources=sources
        )
    
    def _generate_answer(self, query: str, similar_docs: List[Dict[str, Any]]) -> str:
        """Generate an answer based on similar documents"""
        if not similar_docs:
            return "I couldn't find relevant information in the uploaded resumes."
        
        # Simple answer generation based on query type
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['skill', 'skills', 'technology', 'technologies']):
            return self._generate_skills_answer(similar_docs)
        elif any(word in query_lower for word in ['experience', 'work', 'job', 'career']):
            return self._generate_experience_answer(similar_docs)
        elif any(word in query_lower for word in ['education', 'degree', 'university', 'college']):
            return self._generate_education_answer(similar_docs)
        elif any(word in query_lower for word in ['contact', 'email', 'phone', 'linkedin']):
            return self._generate_contact_answer(similar_docs)
        else:
            return self._generate_general_answer(query, similar_docs)
    
    def _generate_skills_answer(self, similar_docs: List[Dict[str, Any]]) -> str:
        """Generate answer about skills"""
        all_skills = set()
        
        for doc_info in similar_docs:
            doc = doc_info['document']
            content = doc['content'].lower()
            
            # Extract skills from content
            skills = self._extract_skills_from_text(content)
            all_skills.update(skills)
        
        if all_skills:
            skills_list = list(all_skills)[:10]  # Top 10 skills
            return f"Based on the uploaded resumes, I found these skills: {', '.join(skills_list)}."
        else:
            return "I couldn't find specific skills mentioned in the resumes."
    
    def _generate_experience_answer(self, similar_docs: List[Dict[str, Any]]) -> str:
        """Generate answer about work experience"""
        experiences = []
        
        for doc_info in similar_docs:
            doc = doc_info['document']
            content = doc['content']
            
            # Extract experience information
            exp_info = self._extract_experience_from_text(content)
            if exp_info:
                experiences.extend(exp_info)
        
        if experiences:
            return f"Based on the resumes, I found work experience at: {', '.join(experiences[:5])}."
        else:
            return "I couldn't find specific work experience details in the resumes."
    
    def _generate_education_answer(self, similar_docs: List[Dict[str, Any]]) -> str:
        """Generate answer about education"""
        education_info = []
        
        for doc_info in similar_docs:
            doc = doc_info['document']
            content = doc['content']
            
            # Extract education information
            edu_info = self._extract_education_from_text(content)
            if edu_info:
                education_info.extend(edu_info)
        
        if education_info:
            return f"Based on the resumes, I found education information: {', '.join(education_info[:3])}."
        else:
            return "I couldn't find specific education details in the resumes."
    
    def _generate_contact_answer(self, similar_docs: List[Dict[str, Any]]) -> str:
        """Generate answer about contact information"""
        contact_info = []
        
        for doc_info in similar_docs:
            doc = doc_info['document']
            content = doc['content']
            
            # Extract contact information
            contact = self._extract_contact_from_text(content)
            if contact:
                contact_info.extend(contact)
        
        if contact_info:
            return f"Based on the resumes, I found contact information: {', '.join(contact_info[:3])}."
        else:
            return "I couldn't find specific contact information in the resumes."
    
    def _generate_general_answer(self, query: str, similar_docs: List[Dict[str, Any]]) -> str:
        """Generate a general answer based on query and similar documents"""
        if not similar_docs:
            return "I couldn't find relevant information to answer your question."
        
        # Get the most relevant document
        most_relevant = similar_docs[0]
        content = most_relevant['document']['content']
        
        # Extract relevant snippets
        snippets = self._extract_relevant_snippets(query, content)
        
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
    
    def _extract_relevant_snippets(self, query: str, content: str) -> List[str]:
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
