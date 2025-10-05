from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
import redis
import os
from dotenv import load_dotenv

load_dotenv()

# Redis connection for rate limiting
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

class RateLimitMiddleware:
    def __init__(self, app):
        self.app = app
        self.redis_client = redis_client
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Get user identifier (IP address or user ID if authenticated)
            user_id = self._get_user_identifier(request)
            
            # Check rate limit
            if not self._check_rate_limit(user_id):
                response = HTTPException(
                    status_code=429,
                    detail={"error": {"code": "RATE_LIMIT", "message": "Rate limit exceeded"}}
                )
                await response(scope, receive, send)
                return
        
        await self.app(scope, receive, send)
    
    def _get_user_identifier(self, request: Request) -> str:
        """Get user identifier for rate limiting"""
        # Try to get user ID from JWT token if available
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # In a real implementation, you would decode the JWT to get user ID
            # For now, we'll use the IP address
            pass
        
        # Fall back to IP address
        return get_remote_address(request)
    
    def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user has exceeded rate limit"""
        current_time = int(time.time())
        window_start = current_time - 60  # 1 minute window
        
        # Clean old entries
        self.redis_client.zremrangebyscore(f"rate_limit:{user_id}", 0, window_start)
        
        # Count current requests
        current_requests = self.redis_client.zcard(f"rate_limit:{user_id}")
        
        if current_requests >= 60:  # 60 requests per minute
            return False
        
        # Add current request
        self.redis_client.zadd(f"rate_limit:{user_id}", {str(current_time): current_time})
        self.redis_client.expire(f"rate_limit:{user_id}", 60)
        
        return True
