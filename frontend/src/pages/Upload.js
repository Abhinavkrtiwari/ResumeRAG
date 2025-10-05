import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { resumeAPI } from '../services/api';
import { Upload, File, X, CheckCircle, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const Upload = () => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const queryClient = useQueryClient();

  // Fetch existing resumes
  const { data: resumes, isLoading } = useQuery(
    'resumes',
    () => resumeAPI.getAll().then(res => res.data),
    {
      onError: (error) => {
        toast.error('Failed to load resumes');
      }
    }
  );

  // Upload mutation
  const uploadMutation = useMutation(
    ({ file, idempotencyKey }) => resumeAPI.upload(file, idempotencyKey),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('resumes');
        toast.success('Resume uploaded successfully!');
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Upload failed');
      }
    }
  );

  const onDrop = useCallback((acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      status: 'pending',
      progress: 0
    }));
    
    setUploadedFiles(prev => [...prev, ...newFiles]);
    
    // Upload files
    newFiles.forEach(fileObj => {
      uploadFile(fileObj);
    });
  }, []);

  const uploadFile = async (fileObj) => {
    try {
      setUploading(true);
      
      // Generate idempotency key
      const idempotencyKey = `${fileObj.file.name}_${Date.now()}`;
      
      // Update file status
      setUploadedFiles(prev => 
        prev.map(f => 
          f.id === fileObj.id 
            ? { ...f, status: 'uploading', progress: 50 }
            : f
        )
      );
      
      await uploadMutation.mutateAsync({
        file: fileObj.file,
        idempotencyKey
      });
      
      // Update file status to success
      setUploadedFiles(prev => 
        prev.map(f => 
          f.id === fileObj.id 
            ? { ...f, status: 'success', progress: 100 }
            : f
        )
      );
      
    } catch (error) {
      // Update file status to error
      setUploadedFiles(prev => 
        prev.map(f => 
          f.id === fileObj.id 
            ? { ...f, status: 'error', progress: 0 }
            : f
        )
      );
    } finally {
      setUploading(false);
    }
  };

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'application/zip': ['.zip']
    },
    multiple: true
  });

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Resumes</h1>
        <p className="text-gray-600">
          Upload resume files in PDF, DOCX, TXT, or ZIP format. ZIP files can contain multiple resumes.
        </p>
      </div>

      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-lg font-medium text-gray-900 mb-2">
          {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
        </p>
        <p className="text-gray-500 mb-4">
          or click to select files
        </p>
        <p className="text-sm text-gray-400">
          Supports PDF, DOCX, TXT, and ZIP files
        </p>
      </div>

      {/* Upload Progress */}
      {uploadedFiles.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Upload Progress</h3>
          <div className="space-y-3">
            {uploadedFiles.map((fileObj) => (
              <div key={fileObj.id} className="bg-white border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <File className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {fileObj.file.name}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatFileSize(fileObj.file.size)}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {fileObj.status === 'success' && (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    )}
                    {fileObj.status === 'error' && (
                      <AlertCircle className="h-5 w-5 text-red-500" />
                    )}
                    {fileObj.status === 'uploading' && (
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
                    )}
                    
                    <button
                      onClick={() => removeFile(fileObj.id)}
                      className="text-gray-400 hover:text-red-500"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                </div>
                
                {fileObj.status === 'uploading' && (
                  <div className="mt-2">
                    <div className="bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${fileObj.progress}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Existing Resumes */}
      <div className="mt-8">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Your Resumes</h3>
        
        {isLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-2 text-gray-500">Loading resumes...</p>
          </div>
        ) : resumes?.items?.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {resumes.items.map((resume) => (
              <div key={resume.id} className="bg-white border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 truncate">
                      {resume.original_filename}
                    </h4>
                    <p className="text-sm text-gray-500 mt-1">
                      {formatFileSize(resume.file_size)}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      Uploaded {new Date(resume.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <File className="h-5 w-5 text-gray-400 flex-shrink-0 ml-2" />
                </div>
                
                {resume.metadata && (
                  <div className="mt-3">
                    {resume.metadata.skills && resume.metadata.skills.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {resume.metadata.skills.slice(0, 3).map((skill, index) => (
                          <span
                            key={index}
                            className="inline-block bg-primary-100 text-primary-800 text-xs px-2 py-1 rounded"
                          >
                            {skill}
                          </span>
                        ))}
                        {resume.metadata.skills.length > 3 && (
                          <span className="text-xs text-gray-500">
                            +{resume.metadata.skills.length - 3} more
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <File className="mx-auto h-12 w-12 text-gray-300 mb-4" />
            <p>No resumes uploaded yet</p>
            <p className="text-sm">Upload your first resume to get started</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Upload;
