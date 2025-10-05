import re
from typing import Dict, Any, List
from models import User

class PIIService:
    def __init__(self):
        # Common PII patterns
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'address': r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)',
            'linkedin': r'linkedin\.com/in/[a-zA-Z0-9-]+',
            'github': r'github\.com/[a-zA-Z0-9-]+',
            'personal_website': r'https?://(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?'
        }
        
        # Replacement patterns
        self.replacements = {
            'email': '[EMAIL_REDACTED]',
            'phone': '[PHONE_REDACTED]',
            'ssn': '[SSN_REDACTED]',
            'credit_card': '[CARD_REDACTED]',
            'address': '[ADDRESS_REDACTED]',
            'linkedin': '[LINKEDIN_REDACTED]',
            'github': '[GITHUB_REDACTED]',
            'personal_website': '[WEBSITE_REDACTED]'
        }
    
    def redact_pii(self, text: str, user: User) -> str:
        """Redact PII from text unless user is a recruiter"""
        if user.is_recruiter:
            return text
        
        redacted_text = text
        
        for pii_type, pattern in self.pii_patterns.items():
            replacement = self.replacements.get(pii_type, f'[{pii_type.upper()}_REDACTED]')
            redacted_text = re.sub(pattern, replacement, redacted_text, flags=re.IGNORECASE)
        
        return redacted_text
    
    def redact_metadata(self, metadata: Dict[str, Any], user: User) -> Dict[str, Any]:
        """Redact PII from metadata unless user is a recruiter"""
        if user.is_recruiter:
            return metadata
        
        redacted_metadata = metadata.copy()
        
        # Redact contact information
        if 'contact_info' in redacted_metadata:
            contact_info = redacted_metadata['contact_info'].copy()
            
            # Redact specific fields
            if 'email' in contact_info:
                contact_info['email'] = '[EMAIL_REDACTED]'
            if 'phone' in contact_info:
                contact_info['phone'] = '[PHONE_REDACTED]'
            if 'linkedin' in contact_info:
                contact_info['linkedin'] = '[LINKEDIN_REDACTED]'
            
            redacted_metadata['contact_info'] = contact_info
        
        return redacted_metadata
    
    def extract_pii_summary(self, text: str) -> Dict[str, List[str]]:
        """Extract PII information for summary (without revealing actual values)"""
        pii_summary = {}
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            if matches:
                pii_summary[pii_type] = [f"{pii_type.title()} found" for _ in matches]
        
        return pii_summary
    
    def get_redaction_status(self, user: User) -> Dict[str, Any]:
        """Get information about PII redaction status for the user"""
        return {
            'pii_redacted': not user.is_recruiter,
            'user_type': 'recruiter' if user.is_recruiter else 'regular_user',
            'message': 'PII is visible' if user.is_recruiter else 'PII has been redacted for privacy'
        }
