from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User, Resume, Job
from services.auth_service import AuthService
import os

def create_sample_data():
    """Create sample data for Render deployment"""
    db = SessionLocal()
    auth_service = AuthService()
    
    try:
        # Create sample users
        users_data = [
            {
                "email": "admin@example.com",
                "username": "admin",
                "password": "password123",
                "is_recruiter": True
            },
            {
                "email": "user@example.com",
                "username": "user",
                "password": "password123",
                "is_recruiter": False
            }
        ]
        
        created_users = []
        for user_data in users_data:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing_user:
                hashed_password = auth_service.get_password_hash(user_data["password"])
                user = User(
                    email=user_data["email"],
                    username=user_data["username"],
                    hashed_password=hashed_password,
                    is_recruiter=user_data["is_recruiter"]
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                created_users.append(user)
                print(f"Created user: {user.email}")
            else:
                created_users.append(existing_user)
                print(f"User already exists: {existing_user.email}")
        
        # Create sample resumes
        resumes_data = [
            {
                "filename": "john_doe_resume.txt",
                "original_filename": "john_doe_resume.txt",
                "file_path": "uploads/john_doe_resume.txt",
                "file_size": 1024,
                "content": """John Doe
Software Engineer
john.doe@example.com
+1-555-123-4567

EXPERIENCE
Senior Software Engineer | TechCorp Inc | 2020-2024
- Developed scalable web applications using Python, Django, and React
- Led a team of 5 developers on multiple projects
- Implemented CI/CD pipelines using AWS and Docker
- Improved system performance by 40% through optimization

Software Engineer | StartupXYZ | 2018-2020
- Built RESTful APIs using Python and FastAPI
- Worked with PostgreSQL and Redis databases
- Collaborated with frontend team on React applications

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley | 2014-2018

SKILLS
Python, JavaScript, React, Django, FastAPI, PostgreSQL, Redis, AWS, Docker, Git, Agile, Leadership""",
                "owner_id": created_users[0].id
            },
            {
                "filename": "jane_smith_resume.txt",
                "original_filename": "jane_smith_resume.txt",
                "file_path": "uploads/jane_smith_resume.txt",
                "file_size": 1156,
                "content": """Jane Smith
Data Scientist
jane.smith@example.com
+1-555-987-6543

EXPERIENCE
Senior Data Scientist | DataCorp | 2021-2024
- Built machine learning models for predictive analytics
- Led data science initiatives across multiple business units
- Implemented MLOps pipelines using Python, TensorFlow, and Kubernetes
- Achieved 95% accuracy in customer churn prediction

Data Scientist | AnalyticsPro | 2019-2021
- Developed recommendation systems using collaborative filtering
- Analyzed large datasets using Python, Pandas, and Spark
- Created data visualizations using Tableau and D3.js

EDUCATION
Master of Science in Data Science
Stanford University | 2017-2019
Bachelor of Science in Mathematics
University of Washington | 2013-2017

SKILLS
Python, R, SQL, Machine Learning, TensorFlow, PyTorch, Pandas, NumPy, Spark, Tableau, Statistics, Mathematics""",
                "owner_id": created_users[0].id
            }
        ]
        
        for resume_data in resumes_data:
            # Check if resume already exists
            existing_resume = db.query(Resume).filter(
                Resume.original_filename == resume_data["original_filename"]
            ).first()
            
            if not existing_resume:
                resume = Resume(
                    filename=resume_data["filename"],
                    original_filename=resume_data["original_filename"],
                    file_path=resume_data["file_path"],
                    file_size=resume_data["file_size"],
                    content=resume_data["content"],
                    embeddings=None,
                    owner_id=resume_data["owner_id"]
                )
                db.add(resume)
                db.commit()
                db.refresh(resume)
                print(f"Created resume: {resume.original_filename}")
            else:
                print(f"Resume already exists: {existing_resume.original_filename}")
        
        # Create sample jobs
        jobs_data = [
            {
                "title": "Senior Python Developer",
                "description": "We are looking for an experienced Python developer to join our team. You will work on building scalable web applications and APIs using modern technologies.",
                "requirements": ["Python", "Django", "PostgreSQL", "AWS", "5+ years experience", "Leadership skills"],
                "location": "San Francisco, CA",
                "salary_min": 120000,
                "salary_max": 180000,
                "company": "TechCorp Inc",
                "owner_id": created_users[0].id
            },
            {
                "title": "Data Scientist",
                "description": "Join our data science team to build machine learning models and extract insights from large datasets. You will work on cutting-edge AI projects.",
                "requirements": ["Python", "Machine Learning", "TensorFlow", "SQL", "Statistics", "PhD or MS"],
                "location": "Remote",
                "salary_min": 100000,
                "salary_max": 150000,
                "company": "DataCorp",
                "owner_id": created_users[0].id
            }
        ]
        
        for job_data in jobs_data:
            # Check if job already exists
            existing_job = db.query(Job).filter(
                Job.title == job_data["title"],
                Job.company == job_data["company"]
            ).first()
            
            if not existing_job:
                job = Job(
                    title=job_data["title"],
                    description=job_data["description"],
                    requirements=job_data["requirements"],
                    location=job_data["location"],
                    salary_min=job_data["salary_min"],
                    salary_max=job_data["salary_max"],
                    company=job_data["company"],
                    embeddings=None,
                    owner_id=job_data["owner_id"]
                )
                db.add(job)
                db.commit()
                db.refresh(job)
                print(f"Created job: {job.title} at {job.company}")
            else:
                print(f"Job already exists: {existing_job.title} at {existing_job.company}")
        
        print("\nSample data creation completed!")
        print("Test credentials:")
        print("Admin/Recruiter: admin@example.com / password123")
        print("Regular User: user@example.com / password123")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
