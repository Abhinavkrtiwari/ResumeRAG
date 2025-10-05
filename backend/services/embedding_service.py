from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any
import json

class EmbeddingService:
    def __init__(self):
        # Initialize the sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for a given text"""
        # Clean and preprocess text
        cleaned_text = self._clean_text(text)
        
        # Generate embeddings
        embeddings = self.model.encode(cleaned_text)
        
        # Convert to list for JSON serialization
        return embeddings.tolist()
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        cleaned_texts = [self._clean_text(text) for text in texts]
        embeddings = self.model.encode(cleaned_texts)
        return [emb.tolist() for emb in embeddings]
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        # Convert to numpy arrays
        emb1 = np.array(embedding1)
        emb2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
    
    def find_similar_documents(self, query_embedding: List[float], document_embeddings: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """Find most similar documents to a query embedding"""
        similarities = []
        
        for doc in document_embeddings:
            if 'embeddings' in doc and doc['embeddings']:
                similarity = self.calculate_similarity(query_embedding, doc['embeddings'])
                similarities.append({
                    'document': doc,
                    'similarity': similarity
                })
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities[:top_k]
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text for embedding"""
        import re
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep alphanumeric and basic punctuation
        text = re.sub(r'[^\w\s.,!?;:-]', '', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove very short words
        words = text.split()
        words = [word for word in words if len(word) > 2]
        
        return ' '.join(words)
