import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (data) => api.post('/api/login', data),
  register: (data) => api.post('/api/register', data),
};

// Resume API
export const resumeAPI = {
  upload: (file, idempotencyKey) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const headers = {};
    if (idempotencyKey) {
      headers['Idempotency-Key'] = idempotencyKey;
    }
    
    return api.post('/api/resumes', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        ...headers,
      },
    });
  },
  getAll: (params) => api.get('/api/resumes', { params }),
  getById: (id) => api.get(`/api/resumes/${id}`),
};

// Job API
export const jobAPI = {
  create: (data, idempotencyKey) => {
    const headers = {};
    if (idempotencyKey) {
      headers['Idempotency-Key'] = idempotencyKey;
    }
    
    return api.post('/api/jobs', data, { headers });
  },
  getById: (id) => api.get(`/api/jobs/${id}`),
  match: (jobId, data) => api.post(`/api/jobs/${jobId}/match`, data),
};

// RAG API
export const ragAPI = {
  ask: (data) => api.post('/api/ask', data),
};

export default api;
