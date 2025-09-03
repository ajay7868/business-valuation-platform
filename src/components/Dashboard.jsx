import React, { useState } from 'react';
import { toast } from 'react-toastify';
import { calculateValuation, generateSWOT } from '../services/api';

function Dashboard({ 
  companyData, 
  setCompanyData, 
  onNext, 
  onPrev, 
  setValuationResults, 
  setSwotAnalysis 
}) {
  const [loading, setLoading] = useState(false);
  const [swotLoading, setSwotLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCompanyData({
      ...companyData,
      [name]: value
    });
  };

  const handleValuation = async () => {
    setLoading(true);
    try {
      const response = await calculateValuation(companyData);
      setValuationResults(response.valuation_results);
      toast.success('Valuation completed successfully!');
      onNext();
    } catch (error) {
      toast.error('Valuation failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateSWOT = async () => {
    setSwotLoading(true);
    try {
      const response = await generateSWOT(companyData);
      setSwotAnalysis(response.swot_analysis);
      toast.success('SWOT analysis generated!');
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
          </div>
          <div className="card-body">
            <form>
              <div className="row">
                <div className="col-md-6 mb-3">
                  <label className="form-label">Company Name</label>
                  <input
                    type="text"
                    className="form-control"
                    name="company_name"
                    value={companyData.company_name || ''}
                    onChange={handleInputChange}
                    placeholder="Enter company name"
                  />
                </div>
                <div className="col-md-6 mb-3">
                  <label className="form-label">Industry</label>
                  <select
                    className="form-control"
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
                  <label className="form-label">Annual Revenue ($)</label>
                  <input
                    type="number"
                    className="form-control"
                    name="revenue"
                    value={companyData.revenue || ''}
                    onChange={handleInputChange}
                    placeholder="0"
                  />
                </div>
                <div className="col-md-6 mb-3">
                  <label className="form-label">EBITDA ($)</label>
                  <input
                    type="number"
                    className="form-control"
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
              className="btn btn-info btn-block mb-3"
              onClick={handleGenerateSWOT}
              disabled={swotLoading}
            >
              {swotLoading ? 'Generating...' : 'Generate SWOT Analysis'}
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
      </div>
    </div>
  );
}

export default Dashboard;