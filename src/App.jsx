import React, { useState, useEffect } from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

import Dashboard from './components/Dashboard';
import FileUpload from './components/FileUpload';
import ValuationResults from './components/ValuationResults';
import ReportGenerator from './components/ReportGenerator';
import Auth from './components/Auth';
import UserProfile from './components/UserProfile';

function App() {
  const [currentStep, setCurrentStep] = useState(1);
  const [companyData, setCompanyData] = useState({});
  const [extractedData, setExtractedData] = useState(null);
  const [valuationResults, setValuationResults] = useState(null);
  const [swotAnalysis, setSwotAnalysis] = useState(null);
  const [user, setUser] = useState(null);
  const [showAuth, setShowAuth] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [rateLimitStatus, setRateLimitStatus] = useState(null);

  const steps = [
    { id: 1, title: 'Upload Documents', component: 'upload' },
    { id: 2, title: 'Company Data', component: 'data' },
    { id: 3, title: 'Valuation Results', component: 'results' },
    { id: 4, title: 'Generate Report', component: 'report' }
  ];

  const nextStep = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  // Check authentication status on app load
  useEffect(() => {
    // Check if user is already authenticated from localStorage
    const sessionToken = localStorage.getItem('session_token');
    const userData = localStorage.getItem('user_data');
    
    if (sessionToken && userData) {
      try {
        const user = JSON.parse(userData);
        setUser(user);
        // Validate session with backend
        validateSessionWithBackend(sessionToken);
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        localStorage.removeItem('session_token');
        localStorage.removeItem('user_data');
        checkAuthStatus();
      }
    } else {
      // Check if user is already authenticated
      checkAuthStatus();
    }
    
    checkRateLimitStatus();
  }, []);

  const validateSessionWithBackend = async (sessionToken) => {
    try {
      const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:5001';
      const response = await fetch(`${baseUrl}/api/auth/profile`, {
        headers: {
          'Authorization': `Bearer ${sessionToken}`
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        // Update user data with fresh data from backend
        setUser(result.user);
        localStorage.setItem('user_data', JSON.stringify(result.user));
      } else {
        // Session is invalid, clear localStorage
        localStorage.removeItem('session_token');
        localStorage.removeItem('user_data');
        setUser(null);
      }
    } catch (error) {
      console.error('Session validation error:', error);
      localStorage.removeItem('session_token');
      localStorage.removeItem('user_data');
      setUser(null);
    }
  };

  const checkAuthStatus = async () => {
    try {
      const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:5001'; // Point to our minimal auth backend
      const response = await fetch(`${baseUrl}/api/auth/profile`);
      if (response.ok) {
        const result = await response.json();
        setUser(result.user);
      }
          } catch (error) {
        // User not authenticated - this is expected for new users
      }
  };

  const checkRateLimitStatus = async () => {
    try {
      const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:5001';
      const sessionToken = localStorage.getItem('session_token');
      
      const headers = {};
      if (sessionToken) {
        headers['Authorization'] = `Bearer ${sessionToken}`;
      }
      
      const response = await fetch(`${baseUrl}/api/auth/rate-limit-status`, { headers });
      if (response.ok) {
        const result = await response.json();
        setRateLimitStatus(result);
      }
    } catch (error) {
      // Could not fetch rate limit status - non-critical
    }
  };

  const handleAuthSuccess = (userData) => {
    setUser(userData);
    setShowAuth(false);
    checkRateLimitStatus();
  };

  const handleLogout = async () => {
    try {
      const sessionToken = localStorage.getItem('session_token');
      if (sessionToken) {
        const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:5001';
        await fetch(`${baseUrl}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ session_token: sessionToken })
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear localStorage and state
      localStorage.removeItem('session_token');
      localStorage.removeItem('user_data');
      setUser(null);
      setCompanyData({});
      setValuationResults(null);
      setSwotAnalysis(null);
      setCurrentStep(1);
      setRateLimitStatus(null);
    }
  };

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <FileUpload 
            onNext={nextStep}
            onDataExtracted={(data) => {
              
              // Handle new data structure with formData and extractedData
              const formData = data.formData || data;
              const extractedData = data.extractedData || null;
              
      
              
              const newCompanyData = {...companyData, ...formData};
              setCompanyData(newCompanyData);
              // Store the extracted data for SWOT analysis
              setExtractedData(extractedData);
            }}
          />
        );
      case 2:
        return (
          <Dashboard 
            companyData={companyData}
            setCompanyData={setCompanyData}
            onNext={nextStep}
            onPrev={prevStep}
            setValuationResults={setValuationResults}
            setSwotAnalysis={setSwotAnalysis}
            extractedData={extractedData}
          />
        );
      case 3:
        return (
          <ValuationResults 
            valuationResults={valuationResults}
            companyData={companyData}
            swotAnalysis={swotAnalysis}
            onNext={nextStep}
            onPrev={prevStep}
          />
        );
      case 4:
        return (
          <ReportGenerator 
            companyData={companyData}
            valuationResults={valuationResults}
            swotAnalysis={swotAnalysis}
            onPrev={prevStep}
          />
        );
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="App">
      <nav className="navbar navbar-dark bg-primary">
        <div className="container">
          <span className="navbar-brand mb-0 h1">Business Valuation Platform</span>
          <div className="navbar-nav ms-auto">
            {user ? (
              <div className="d-flex align-items-center">
                <span className="text-white me-3">
                  <i className="fas fa-user me-2"></i>
                  {user.email}
                </span>
                <button
                  className="btn btn-outline-light btn-sm me-2"
                  onClick={() => setShowProfile(true)}
                >
                  Profile
                </button>
                <button
                  className="btn btn-outline-light btn-sm"
                  onClick={handleLogout}
                >
                  Logout
                </button>
              </div>
            ) : (
              <button
                className="btn btn-outline-light"
                onClick={() => setShowAuth(true)}
              >
                <i className="fas fa-sign-in-alt me-2"></i>
                Login / Sign Up
              </button>
            )}
          </div>
        </div>
      </nav>

      <div className="container mt-4">
        {/* Rate Limit Warning */}
        {rateLimitStatus && (rateLimitStatus.upload.blocked || rateLimitStatus.report_generation.blocked) && (
          <div className="alert alert-warning">
            <i className="fas fa-exclamation-triangle me-2"></i>
            <strong>Rate Limit Exceeded</strong>
            {rateLimitStatus.upload.blocked && (
              <div>File uploads are temporarily blocked. Please sign up to continue.</div>
            )}
            {rateLimitStatus.report_generation.blocked && (
              <div>Report generation is temporarily blocked. Please sign up to continue.</div>
            )}
          </div>
        )}



        {/* Progress Steps */}
        <div className="row mb-4">
          <div className="col-12">
            <div className="progress-steps">
              {steps.map((step) => (
                <div 
                  key={step.id}
                  className={`step ${currentStep >= step.id ? 'active' : ''}`}
                >
                  <div className="step-number">{step.id}</div>
                  <div className="step-title">{step.title}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Current Step Content */}
        {renderCurrentStep()}
      </div>

      {/* Authentication Modal */}
      {showAuth && (
        <Auth 
          onAuthSuccess={handleAuthSuccess}
          onClose={() => setShowAuth(false)}
        />
      )}

      {/* User Profile Modal */}
      {showProfile && (
        <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  <i className="fas fa-user me-2"></i>
                  User Profile
                </h5>
                <button type="button" className="btn-close" onClick={() => setShowProfile(false)}></button>
              </div>
              <div className="modal-body">
                {user ? (
                  <UserProfile user={user} onLogout={handleLogout} />
                ) : (
                  <div className="text-center">
                    <div className="spinner-border" role="status">
                      <span className="visually-hidden">Loading...</span>
                    </div>
                    <p className="mt-2">Loading user profile...</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      <ToastContainer position="top-right" autoClose={3000} />
    </div>
  );
}

export default App;