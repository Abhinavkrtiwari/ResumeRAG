from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

from models import User
from schemas import UserCreate, LoginRequest, UserResponse

load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthService:
    def __init__(self):
        self.pwd_context = pwd_context
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str, db: Session) -> Optional[User]:
        """Verify a JWT token and return the user"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = payload.get("sub")
            if user_id is None:
                return None
        except JWTError:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        return user
    
    def register(self, user_create: UserCreate, db: Session) -> UserResponse:
        """Register a new user"""
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == user_create.email) | (User.username == user_create.username)
        ).first()
        
        if existing_user:
            if existing_user.email == user_create.email:
                raise ValueError("Email already registered")
            else:
                raise ValueError("Username already taken")
        
        # Create new user
        hashed_password = self.get_password_hash(user_create.password)
        db_user = User(
            email=user_create.email,
            username=user_create.username,
            hashed_password=hashed_password,
            is_recruiter=user_create.is_recruiter
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return UserResponse.from_orm(db_user)
    
    def login(self, login_request: LoginRequest, db: Session) -> str:
        """Login user and return JWT token"""
        # Find user by email
        user = db.query(User).filter(User.email == login_request.email).first()
        
        if not user or not self.verify_password(login_request.password, user.hashed_password):
            raise ValueError("Invalid email or password")
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        return access_token
