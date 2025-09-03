import React, { useState, useEffect } from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

import Dashboard from './components/Dashboard';
import FileUpload from './components/FileUpload';
import ValuationResults from './components/ValuationResults';
import ReportGenerator from './components/ReportGenerator';

function App() {
  const [currentStep, setCurrentStep] = useState(1);
  const [companyData, setCompanyData] = useState({});
  const [valuationResults, setValuationResults] = useState(null);
  const [swotAnalysis, setSwotAnalysis] = useState(null);

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

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <FileUpload 
            onNext={nextStep}
            onDataExtracted={(data) => {
              setCompanyData(prevData => ({...prevData, ...data}));
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
          />
        );
      case 3:
        return (
          <ValuationResults 
            results={valuationResults}
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
        </div>
      </nav>

      <div className="container mt-4">
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

      <ToastContainer position="top-right" autoClose={3000} />
    </div>
  );
}

export default App;