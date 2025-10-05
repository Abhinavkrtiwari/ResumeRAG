import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { jobAPI } from '../services/api';
import { useForm } from 'react-hook-form';
import { Plus, Briefcase, MapPin, DollarSign, Building, Target, Users } from 'lucide-react';
import toast from 'react-hot-toast';

const Jobs = () => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [matchResults, setMatchResults] = useState(null);
  const [matching, setMatching] = useState(false);
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm();

  // Mock jobs data since we don't have a jobs list endpoint
  const jobs = [
    {
      id: 1,
      title: "Senior Python Developer",
      description: "We are looking for an experienced Python developer to join our team. You will work on building scalable web applications and APIs.",
      requirements: ["Python", "Django", "PostgreSQL", "AWS", "5+ years experience"],
      location: "San Francisco, CA",
      salary_min: 120000,
      salary_max: 180000,
      company: "TechCorp Inc",
      created_at: "2024-01-15T10:00:00Z"
    },
    {
      id: 2,
      title: "Frontend React Developer",
      description: "Join our frontend team to build beautiful and responsive user interfaces using React and modern web technologies.",
      requirements: ["React", "JavaScript", "TypeScript", "CSS", "3+ years experience"],
      location: "New York, NY",
      salary_min: 90000,
      salary_max: 130000,
      company: "WebSolutions LLC",
      created_at: "2024-01-20T14:30:00Z"
    },
    {
      id: 3,
      title: "Data Scientist",
      description: "We need a data scientist to help us extract insights from large datasets and build machine learning models.",
      requirements: ["Python", "Machine Learning", "SQL", "Statistics", "PhD or MS"],
      location: "Remote",
      salary_min: 100000,
      salary_max: 150000,
      company: "DataTech Corp",
      created_at: "2024-01-25T09:15:00Z"
    }
  ];

  const createJobMutation = useMutation(
    (data) => jobAPI.create(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('jobs');
        toast.success('Job created successfully!');
        setShowCreateForm(false);
        reset();
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Failed to create job');
      }
    }
  );

  const matchMutation = useMutation(
    ({ jobId, topN }) => jobAPI.match(jobId, { top_n: topN }),
    {
      onSuccess: (response) => {
        setMatchResults(response.data);
        toast.success('Matching completed!');
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Matching failed');
      }
    }
  );

  const onSubmit = (data) => {
    // Convert requirements string to array
    const requirements = data.requirements
      .split('\n')
      .map(req => req.trim())
      .filter(req => req.length > 0);
    
    createJobMutation.mutate({
      ...data,
      requirements
    });
  };

  const handleMatch = async (jobId, topN = 10) => {
    setMatching(true);
    try {
      await matchMutation.mutateAsync({ jobId, topN });
    } finally {
      setMatching(false);
    }
  };

  const formatSalary = (min, max) => {
    if (min && max) {
      return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
    } else if (min) {
      return `$${min.toLocaleString()}+`;
    } else if (max) {
      return `Up to $${max.toLocaleString()}`;
    }
    return 'Salary not specified';
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Job Postings</h1>
          <p className="text-gray-600">
            Create job postings and match candidates against your requirements.
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>Create Job</span>
        </button>
      </div>

      {/* Create Job Form */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Create New Job</h2>
            
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Job Title *
                  </label>
                  <input
                    {...register('title', { required: 'Job title is required' })}
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    placeholder="e.g., Senior Python Developer"
                  />
                  {errors.title && (
                    <p className="text-sm text-red-600 mt-1">{errors.title.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Company *
                  </label>
                  <input
                    {...register('company', { required: 'Company is required' })}
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    placeholder="e.g., TechCorp Inc"
                  />
                  {errors.company && (
                    <p className="text-sm text-red-600 mt-1">{errors.company.message}</p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Job Description *
                </label>
                <textarea
                  {...register('description', { required: 'Description is required' })}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Describe the role, responsibilities, and what you're looking for..."
                />
                {errors.description && (
                  <p className="text-sm text-red-600 mt-1">{errors.description.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Requirements (one per line) *
                </label>
                <textarea
                  {...register('requirements', { required: 'Requirements are required' })}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Python&#10;Django&#10;PostgreSQL&#10;5+ years experience"
                />
                {errors.requirements && (
                  <p className="text-sm text-red-600 mt-1">{errors.requirements.message}</p>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Location
                  </label>
                  <input
                    {...register('location')}
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    placeholder="e.g., San Francisco, CA"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Min Salary
                  </label>
                  <input
                    {...register('salary_min', { valueAsNumber: true })}
                    type="number"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    placeholder="120000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Max Salary
                  </label>
                  <input
                    {...register('salary_max', { valueAsNumber: true })}
                    type="number"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    placeholder="180000"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createJobMutation.isLoading}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
                >
                  {createJobMutation.isLoading ? 'Creating...' : 'Create Job'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Jobs List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {jobs.map((job) => (
          <div key={job.id} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-1">
                  {job.title}
                </h3>
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <div className="flex items-center space-x-1">
                    <Building className="h-4 w-4" />
                    <span>{job.company}</span>
                  </div>
                  {job.location && (
                    <div className="flex items-center space-x-1">
                      <MapPin className="h-4 w-4" />
                      <span>{job.location}</span>
                    </div>
                  )}
                </div>
              </div>
              <button
                onClick={() => handleMatch(job.id)}
                disabled={matching}
                className="bg-primary-600 text-white px-3 py-1 rounded text-sm hover:bg-primary-700 transition-colors disabled:opacity-50 flex items-center space-x-1"
              >
                <Target className="h-3 w-3" />
                <span>{matching ? 'Matching...' : 'Match'}</span>
              </button>
            </div>

            <p className="text-gray-600 mb-4 line-clamp-3">
              {job.description}
            </p>

            <div className="space-y-3">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Requirements</h4>
                <div className="flex flex-wrap gap-2">
                  {job.requirements.map((req, index) => (
                    <span
                      key={index}
                      className="bg-primary-100 text-primary-800 text-xs px-2 py-1 rounded"
                    >
                      {req}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex items-center space-x-1 text-sm text-gray-500">
                <DollarSign className="h-4 w-4" />
                <span>{formatSalary(job.salary_min, job.salary_max)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Match Results */}
      {matchResults && (
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Users className="h-5 w-5 text-primary-600" />
            <h3 className="text-lg font-medium text-gray-900">Match Results</h3>
          </div>
          
          <div className="space-y-4">
            {matchResults.matches.map((match, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-medium text-gray-900">
                    {match.filename}
                  </h4>
                  <span className="text-sm font-medium text-primary-600">
                    {(match.score * 100).toFixed(1)}% match
                  </span>
                </div>
                
                {match.evidence && match.evidence.length > 0 && (
                  <div className="mb-3">
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Evidence</h5>
                    <div className="space-y-2">
                      {match.evidence.map((evidence, idx) => (
                        <div key={idx} className="text-sm text-gray-600 bg-green-50 p-2 rounded">
                          <span className="font-medium">{evidence.requirement}:</span> {evidence.evidence}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {match.missing_requirements && match.missing_requirements.length > 0 && (
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Missing Requirements</h5>
                    <div className="flex flex-wrap gap-1">
                      {match.missing_requirements.map((req, idx) => (
                        <span key={idx} className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded">
                          {req}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Jobs;
