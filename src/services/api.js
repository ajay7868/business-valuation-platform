import axios from 'axios';

// Configure API base URL based on environment
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://business-valuation-platform-1.vercel.app/api'
  : '/api';

// Create axios instance with configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for debugging and error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response.data;
  },
  (error) => {
    console.error('❌ API Response Error:', error);
    
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      console.error(`HTTP ${status}:`, data);
      
      switch (status) {
        case 413:
          throw new Error('File too large. Maximum size is 100MB.');
        case 400:
          throw new Error(data?.error || 'Bad request. Please check your data.');
        case 500:
          throw new Error('Server error. Please try again later.');
        default:
          throw new Error(data?.error || `Request failed with status ${status}`);
      }
    } else if (error.request) {
      // Request made but no response received
      if (error.code === 'ECONNABORTED') {
        throw new Error('Request timeout. Please try again.');
      }
      throw new Error('No response from server. Please check your connection.');
    } else {
      // Something else happened
      throw new Error(error.message || 'An unexpected error occurred.');
    }
  }
);

// API functions
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  console.log('📤 Uploading file:', file.name, 'Size:', (file.size / 1024 / 1024).toFixed(2), 'MB');
  
  return api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const calculateValuation = async (companyData) => {
  console.log('💰 Calculating valuation for:', companyData.company_name);
  return api.post('/valuation', companyData);
};

export const generateSWOT = async (companyData) => {
  console.log('🔍 Generating SWOT analysis for:', companyData.company_name);
  return api.post('/swot', companyData);
};

export const generateReport = async (reportData) => {
  console.log('📊 Generating report for:', reportData.company_data?.company_name);
  return api.post('/report/generate', reportData);
};

export const downloadReport = async (filename) => {
  console.log('📥 Downloading report:', filename);
  return api.get(`/report/download/${filename}`, {
    responseType: 'blob',
  });
};

export default api;
