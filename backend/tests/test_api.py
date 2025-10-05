import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import get_db, Base
from models import User
from services.auth_service import AuthService

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(setup_database):
    auth_service = AuthService()
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "is_recruiter": False
    }
    
    # Create user
    response = client.post("/api/register", json=user_data)
    assert response.status_code == 200
    
    # Login to get token
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/api/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"token": token, "user_data": user_data}

@pytest.fixture
def recruiter_user(setup_database):
    user_data = {
        "email": "recruiter@example.com",
        "username": "recruiter",
        "password": "testpassword123",
        "is_recruiter": True
    }
    
    # Create recruiter user
    response = client.post("/api/register", json=user_data)
    assert response.status_code == 200
    
    # Login to get token
    login_data = {
        "email": "recruiter@example.com",
        "password": "testpassword123"
    }
    response = client.post("/api/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"token": token, "user_data": user_data}

class TestAuth:
    def test_register_user(self, setup_database):
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "is_recruiter": False
        }
        
        response = client.post("/api/register", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["is_recruiter"] == user_data["is_recruiter"]
        assert "id" in data
    
    def test_register_duplicate_email(self, setup_database):
        user_data = {
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "password123",
            "is_recruiter": False
        }
        
        # First registration
        response = client.post("/api/register", json=user_data)
        assert response.status_code == 200
        
        # Second registration with same email
        user_data["username"] = "user2"
        response = client.post("/api/register", json=user_data)
        assert response.status_code == 400
    
    def test_login_success(self, setup_database):
        # Register user first
        user_data = {
            "email": "login@example.com",
            "username": "loginuser",
            "password": "password123",
            "is_recruiter": False
        }
        client.post("/api/register", json=user_data)
        
        # Login
        login_data = {
            "email": "login@example.com",
            "password": "password123"
        }
        response = client.post("/api/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, setup_database):
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/api/login", json=login_data)
        assert response.status_code == 401

class TestResumes:
    def test_upload_resume(self, test_user):
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        # Create a test file
        test_content = "John Doe\nSoftware Engineer\nPython, JavaScript, React\njohn.doe@example.com"
        files = {"file": ("test_resume.txt", test_content, "text/plain")}
        
        response = client.post("/api/resumes", files=files, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["original_filename"] == "test_resume.txt"
        assert "id" in data
        assert data["content"] == test_content
    
    def test_get_resumes(self, test_user):
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        response = client.get("/api/resumes", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "next_offset" in data
        assert isinstance(data["items"], list)
    
    def test_get_resume_by_id(self, test_user):
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        # First upload a resume
        test_content = "Jane Smith\nData Scientist\nPython, Machine Learning\njane.smith@example.com"
        files = {"file": ("jane_resume.txt", test_content, "text/plain")}
        upload_response = client.post("/api/resumes", files=files, headers=headers)
        assert upload_response.status_code == 200
        
        resume_id = upload_response.json()["id"]
        
        # Get the resume by ID
        response = client.get(f"/api/resumes/{resume_id}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == resume_id
        assert data["content"] == test_content
    
    def test_pii_redaction_regular_user(self, test_user):
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        # Upload resume with PII
        test_content = "John Doe\nSoftware Engineer\njohn.doe@example.com\n+1-555-123-4567"
        files = {"file": ("pii_resume.txt", test_content, "text/plain")}
        upload_response = client.post("/api/resumes", files=files, headers=headers)
        assert upload_response.status_code == 200
        
        resume_id = upload_response.json()["id"]
        
        # Get the resume - PII should be redacted
        response = client.get(f"/api/resumes/{resume_id}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "[EMAIL_REDACTED]" in data["content"]
        assert "[PHONE_REDACTED]" in data["content"]
    
    def test_pii_visible_recruiter(self, recruiter_user):
        headers = {"Authorization": f"Bearer {recruiter_user['token']}"}
        
        # Upload resume with PII
        test_content = "John Doe\nSoftware Engineer\njohn.doe@example.com\n+1-555-123-4567"
        files = {"file": ("pii_resume.txt", test_content, "text/plain")}
        upload_response = client.post("/api/resumes", files=files, headers=headers)
        assert upload_response.status_code == 200
        
        resume_id = upload_response.json()["id"]
        
        # Get the resume - PII should be visible for recruiters
        response = client.get(f"/api/resumes/{resume_id}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "john.doe@example.com" in data["content"]
        assert "+1-555-123-4567" in data["content"]

class TestJobs:
    def test_create_job(self, test_user):
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        job_data = {
            "title": "Software Engineer",
            "description": "We are looking for a software engineer",
            "requirements": ["Python", "JavaScript", "3+ years experience"],
            "company": "TechCorp",
            "location": "San Francisco, CA",
            "salary_min": 100000,
            "salary_max": 150000
        }
        
        response = client.post("/api/jobs", json=job_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == job_data["title"]
        assert data["company"] == job_data["company"]
        assert data["requirements"] == job_data["requirements"]
    
    def test_get_job_by_id(self, test_user):
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        # Create a job first
        job_data = {
            "title": "Data Scientist",
            "description": "Looking for a data scientist",
            "requirements": ["Python", "Machine Learning"],
            "company": "DataCorp"
        }
        create_response = client.post("/api/jobs", json=job_data, headers=headers)
        assert create_response.status_code == 200
        
        job_id = create_response.json()["id"]
        
        # Get the job by ID
        response = client.get(f"/api/jobs/{job_id}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == job_id
        assert data["title"] == job_data["title"]

class TestRAG:
    def test_ask_question(self, test_user):
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        # First upload a resume
        test_content = "John Doe\nSoftware Engineer\nPython, JavaScript, React\n5 years experience"
        files = {"file": ("test_resume.txt", test_content, "text/plain")}
        upload_response = client.post("/api/resumes", files=files, headers=headers)
        assert upload_response.status_code == 200
        
        # Ask a question
        ask_data = {
            "query": "What skills does the candidate have?",
            "k": 3
        }
        
        response = client.post("/api/ask", json=ask_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert isinstance(data["sources"], list)

class TestMatching:
    def test_match_candidates(self, test_user):
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        # First upload a resume
        test_content = "John Doe\nSoftware Engineer\nPython, JavaScript, React\n5 years experience"
        files = {"file": ("test_resume.txt", test_content, "text/plain")}
        upload_response = client.post("/api/resumes", files=files, headers=headers)
        assert upload_response.status_code == 200
        
        # Create a job
        job_data = {
            "title": "Software Engineer",
            "description": "Looking for a software engineer with Python experience",
            "requirements": ["Python", "JavaScript", "3+ years experience"],
            "company": "TechCorp"
        }
        job_response = client.post("/api/jobs", json=job_data, headers=headers)
        assert job_response.status_code == 200
        
        job_id = job_response.json()["id"]
        
        # Match candidates
        match_data = {"top_n": 5}
        response = client.post(f"/api/jobs/{job_id}/match", json=match_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "matches" in data
        assert isinstance(data["matches"], list)

class TestRateLimiting:
    def test_rate_limit_exceeded(self, test_user):
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        # Make many requests quickly to trigger rate limit
        for i in range(65):  # Exceed 60 req/min limit
            response = client.get("/api/resumes", headers=headers)
            if response.status_code == 429:
                break
        
        # Should eventually get rate limited
        assert response.status_code == 429
        data = response.json()
        assert data["error"]["code"] == "RATE_LIMIT"

class TestIdempotency:
    def test_idempotent_resume_upload(self, test_user):
        headers = {
            "Authorization": f"Bearer {test_user['token']}",
            "Idempotency-Key": "test-key-123"
        }
        
        test_content = "Test Resume Content"
        files = {"file": ("test.txt", test_content, "text/plain")}
        
        # First upload
        response1 = client.post("/api/resumes", files=files, headers=headers)
        assert response1.status_code == 200
        
        # Second upload with same idempotency key
        response2 = client.post("/api/resumes", files=files, headers=headers)
        assert response2.status_code == 200
        
        # Should return the same resume
        assert response1.json()["id"] == response2.json()["id"]
    
    def test_idempotent_job_creation(self, test_user):
        headers = {
            "Authorization": f"Bearer {test_user['token']}",
            "Idempotency-Key": "job-key-456"
        }
        
        job_data = {
            "title": "Test Job",
            "description": "Test description",
            "requirements": ["Python"],
            "company": "TestCorp"
        }
        
        # First creation
        response1 = client.post("/api/jobs", json=job_data, headers=headers)
        assert response1.status_code == 200
        
        # Second creation with same idempotency key
        response2 = client.post("/api/jobs", json=job_data, headers=headers)
        assert response2.status_code == 200
        
        # Should return the same job
        assert response1.json()["id"] == response2.json()["id"]
