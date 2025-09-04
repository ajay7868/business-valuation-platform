import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { calculateValuation, generateSWOT } from '../services/api';

function Dashboard({ 
  companyData, 
  setCompanyData, 
  onNext, 
  onPrev, 
  setValuationResults, 
  setSwotAnalysis,
  extractedData 
}) {
  
  const [loading, setLoading] = useState(false);
  const [swotLoading, setSwotLoading] = useState(false);
  const [valuationResults, setValuationResultsLocal] = useState(null);
  
  // Add useEffect to track companyData changes and auto-fill form
  useEffect(() => {
   
    // Show success message when data is auto-filled from file upload
    if (companyData && Object.keys(companyData).length > 0) {
      const hasFinancialData = companyData.revenue || companyData.ebitda || companyData.net_income;
      if (hasFinancialData) {
        //toast.success('auto-filled with data from uploaded file! Please fill rest fields for better results');
      }
    }
  }, [companyData]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCompanyData({
      ...companyData,
      [name]: value
    });
  };

  // Helper function to check if a field has auto-filled data
  const isFieldAutoFilled = (fieldName) => {
    return companyData[fieldName] && companyData[fieldName] !== '';
  };

  // Helper function to get field styling for auto-filled fields
  const getFieldClassName = (fieldName) => {
    const baseClass = "form-control";
    return isFieldAutoFilled(fieldName) ? `${baseClass} border-success` : baseClass;
  };

  const handleValuation = async () => {
    setLoading(true);
    try {
      const response = await calculateValuation(companyData);
      setValuationResultsLocal(response.valuation_results);
      // Also update the parent component's state
      if (setValuationResults) {
        setValuationResults(response.valuation_results);
      }
      toast.success('Valuation completed successfully!');
      // Don't auto-navigate, let user see results first
    } catch (error) {
      console.error('💰 Valuation error:', error);
      toast.error('Valuation failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateSWOT = async () => {
    // Check if we have meaningful data for SWOT analysis
    const hasData = companyData.company_name && 
                   (companyData.revenue || companyData.ebitda || companyData.net_income);
    
    if (!hasData) {
      toast.warning('Please provide company name and at least one financial metric (revenue, EBITDA, or net income) before generating SWOT analysis.');
      return;
    }
    
    setSwotLoading(true);
    try {
      // Prepare data for SWOT analysis - include extracted data if available
      const swotData = {
        ...companyData,
        extracted_data: extractedData || null
      };
      
      const response = await generateSWOT(swotData);
      setSwotAnalysis(response.swot_analysis);
      toast.success('SWOT analysis generated successfully!');
    } catch (error) {
      toast.error('SWOT generation failed: ' + error.message);
    } finally {
      setSwotLoading(false);
    }
  };

  return (
    <div className="row">
      <div className="col-md-8">
        <div className="card">
          <div className="card-header">
            <h5>Company Information</h5>
            {/* Debug: Show received data */}
            {/* {Object.keys(companyData).length > 0 && (
              <div className="alert alert-info mt-2">
                <small>
                  <strong>Debug - Received Data:</strong> {JSON.stringify(companyData, null, 2)}
                </small>
              </div>
            )} */}
          </div>
          <div className="card-body">
            <form>
              <div className="row">
                <div className="col-md-6 mb-3">
                  {/* <label className="form-label">
                    Company Name
                    {isFieldAutoFilled('company_name') && (
                      <span className="badge bg-success ms-2">Auto-filled</span>
                    )}
                  </label> */}
                  <input
                    type="text"
                    className={getFieldClassName('company_name')}
                    name="company_name"
                    value={companyData.company_name || ''}
                    onChange={handleInputChange}
                    placeholder="Enter company name"
                    onFocus={() => {}}
                  />
                </div>
                <div className="col-md-6 mb-3">
                  {/* <label className="form-label">
                    Industry
                    {isFieldAutoFilled('industry') && (
                      <span className="badge bg-success ms-2">Auto-filled</span>
                    )}
                  </label> */}
                  <select
                    className={getFieldClassName('industry')}
                    name="industry"
                    value={companyData.industry || ''}
                    onChange={handleInputChange}
                  >
                    <option value="">Select industry</option>
                    <option value="manufacturing">Manufacturing</option>
                    <option value="technology">Technology</option>
                    <option value="retail">Retail</option>
                    <option value="services">Services</option>
                    <option value="construction">Construction</option>
                  </select>
                </div>
              </div>

              <div className="row">
                <div className="col-md-6 mb-3">
                  <label className="form-label">
                    Annual Revenue ($)
                    {/* {isFieldAutoFilled('revenue') && (
                      <span className="badge bg-success ms-2">Auto-filled</span>
                    )} */}
                  </label>
                  <input
                    type="number"
                    className={getFieldClassName('revenue')}
                    name="revenue"
                    value={companyData.revenue || ''}
                    onChange={handleInputChange}
                    placeholder="0"
                  />
                </div>
                <div className="col-md-6 mb-3">
                  <label className="form-label">
                    EBITDA ($)
                    {isFieldAutoFilled('ebitda') && (
                      <span className="badge bg-success ms-2">Auto-filled</span>
                    )}
                  </label>
                  <input
                    type="number"
                    className={getFieldClassName('ebitda')}
                    name="ebitda"
                    value={companyData.ebitda || ''}
                    onChange={handleInputChange}
                    placeholder="0"
                  />
                </div>
              </div>

              <div className="row">
                <div className="col-md-6 mb-3">
                  <label className="form-label">Inventory ($)</label>
                  <input
                    type="number"
                    className="form-control"
                    name="inventory"
                    value={companyData.inventory || ''}
                    onChange={handleInputChange}
                    placeholder="0"
                  />
                </div>
                <div className="col-md-6 mb-3">
                  <label className="form-label">Accounts Receivable ($)</label>
                  <input
                    type="number"
                    className="form-control"
                    name="accounts_receivable"
                    value={companyData.accounts_receivable || ''}
                    onChange={handleInputChange}
                    placeholder="0"
                  />
                </div>
              </div>

              <div className="row">
                <div className="col-md-6 mb-3">
                  <label className="form-label">Total Assets ($)</label>
                  <input
                    type="number"
                    className="form-control"
                    name="total_assets"
                    value={companyData.total_assets || ''}
                    onChange={handleInputChange}
                    placeholder="0"
                  />
                </div>
                <div className="col-md-6 mb-3">
                  <label className="form-label">Total Liabilities ($)</label>
                  <input
                    type="number"
                    className="form-control"
                    name="total_liabilities"
                    value={companyData.total_liabilities || ''}
                    onChange={handleInputChange}
                    placeholder="0"
                  />
                </div>
              </div>

              <div className="row">
                <div className="col-md-6 mb-3">
                  <label className="form-label">Cash ($)</label>
                  <input
                    type="number"
                    className="form-control"
                    name="cash"
                    value={companyData.cash || ''}
                    onChange={handleInputChange}
                    placeholder="0"
                  />
                </div>
                <div className="col-md-6 mb-3">
                  <label className="form-label">Net Income ($)</label>
                  <input
                    type="number"
                    className="form-control"
                    name="net_income"
                    value={companyData.net_income || ''}
                    onChange={handleInputChange}
                    placeholder="0"
                  />
                </div>
              </div>

              <div className="mb-3">
                <label className="form-label">Number of Employees</label>
                <input
                  type="number"
                  className="form-control"
                  name="employees"
                  value={companyData.employees || ''}
                  onChange={handleInputChange}
                  placeholder="0"
                />
              </div>
            </form>
          </div>
        </div>
      </div>

      <div className="col-md-4">
        <div className="card">
          <div className="card-header">
            <h5>Actions</h5>
          </div>
          <div className="card-body">
            <button
              className={`btn btn-block mb-3 ${
                companyData.company_name && (companyData.revenue || companyData.ebitda || companyData.net_income)
                  ? 'btn-info' 
                  : 'btn-outline-secondary'
              }`}
              onClick={handleGenerateSWOT}
              disabled={swotLoading || !companyData.company_name || (!companyData.revenue && !companyData.ebitda && !companyData.net_income)}
              title={
                !companyData.company_name 
                  ? 'Please enter company name first'
                  : (!companyData.revenue && !companyData.ebitda && !companyData.net_income)
                  ? 'Please provide at least one financial metric (revenue, EBITDA, or net income)'
                  : 'Generate intelligent SWOT analysis based on your data'
              }
            >
              {swotLoading ? 'Generating...' : 'Generate SWOT Analysis'}
              {companyData.company_name && (companyData.revenue || companyData.ebitda || companyData.net_income) && (
                <span className="badge bg-success ms-2">Ready</span>
              )}
            </button>

            <button
              className="btn btn-success btn-block mb-3"
              onClick={handleValuation}
              disabled={loading || !companyData.company_name}
            >
              {loading ? 'Calculating...' : 'Calculate Valuation'}
            </button>



            <div className="d-flex justify-content-between">
              <button className="btn btn-secondary" onClick={onPrev}>
                Previous
              </button>
            </div>
          </div>
        </div>

        {companyData.revenue && (
          <div className="card mt-3">
            <div className="card-header">
              <h6>Quick Stats</h6>
            </div>
            <div className="card-body">
              <p><strong>Revenue:</strong> ${parseInt(companyData.revenue || 0).toLocaleString()}</p>
              <p><strong>EBITDA:</strong> ${parseInt(companyData.ebitda || 0).toLocaleString()}</p>
              <p><strong>Employees:</strong> {companyData.employees || 'N/A'}</p>
              <p><strong>Industry:</strong> {companyData.industry || 'N/A'}</p>
            </div>
          </div>
        )}

        {/* Valuation Results Summary */}
        {valuationResults && (
          <div className="card mt-3">
            <div className="card-header bg-success text-white">
              <h6 className="mb-0">✅ Valuation Complete</h6>
            </div>
            <div className="card-body">
              <div className="alert alert-success">
                <h6>Company: {valuationResults.company_name}</h6>
                <p className="mb-2"><strong>Calculated Value:</strong> ${valuationResults.calculated_value.toLocaleString()}</p>
                <p className="mb-2"><strong>Method:</strong> {valuationResults.method}</p>
                <p className="mb-0 text-muted"><small>Calculated: {new Date(valuationResults.calculated_at).toLocaleString()}</small></p>
              </div>
              
              <div className="d-flex gap-2">
                <button 
                  className="btn btn-primary"
                  onClick={onNext}
                >
                  📊 View Detailed Results
                </button>
                <button 
                  className="btn btn-outline-secondary"
                  onClick={() => setValuationResultsLocal(null)}
                >
                  Clear Results
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;