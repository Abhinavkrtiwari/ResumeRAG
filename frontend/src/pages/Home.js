import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Upload, Search, Briefcase, Brain, Users, Target } from 'lucide-react';

const Home = () => {
  const { user } = useAuth();

  const features = [
    {
      icon: <Upload className="h-8 w-8 text-primary-600" />,
      title: 'Upload Resumes',
      description: 'Upload multiple resumes in PDF, DOCX, or ZIP format for processing and analysis.',
    },
    {
      icon: <Brain className="h-8 w-8 text-primary-600" />,
      title: 'AI-Powered Search',
      description: 'Ask questions about your resumes using natural language and get intelligent answers.',
    },
    {
      icon: <Target className="h-8 w-8 text-primary-600" />,
      title: 'Smart Matching',
      description: 'Match candidates against job descriptions with evidence and missing requirements.',
    },
    {
      icon: <Users className="h-8 w-8 text-primary-600" />,
      title: 'Candidate Management',
      description: 'View detailed candidate profiles and track their information efficiently.',
    },
  ];

  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <div className="text-center py-16">
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
          ResumeRAG
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          The intelligent resume search and job matching platform powered by AI. 
          Upload resumes, ask questions, and find the perfect candidates for your jobs.
        </p>
        
        {user ? (
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/upload"
              className="bg-primary-600 text-white px-8 py-3 rounded-lg hover:bg-primary-700 transition-colors inline-flex items-center justify-center space-x-2"
            >
              <Upload className="h-5 w-5" />
              <span>Upload Resumes</span>
            </Link>
            <Link
              to="/search"
              className="bg-white text-primary-600 border border-primary-600 px-8 py-3 rounded-lg hover:bg-primary-50 transition-colors inline-flex items-center justify-center space-x-2"
            >
              <Search className="h-5 w-5" />
              <span>Search Resumes</span>
            </Link>
          </div>
        ) : (
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="bg-primary-600 text-white px-8 py-3 rounded-lg hover:bg-primary-700 transition-colors"
            >
              Get Started
            </Link>
            <Link
              to="/login"
              className="bg-white text-primary-600 border border-primary-600 px-8 py-3 rounded-lg hover:bg-primary-50 transition-colors"
            >
              Login
            </Link>
          </div>
        )}
      </div>

      {/* Features Section */}
      <div className="py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Key Features
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
              <div className="mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* How it Works Section */}
      <div className="py-16 bg-gray-50 rounded-lg">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          How It Works
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-primary-600">1</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Upload Resumes
            </h3>
            <p className="text-gray-600">
              Upload your resumes in various formats. Our system processes and extracts key information automatically.
            </p>
          </div>
          <div className="text-center">
            <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-primary-600">2</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Ask Questions
            </h3>
            <p className="text-gray-600">
              Use natural language to ask questions about your resumes. Get intelligent answers with source citations.
            </p>
          </div>
          <div className="text-center">
            <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-primary-600">3</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Match Candidates
            </h3>
            <p className="text-gray-600">
              Create job postings and get intelligent candidate matches with evidence and missing requirements.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
