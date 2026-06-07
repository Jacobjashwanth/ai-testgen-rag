import { Loader, Search } from 'lucide-react';
import { useState } from 'react';
import { generateTests } from '../services/api';

const TEST_TYPES = [
  { id: 'pytest', label: 'Pytest (Unit Tests)', color: 'bg-purple-500' },
  { id: 'selenium', label: 'Selenium (UI Tests)', color: 'bg-orange-500' },
  { id: 'rest', label: 'REST API Tests', color: 'bg-green-500' }
];

export default function QueryInterface({ onResults, onError }) {
  const [query, setQuery] = useState('');
  const [selectedTypes, setSelectedTypes] = useState(['pytest']);
  const [loading, setLoading] = useState(false);

  const toggleTestType = (typeId) => {
    setSelectedTypes(prev =>
      prev.includes(typeId)
        ? prev.filter(t => t !== typeId)
        : [...prev, typeId]
    );
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim() || selectedTypes.length === 0) {
      onError('Please enter a query and select at least one test type');
      return;
    }

    setLoading(true);
    onError('');

    try {
      const response = await generateTests(query, selectedTypes);
      onResults(response.data);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message;
      onError(`Error generating tests: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <h2 className="text-2xl font-bold mb-4">Generate Tests</h2>

      <form onSubmit={handleSearch} className="space-y-4">
        {/* Query Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            What tests do you need?
          </label>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., Generate tests for user authentication, Test the payment API endpoint..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
        </div>

        {/* Test Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Test Types
          </label>
          <div className="flex flex-wrap gap-2">
            {TEST_TYPES.map(type => (
              <button
                key={type.id}
                type="button"
                onClick={() => toggleTestType(type.id)}
                className={`px-4 py-2 rounded-lg font-medium text-white transition ${
                  selectedTypes.includes(type.id)
                    ? `${type.color} opacity-100`
                    : 'bg-gray-300 opacity-50 hover:opacity-70'
                }`}
                disabled={loading}
              >
                {type.label}
              </button>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Generating Tests...
            </>
          ) : (
            <>
              <Search className="w-5 h-5" />
              Generate Tests
            </>
          )}
        </button>
      </form>
    </div>
  );
}
