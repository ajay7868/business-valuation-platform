import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const apiService = {
  // Health check
  healthCheck: () => axios.get(`${API_BASE_URL}/health`),

  // File upload
  uploadFile: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return axios.post(`${API_BASE_URL}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Create valuation
  createValuation: (companyData) => 
    axios.post(`${API_BASE_URL}/valuation`, companyData),

  // Generate SWOT analysis
  generateSWOT: (companyData) => 
    axios.post(`${API_BASE_URL}/swot`, companyData),

  // Generate report
  generateReport: (reportData) => 
    axios.post(`${API_BASE_URL}/report/generate`, reportData),

  // Download report
  downloadReport: (filename) => 
    axios.get(`${API_BASE_URL}/report/download/${filename}`, {
      responseType: 'blob',
    }),

  // List companies
  listCompanies: () => axios.get(`${API_BASE_URL}/companies`),
};

export default apiService;