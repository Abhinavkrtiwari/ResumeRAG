import os
import zipfile
import tempfile
from typing import Tuple, Dict, Any
import PyPDF2
from docx import Document
import re

class FileProcessingService:
    def __init__(self):
        self.upload_dir = "uploads"
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def save_file(self, file) -> str:
        """Save uploaded file to disk"""
        # Generate unique filename
        filename = f"{file.filename}_{os.urandom(8).hex()}"
        file_path = os.path.join(self.upload_dir, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return file_path
    
    async def process_resume_file(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Process a resume file and extract content and metadata"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return await self._process_pdf(file_path)
        elif file_ext == '.docx':
            return await self._process_docx(file_path)
        elif file_ext == '.txt':
            return await self._process_txt(file_path)
        elif file_ext == '.zip':
            return await self._process_zip(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    async def _process_pdf(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Process PDF file"""
        content = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
        
        metadata = self._extract_metadata(content)
        return content, metadata
    
    async def _process_docx(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Process DOCX file"""
        doc = Document(file_path)
        content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        metadata = self._extract_metadata(content)
        return content, metadata
    
    async def _process_txt(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Process TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        metadata = self._extract_metadata(content)
        return content, metadata
    
    async def _process_zip(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Process ZIP file containing multiple resumes"""
        all_content = []
        all_metadata = []
        
        with zipfile.ZipFile(file_path, 'r') as zip_file:
            for file_info in zip_file.filelist:
                if not file_info.is_dir():
                    # Extract file
                    with zip_file.open(file_info.filename) as file:
                        # Create temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_info.filename)[1]) as temp_file:
                            temp_file.write(file.read())
                            temp_file_path = temp_file.name
                    
                    try:
                        # Process the extracted file
                        content, metadata = await self.process_resume_file(temp_file_path)
                        all_content.append(f"=== {file_info.filename} ===\n{content}\n")
                        all_metadata.append(metadata)
                    finally:
                        # Clean up temporary file
                        os.unlink(temp_file_path)
        
        combined_content = "\n".join(all_content)
        combined_metadata = {
            "type": "zip",
            "file_count": len(all_content),
            "files": all_metadata
        }
        
        return combined_content, combined_metadata
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from resume content"""
        metadata = {
            "skills": self._extract_skills(content),
            "experience": self._extract_experience(content),
            "education": self._extract_education(content),
            "contact_info": self._extract_contact_info(content)
        }
        return metadata
    
    def _extract_skills(self, content: str) -> list:
        """Extract skills from resume content"""
        # Common skills keywords
        skills_keywords = [
            'python', 'javascript', 'java', 'react', 'node.js', 'sql', 'aws', 'docker',
            'kubernetes', 'git', 'html', 'css', 'typescript', 'angular', 'vue', 'django',
            'flask', 'fastapi', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'machine learning', 'ai', 'data science', 'analytics', 'project management',
            'agile', 'scrum', 'leadership', 'communication', 'problem solving'
        ]
        
        found_skills = []
        content_lower = content.lower()
        
        for skill in skills_keywords:
            if skill in content_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _extract_experience(self, content: str) -> list:
        """Extract work experience from resume content"""
        # Simple regex to find experience sections
        experience_pattern = r'(?i)(experience|work history|employment|career)'
        experience_section = re.search(experience_pattern, content)
        
        if experience_section:
            # Extract text after experience section
            start_pos = experience_section.end()
            experience_text = content[start_pos:start_pos + 1000]  # Get next 1000 chars
            
            # Look for company names and job titles
            companies = re.findall(r'([A-Z][a-zA-Z\s&]+(?:Inc|Corp|LLC|Ltd|Company|Technologies|Systems))', experience_text)
            return companies[:5]  # Return top 5 companies
        
        return []
    
    def _extract_education(self, content: str) -> list:
        """Extract education information from resume content"""
        education_pattern = r'(?i)(education|academic|degree|university|college|bachelor|master|phd)'
        education_section = re.search(education_pattern, content)
        
        if education_section:
            start_pos = education_section.end()
            education_text = content[start_pos:start_pos + 500]  # Get next 500 chars
            
            # Look for degree information
            degrees = re.findall(r'(?i)(bachelor|master|phd|mba|bs|ms|phd)\s+[a-zA-Z\s]+', education_text)
            return degrees[:3]  # Return top 3 degrees
        
        return []
    
    def _extract_contact_info(self, content: str) -> Dict[str, str]:
        """Extract contact information from resume content"""
        contact_info = {}
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, content)
        if email_match:
            contact_info['email'] = email_match.group()
        
        # Phone
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phone_match = re.search(phone_pattern, content)
        if phone_match:
            contact_info['phone'] = phone_match.group()
        
        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[a-zA-Z0-9-]+'
        linkedin_match = re.search(linkedin_pattern, content)
        if linkedin_match:
            contact_info['linkedin'] = linkedin_match.group()
        
        return contact_info
