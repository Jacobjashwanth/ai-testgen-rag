import { AlertCircle, BarChart3 } from 'lucide-react'
import { useEffect, useState } from 'react'
import FileUpload from './components/FileUpload'
import QueryInterface from './components/QueryInterface'
import TestResults from './components/TestResults'
import { getIndexStatus } from './services/api'

export default function App() {
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [status, setStatus] = useState('');
  const [indexStats, setIndexStats] = useState(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await getIndexStatus();
        setIndexStats(response.data);
      } catch (err) {
        console.log('Could not fetch index status');
      }
    };
    
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-8 h-8 text-blue-600" />
              <h1 className="text-3xl font-bold text-gray-900">AI Test Generator</h1>
            </div>
            {indexStats && (
              <div className="text-sm text-gray-600">
                <span className="font-semibold">{indexStats.total_chunks}</span> chunks indexed
              </div>
            )}
          </div>
          <p className="text-gray-600 mt-2">RAG-powered test generation with AI</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-300 rounded-lg flex items-center gap-2 text-red-800">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
            <button
              onClick={() => setError('')}
              className="ml-auto text-red-600 hover:text-red-800 font-medium"
            >
              ✕
            </button>
          </div>
        )}

        {/* Status Message */}
        {status && (
          <div className="mb-6 p-4 bg-blue-100 border border-blue-300 rounded-lg text-blue-800">
            {status}
          </div>
        )}

        {/* Upload Section */}
        <FileUpload
          onUploadSuccess={() => setError('')}
          onStatusChange={setStatus}
        />

        {/* Query Section */}
        <QueryInterface
          onResults={setResults}
          onError={setError}
        />

        {/* Results Section */}
        {results && (
          <div>
            <TestResults results={results} />
          </div>
        )}

        {/* Empty State */}
        {!results && (
          <div className="text-center py-12 text-gray-500">
            <p className="mb-2">Upload your files to get started.</p>
            <p className="text-sm">Once indexed, write a query to generate tests!</p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-sm text-gray-600">
          <p>AI Test Case Generator © 2024 • Powered by Claude AI & RAG</p>
        </div>
      </footer>
    </div>
  );
}
