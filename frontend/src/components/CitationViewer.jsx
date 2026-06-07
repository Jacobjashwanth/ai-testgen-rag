import { ChevronDown, ChevronUp, FileCode } from 'lucide-react';
import { useState } from 'react';
import { SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomOneDark } from 'react-syntax-highlighter/dist/esm/styles/hljs';

export default function CitationViewer({ citations }) {
  const [expandedCitations, setExpandedCitations] = useState(new Set());

  const toggleCitation = (idx) => {
    const newExpanded = new Set(expandedCitations);
    if (newExpanded.has(idx)) {
      newExpanded.delete(idx);
    } else {
      newExpanded.add(idx);
    }
    setExpandedCitations(newExpanded);
  };

  return (
    <div className="p-4 bg-gray-50">
      <h4 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
        <FileCode className="w-5 h-5" />
        Source Citations ({citations.length})
      </h4>
      
      <div className="space-y-2">
        {citations.map((citation, idx) => {
          const isExpanded = expandedCitations.has(idx);
          
          return (
            <div key={idx} className="border border-gray-300 rounded overflow-hidden bg-white">
              <button
                onClick={() => toggleCitation(idx)}
                className="w-full p-3 text-left hover:bg-gray-100 transition flex items-center justify-between"
              >
                <div className="flex-1">
                  <div className="font-medium text-gray-800">
                    {citation.name}
                    <span className="text-sm text-gray-500 font-normal ml-2">
                      ({citation.chunk_type})
                    </span>
                  </div>
                  <div className="text-xs text-gray-600 mt-1">
                    📄 {citation.source_file}
                    <span className="ml-2">
                      Lines {citation.line_start}-{citation.line_end}
                    </span>
                  </div>
                </div>
                {isExpanded ? (
                  <ChevronUp className="w-4 h-4 text-gray-500" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-gray-500" />
                )}
              </button>

              {isExpanded && (
                <div className="border-t border-gray-200 p-3 bg-gray-50">
                  <div className="overflow-x-auto rounded bg-gray-900 text-sm">
                    <SyntaxHighlighter
                      language="python"
                      style={atomOneDark}
                      customStyle={{ margin: 0, padding: '0.75rem' }}
                    >
                      {citation.content}
                    </SyntaxHighlighter>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
