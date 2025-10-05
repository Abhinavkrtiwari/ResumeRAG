import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { resumeAPI } from '../services/api';
import { ArrowLeft, File, User, Mail, Phone, MapPin, Calendar, Award, Briefcase, GraduationCap } from 'lucide-react';
import toast from 'react-hot-toast';

const CandidateDetail = () => {
  const { id } = useParams();
  
  const { data: resume, isLoading, error } = useQuery(
    ['resume', id],
    () => resumeAPI.getById(id).then(res => res.data),
    {
      onError: (error) => {
        toast.error('Failed to load candidate details');
      }
    }
  );

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-2 text-gray-500">Loading candidate details...</p>
        </div>
      </div>
    );
  }

  if (error || !resume) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="text-center py-8">
          <File className="mx-auto h-12 w-12 text-gray-300 mb-4" />
          <p className="text-gray-500">Candidate not found</p>
          <Link
            to="/upload"
            className="mt-4 inline-block bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
          >
            Back to Upload
          </Link>
        </div>
      </div>
    );
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link
          to="/upload"
          className="inline-flex items-center space-x-2 text-primary-600 hover:text-primary-700 transition-colors mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Resumes</span>
        </Link>
        
        <div className="flex items-center space-x-3">
          <File className="h-8 w-8 text-primary-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {resume.original_filename}
            </h1>
            <p className="text-gray-500">
              Uploaded on {formatDate(resume.created_at)} • {formatFileSize(resume.file_size)}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Resume Content */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <File className="h-5 w-5" />
              <span>Resume Content</span>
            </h2>
            <div className="prose max-w-none">
              <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed">
                {resume.content}
              </pre>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* File Information */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <File className="h-5 w-5" />
              <span>File Information</span>
            </h3>
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-gray-500">Original Filename</label>
                <p className="text-sm text-gray-900">{resume.original_filename}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">File Size</label>
                <p className="text-sm text-gray-900">{formatFileSize(resume.file_size)}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Upload Date</label>
                <p className="text-sm text-gray-900">{formatDate(resume.created_at)}</p>
              </div>
            </div>
          </div>

          {/* Extracted Information */}
          {resume.metadata && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                <User className="h-5 w-5" />
                <span>Extracted Information</span>
              </h3>
              
              <div className="space-y-4">
                {/* Skills */}
                {resume.metadata.skills && resume.metadata.skills.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center space-x-1">
                      <Award className="h-4 w-4" />
                      <span>Skills</span>
                    </h4>
                    <div className="flex flex-wrap gap-1">
                      {resume.metadata.skills.map((skill, index) => (
                        <span
                          key={index}
                          className="bg-primary-100 text-primary-800 text-xs px-2 py-1 rounded"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Experience */}
                {resume.metadata.experience && resume.metadata.experience.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center space-x-1">
                      <Briefcase className="h-4 w-4" />
                      <span>Experience</span>
                    </h4>
                    <div className="space-y-1">
                      {resume.metadata.experience.map((exp, index) => (
                        <p key={index} className="text-sm text-gray-600">
                          {exp}
                        </p>
                      ))}
                    </div>
                  </div>
                )}

                {/* Education */}
                {resume.metadata.education && resume.metadata.education.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center space-x-1">
                      <GraduationCap className="h-4 w-4" />
                      <span>Education</span>
                    </h4>
                    <div className="space-y-1">
                      {resume.metadata.education.map((edu, index) => (
                        <p key={index} className="text-sm text-gray-600">
                          {edu}
                        </p>
                      ))}
                    </div>
                  </div>
                )}

                {/* Contact Information */}
                {resume.metadata.contact_info && Object.keys(resume.metadata.contact_info).length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center space-x-1">
                      <Mail className="h-4 w-4" />
                      <span>Contact Information</span>
                    </h4>
                    <div className="space-y-1">
                      {resume.metadata.contact_info.email && (
                        <div className="flex items-center space-x-1">
                          <Mail className="h-3 w-3 text-gray-400" />
                          <span className="text-sm text-gray-600">
                            {resume.metadata.contact_info.email}
                          </span>
                        </div>
                      )}
                      {resume.metadata.contact_info.phone && (
                        <div className="flex items-center space-x-1">
                          <Phone className="h-3 w-3 text-gray-400" />
                          <span className="text-sm text-gray-600">
                            {resume.metadata.contact_info.phone}
                          </span>
                        </div>
                      )}
                      {resume.metadata.contact_info.linkedin && (
                        <div className="flex items-center space-x-1">
                          <span className="text-sm text-gray-600">
                            LinkedIn: {resume.metadata.contact_info.linkedin}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Actions</h3>
            <div className="space-y-3">
              <Link
                to="/search"
                className="w-full bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors text-center block"
              >
                Search Similar Candidates
              </Link>
              <Link
                to="/jobs"
                className="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors text-center block"
              >
                Match with Jobs
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CandidateDetail;
