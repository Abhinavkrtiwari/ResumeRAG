import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { ragAPI, resumeAPI } from '../services/api';
import { Search, MessageSquare, File, Brain } from 'lucide-react';
import toast from 'react-hot-toast';

const Search = () => {
  const [query, setQuery] = useState('');
  const [k, setK] = useState(5);
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);

  // Fetch resumes for context
  const { data: resumes } = useQuery(
    'resumes',
    () => resumeAPI.getAll().then(res => res.data),
    {
      onError: (error) => {
        toast.error('Failed to load resumes');
      }
    }
  );

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    setSearching(true);
    try {
      const response = await ragAPI.ask({
        query: query.trim(),
        k: k
      });
      setSearchResults(response.data);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Search failed');
    } finally {
      setSearching(false);
    }
  };

  const exampleQueries = [
    "What skills do the candidates have?",
    "Who has experience with Python?",
    "Show me candidates with machine learning experience",
    "What are the education backgrounds?",
    "Who has worked at tech companies?",
    "Find candidates with project management experience"
  ];

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Search Resumes</h1>
        <p className="text-gray-600">
          Ask questions about your uploaded resumes using natural language. Get intelligent answers with source citations.
        </p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <form onSubmit={handleSearch} className="space-y-4">
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
              Search Query
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MessageSquare className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                placeholder="Ask a question about your resumes..."
                disabled={searching}
              />
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div>
              <label htmlFor="k" className="block text-sm font-medium text-gray-700 mb-1">
                Number of Results
              </label>
              <select
                id="k"
                value={k}
                onChange={(e) => setK(parseInt(e.target.value))}
                className="block w-20 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                disabled={searching}
              >
                <option value={3}>3</option>
                <option value={5}>5</option>
                <option value={10}>10</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={searching || !query.trim()}
              className="mt-6 bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {searching ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <Search className="h-4 w-4" />
                  <span>Search</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Example Queries */}
      <div className="mb-8">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Example Queries</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {exampleQueries.map((example, index) => (
            <button
              key={index}
              onClick={() => setQuery(example)}
              className="text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors text-sm text-gray-700"
            >
              {example}
            </button>
          ))}
        </div>
      </div>

      {/* Search Results */}
      {searchResults && (
        <div className="space-y-6">
          {/* Answer */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Brain className="h-5 w-5 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">Answer</h3>
            </div>
            <p className="text-gray-700 leading-relaxed">
              {searchResults.answer}
            </p>
          </div>

          {/* Sources */}
          {searchResults.sources && searchResults.sources.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Sources</h3>
              <div className="space-y-4">
                {searchResults.sources.map((source, index) => (
                  <div key={index} className="border-l-4 border-primary-200 pl-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <File className="h-4 w-4 text-gray-400" />
                      <span className="font-medium text-gray-900">
                        {source.filename}
                      </span>
                      <span className="text-sm text-gray-500">
                        (Score: {(source.similarity_score * 100).toFixed(1)}%)
                      </span>
                    </div>
                    
                    {source.snippets && source.snippets.length > 0 && (
                      <div className="space-y-2">
                        {source.snippets.map((snippet, snippetIndex) => (
                          <p key={snippetIndex} className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                            {snippet}
                          </p>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* No Results Message */}
      {searchResults && (!searchResults.sources || searchResults.sources.length === 0) && (
        <div className="text-center py-8 text-gray-500">
          <Search className="mx-auto h-12 w-12 text-gray-300 mb-4" />
          <p>No relevant information found</p>
          <p className="text-sm">Try rephrasing your question or upload more resumes</p>
        </div>
      )}

      {/* Resume Count */}
      {resumes && (
        <div className="mt-8 text-center text-sm text-gray-500">
          Searching through {resumes.total} uploaded resume{resumes.total !== 1 ? 's' : ''}
        </div>
      )}
    </div>
  );
};

export default Search;
