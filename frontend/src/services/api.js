import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
});

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const generateTests = async (query, testTypes, topK = 5) => {
  return api.post('/generate-tests', {
    query,
    test_types: testTypes,
    top_k: topK
  });
};

export const getIndexStatus = async () => {
  return api.get('/index-status');
};

export const clearIndex = async () => {
  return api.post('/clear-index');
};

export default api;
