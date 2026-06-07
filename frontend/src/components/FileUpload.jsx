import { AlertCircle, CheckCircle, Upload } from 'lucide-react';
import { useState } from 'react';
import { uploadFile } from '../services/api';

export default function FileUpload({ onUploadSuccess, onStatusChange }) {
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');

  const handleFileUpload = async (e) => {
    const files = e.target.files;
    if (!files) return;

    setError('');
    for (let file of files) {
      setUploading(true);
      setStatus(`Uploading ${file.name}...`);
      onStatusChange(`Uploading ${file.name}...`);

      try {
        const response = await uploadFile(file);
        setStatus(`✓ ${file.name}: ${response.data.chunks_count} chunks added`);
        onStatusChange(`✓ ${file.name}: ${response.data.chunks_count} chunks added`);
        if (onUploadSuccess) onUploadSuccess(response.data);
        setTimeout(() => setStatus(''), 2000);
      } catch (err) {
        const errorMsg = err.response?.data?.detail || err.message;
        setError(`Failed to upload ${file.name}: ${errorMsg}`);
        onStatusChange(`Failed to upload ${file.name}`);
      }
    }
    setUploading(false);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <h2 className="text-2xl font-bold mb-4">Upload Files</h2>
      
      <div className="border-2 border-dashed border-blue-300 rounded-lg p-8 text-center hover:border-blue-500 transition cursor-pointer bg-blue-50">
        <label className="cursor-pointer flex flex-col items-center gap-2">
          <Upload className="w-8 h-8 text-blue-500" />
          <span className="text-lg font-medium text-gray-700">
            Click to upload Python files or API specs
          </span>
          <span className="text-sm text-gray-500">
            Supports .py, .json, .yaml files
          </span>
          <input
            type="file"
            multiple
            accept=".py,.json,.yaml,.yml"
            onChange={handleFileUpload}
            disabled={uploading}
            className="hidden"
          />
        </label>
      </div>

      {status && (
        <div className="mt-4 p-3 bg-blue-100 text-blue-800 rounded flex items-center gap-2">
          <CheckCircle className="w-5 h-5" />
          <span>{status}</span>
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 bg-red-100 text-red-800 rounded flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          <span>{error}</span>
        </div>
      )}

      {uploading && (
        <div className="mt-4 p-3 bg-yellow-100 text-yellow-800 rounded">
          Processing files...
        </div>
      )}
    </div>
  );
}
