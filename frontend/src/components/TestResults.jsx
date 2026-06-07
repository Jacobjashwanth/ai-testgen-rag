import { Check, ChevronDown, ChevronUp, Copy } from 'lucide-react';
import { useState } from 'react';
import { SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomOneDark } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import CitationViewer from './CitationViewer';

export default function TestResults({ results }) {
  const [expandedTests, setExpandedTests] = useState(new Set());
  const [copiedId, setCopiedId] = useState(null);

  if (!results || !results.tests || results.tests.length === 0) {
    return null;
  }

  const toggleExpand = (testId) => {
    const newExpanded = new Set(expandedTests);
    if (newExpanded.has(testId)) {
      newExpanded.delete(testId);
    } else {
      newExpanded.add(testId);
    }
    setExpandedTests(newExpanded);
  };

  const copyToClipboard = (code, testId) => {
    navigator.clipboard.writeText(code).then(() => {
      setCopiedId(testId);
      setTimeout(() => setCopiedId(null), 2000);
    });
  };

  const getTestTypeColor = (testType) => {
    const colors = {
      pytest: 'bg-purple-100 text-purple-800 border-purple-300',
      selenium: 'bg-orange-100 text-orange-800 border-orange-300',
      rest: 'bg-green-100 text-green-800 border-green-300'
    };
    return colors[testType] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-lg shadow p-4 mb-4">
        <h3 className="text-lg font-bold text-gray-800">
          Generated Tests
          <span className="text-sm font-normal text-gray-500 ml-2">
            ({results.tests.length} test suite{results.tests.length !== 1 ? 's' : ''})
          </span>
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Query: <span className="font-mono text-gray-700">{results.query}</span>
        </p>
        <p className="text-sm text-gray-600">
          Retrieved {results.total_chunks_searched} relevant code chunks
        </p>
      </div>

      {results.tests.map((test, idx) => {
        const testId = `test-${idx}`;
        const isExpanded = expandedTests.has(testId);

        return (
          <div key={idx} className="bg-white rounded-lg shadow overflow-hidden">
            {/* Header */}
            <button
              onClick={() => toggleExpand(testId)}
              className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition"
            >
              <div className="flex items-center gap-3">
                <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${getTestTypeColor(test.test_type)}`}>
                  {test.test_type.toUpperCase()}
                </span>
                <span className="text-gray-600">
                  {test.citations.length} source{test.citations.length !== 1 ? 's' : ''}
                </span>
              </div>
              {isExpanded ? (
                <ChevronUp className="w-5 h-5 text-gray-500" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-500" />
              )}
            </button>

            {/* Content */}
            {isExpanded && (
              <div className="border-t border-gray-200">
                {/* Test Code */}
                <div className="p-4 border-b border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-gray-700">Test Code</h4>
                    <button
                      onClick={() => copyToClipboard(test.test_code, testId)}
                      className="flex items-center gap-1 px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm transition"
                    >
                      {copiedId === testId ? (
                        <>
                          <Check className="w-4 h-4" />
                          Copied
                        </>
                      ) : (
                        <>
                          <Copy className="w-4 h-4" />
                          Copy
                        </>
                      )}
                    </button>
                  </div>
                  <div className="overflow-x-auto rounded bg-gray-900">
                    <SyntaxHighlighter
                      language="python"
                      style={atomOneDark}
                      customStyle={{ margin: 0, padding: '1rem' }}
                    >
                      {test.test_code}
                    </SyntaxHighlighter>
                  </div>
                </div>

                {/* Citations */}
                <CitationViewer citations={test.citations} />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
