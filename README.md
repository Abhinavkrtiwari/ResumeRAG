# ResumeRAG - Resume Search & Job Match Platform

A full-stack application that allows users to upload resumes, search through them using natural language queries, and match candidates against job descriptions using AI-powered RAG (Retrieval-Augmented Generation) technology.

## 🚀 Features

- **Resume Upload**: Support for PDF, DOCX, TXT, and ZIP files
- **AI-Powered Search**: Ask natural language questions about uploaded resumes
- **Smart Job Matching**: Match candidates against job requirements with evidence
- **PII Protection**: Automatic redaction of personal information (unless user is a recruiter)
- **Rate Limiting**: 60 requests per minute per user
- **Idempotency**: Support for idempotent operations
- **Authentication**: JWT-based authentication with role-based access

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Primary database
- **Redis**: Rate limiting and caching
- **Sentence Transformers**: Text embeddings
- **PyPDF2**: PDF processing
- **python-docx**: DOCX processing

### Frontend
- **React**: User interface framework
- **Tailwind CSS**: Styling
- **React Query**: Data fetching and caching
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **React Hook Form**: Form handling

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL
- Redis

## 🚀 Quick Start

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd skillvision
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Update `.env` with your configuration:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/resumerag
   REDIS_HOST=localhost
   REDIS_PORT=6379
   SECRET_KEY=your-secret-key-here
   ```

4. **Set up the database**
   ```bash
   # Create database
   createdb resumerag
   
   # Run migrations (if using Alembic)
   alembic upgrade head
   ```

5. **Seed sample data**
   ```bash
   python backend/seed_data.py
   ```

6. **Start the backend server**
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Install Node.js dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server**
   ```bash
   npm start
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "is_recruiter": false
}
```

#### Login
```http
POST /api/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Resume Endpoints

#### Upload Resume
```http
POST /api/resumes
Authorization: Bearer <token>
Content-Type: multipart/form-data
Idempotency-Key: <optional-key>

file: <resume-file>
```

#### Get Resumes (Paginated)
```http
GET /api/resumes?limit=10&offset=0&q=search_query
Authorization: Bearer <token>
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "filename": "resume.pdf",
      "original_filename": "john_doe_resume.pdf",
      "file_size": 1024,
      "content": "Resume content...",
      "metadata": {
        "skills": ["Python", "JavaScript"],
        "experience": ["TechCorp Inc"],
        "education": ["Bachelor of Science"],
        "contact_info": {
          "email": "john@example.com",
          "phone": "+1-555-123-4567"
        }
      },
      "owner_id": 1,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "next_offset": 10,
  "total": 25
}
```

#### Get Resume by ID
```http
GET /api/resumes/{id}
Authorization: Bearer <token>
```

### Job Endpoints

#### Create Job
```http
POST /api/jobs
Authorization: Bearer <token>
Content-Type: application/json
Idempotency-Key: <optional-key>

{
  "title": "Software Engineer",
  "description": "We are looking for a software engineer...",
  "requirements": ["Python", "JavaScript", "3+ years experience"],
  "company": "TechCorp",
  "location": "San Francisco, CA",
  "salary_min": 100000,
  "salary_max": 150000
}
```

#### Get Job by ID
```http
GET /api/jobs/{id}
Authorization: Bearer <token>
```

### RAG Endpoints

#### Ask Question
```http
POST /api/ask
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "What skills do the candidates have?",
  "k": 5
}
```

**Response:**
```json
{
  "answer": "Based on the uploaded resumes, I found these skills: Python, JavaScript, React, Django, PostgreSQL...",
  "sources": [
    {
      "resume_id": 1,
      "filename": "john_doe_resume.pdf",
      "similarity_score": 0.85,
      "snippets": [
        "Python, JavaScript, React, Django, PostgreSQL",
        "5+ years of experience in software development"
      ]
    }
  ]
}
```

### Matching Endpoints

#### Match Candidates
```http
POST /api/jobs/{job_id}/match
Authorization: Bearer <token>
Content-Type: application/json

{
  "top_n": 10
}
```

**Response:**
```json
{
  "matches": [
    {
      "resume_id": 1,
      "filename": "john_doe_resume.pdf",
      "score": 0.92,
      "evidence": [
        {
          "requirement": "Python",
          "evidence": "5+ years of Python development experience",
          "type": "skill_match"
        }
      ],
      "missing_requirements": ["AWS certification"]
    }
  ]
}
```

## 🔒 Security Features

### Rate Limiting
- 60 requests per minute per user
- Returns `429` status with `{"error": {"code": "RATE_LIMIT"}}` when exceeded

### PII Redaction
- Personal information is automatically redacted for regular users
- Recruiters can see full information
- Redacted fields include: email, phone, SSN, addresses, LinkedIn profiles

### Idempotency
- All POST endpoints support `Idempotency-Key` header
- Prevents duplicate operations

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Test Coverage
- Authentication (register, login)
- Resume upload and retrieval
- Job creation and matching
- RAG functionality
- PII redaction
- Rate limiting
- Idempotency

## 📊 Sample Data

The application comes with pre-loaded sample data:

### Test Users
- **Admin/Recruiter**: `admin@example.com` / `password123`
- **Regular User**: `user@example.com` / `password123`

### Sample Resumes
- John Doe - Software Engineer (Python, JavaScript, React)
- Jane Smith - Data Scientist (Python, Machine Learning, TensorFlow)
- Mike Johnson - Frontend Developer (React, TypeScript, Vue.js)

### Sample Jobs
- Senior Python Developer at TechCorp Inc
- Data Scientist at DataCorp
- Frontend React Developer at WebSolutions LLC

## 🚀 Deployment

### Backend Deployment
1. Set up PostgreSQL and Redis on your server
2. Configure environment variables
3. Run database migrations
4. Deploy using Docker or directly with uvicorn

### Frontend Deployment
1. Build the React application: `npm run build`
2. Deploy the `build` folder to your hosting service
3. Configure API URL in environment variables

## 📝 API Error Format

All API errors follow a consistent format:

```json
{
  "error": {
    "code": "FIELD_REQUIRED",
    "field": "email",
    "message": "Email is required"
  }
}
```

### Common Error Codes
- `FIELD_REQUIRED`: Required field is missing
- `RATE_LIMIT`: Rate limit exceeded
- `INVALID_CREDENTIALS`: Invalid login credentials
- `DUPLICATE_EMAIL`: Email already registered
- `FILE_TOO_LARGE`: Uploaded file exceeds size limit
- `UNSUPPORTED_FILE_TYPE`: File type not supported

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the test cases for usage examples

## 🔮 Future Enhancements

- [ ] Advanced search filters
- [ ] Resume parsing improvements
- [ ] Integration with job boards
- [ ] Email notifications
- [ ] Analytics dashboard
- [ ] Multi-language support
- [ ] Mobile app
- [ ] Advanced matching algorithms
