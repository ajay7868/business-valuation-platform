import React, { useState } from 'react';
import { toast } from 'react-toastify';
import { generateReport, downloadReport } from '../services/api';

function ReportGenerator({ companyData, valuationResults, swotAnalysis, onPrev }) {
  const [generating, setGenerating] = useState(false);
  const [reportFormat, setReportFormat] = useState('pdf');
  const [generatedReports, setGeneratedReports] = useState([]);

  const handleGenerateReport = async () => {
    setGenerating(true);
    
    try {
      const reportData = {
        format: reportFormat,
        company_name: companyData.company_name,
        executive_summary: generateExecutiveSummary(),
        asset_value: valuationResults?.asset_based || 0,
        income_value: valuationResults?.income_based?.dcf_value || 0,
        market_value: valuationResults?.market_based?.revenue_multiple || 0,
        low_value: valuationResults?.valuation_range?.low || 0,
        mid_value: valuationResults?.valuation_range?.mid || 0,
        high_value: valuationResults?.valuation_range?.high || 0,
        swot_analysis: swotAnalysis,
        company_data: companyData,
        valuation_results: valuationResults
      };

      const response = await generateReport(reportData);
      
      setGeneratedReports(prev => [...prev, {
        filename: response.report_filename,
        format: reportFormat,
        generated_at: new Date().toLocaleString(),
        download_url: response.download_url
      }]);
      
      toast.success('Report generated successfully!');
    } catch (error) {
      toast.error('Failed to generate report: ' + error.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleDownloadReport = async (filename) => {
    try {
      const response = await downloadReport(filename);
      
      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('Report downloaded!');
    } catch (error) {
      toast.error('Failed to download report: ' + error.message);
    }
  };

  const generateExecutiveSummary = () => {
    const company = companyData.company_name || 'The Company';
    const revenue = companyData.revenue || 0;
    const midValue = valuationResults?.valuation_range?.mid || 0;
    
    return `${company} is a ${companyData.industry || 'business'} company with annual revenue of $${revenue.toLocaleString()}. Based on our comprehensive analysis using multiple valuation methodologies, we estimate the fair market value to be approximately $${midValue.toLocaleString()}.`;
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="row">
      <div className="col-md-8">
        <div className="card">
          <div className="card-header">
            <h5>Generate Valuation Report</h5>
          </div>
          <div className="card-body">
            {/* Report Preview */}
            <div className="report-preview mb-4">
              <h6>Report Preview</h6>
              <div className="border p-3 bg-light">
                <h4>{companyData.company_name || 'Company Name'} - Business Valuation Report</h4>
                <p><strong>Date:</strong> {new Date().toLocaleDateString()}</p>
                <p><strong>Industry:</strong> {companyData.industry || 'N/A'}</p>
                <p><strong>Annual Revenue:</strong> {formatCurrency(companyData.revenue || 0)}</p>
                
                <h6 className="mt-3">Valuation Summary</h6>
                <table className="table table-sm">
                  <tbody>
                    <tr>
                      <td>Low Estimate:</td>
                      <td>{formatCurrency(valuationResults?.valuation_range?.low || 0)}</td>
                    </tr>
                    <tr>
                      <td>Mid Estimate:</td>
                      <td><strong>{formatCurrency(valuationResults?.valuation_range?.mid || 0)}</strong></td>
                    </tr>
                    <tr>
                      <td>High Estimate:</td>
                      <td>{formatCurrency(valuationResults?.valuation_range?.high || 0)}</td>
                    </tr>
                  </tbody>
                </table>
                
                <p className="mt-3">
                  <strong>Executive Summary:</strong> {generateExecutiveSummary()}
                </p>
              </div>
            </div>

            {/* Report Options */}
            <div className="mb-4">
              <h6>Report Format</h6>
              <div className="form-check form-check-inline">
                <input
                  className="form-check-input"
                  type="radio"
                  name="reportFormat"
                  id="pdf"
                  value="pdf"
                  checked={reportFormat === 'pdf'}
                  onChange={(e) => setReportFormat(e.target.value)}
                />
                <label className="form-check-label" htmlFor="pdf">
                  PDF Report
                </label>
              </div>
              <div className="form-check form-check-inline">
                <input
                  className="form-check-input"
                  type="radio"
                  name="reportFormat"
                  id="word"
                  value="word"
                  checked={reportFormat === 'word'}
                  onChange={(e) => setReportFormat(e.target.value)}
                />
                <label className="form-check-label" htmlFor="word">
                  Word Document
                </label>
              </div>
              <div className="form-check form-check-inline">
                <input
                  className="form-check-input"
                  type="radio"
                  name="reportFormat"
                  id="excel"
                  value="excel"
                  checked={reportFormat === 'excel'}
                  onChange={(e) => setReportFormat(e.target.value)}
                />
                <label className="form-check-label" htmlFor="excel">
                  Excel Workbook
                </label>
              </div>
            </div>

            <button
              className="btn btn-success btn-lg"
              onClick={handleGenerateReport}
              disabled={generating}
            >
              {generating ? (
                <>
                  <span className="spinner-border spinner-border-sm mr-2" role="status"></span>
                  Generating Report...
                </>
              ) : (
                `Generate ${reportFormat.toUpperCase()} Report`
              )}
            </button>
          </div>
        </div>

        {/* Generated Reports */}
        {generatedReports.length > 0 && (
          <div className="card mt-4">
            <div className="card-header">
              <h6>Generated Reports</h6>
            </div>
            <div className="card-body">
              <div className="list-group">
                {generatedReports.map((report, index) => (
                  <div key={index} className="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                      <h6 className="mb-1">{report.filename}</h6>
                      <small className="text-muted">
                        Generated: {report.generated_at} | Format: {report.format.toUpperCase()}
                      </small>
                    </div>
                    <button
                      className="btn btn-outline-primary btn-sm"
                      onClick={() => handleDownloadReport(report.filename)}
                    >
                      Download
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="col-md-4">
        <div className="card">
          <div className="card-header">
            <h6>Report Contents</h6>
          </div>
          <div className="card-body">
            <ul className="list-unstyled">
              <li>✓ Executive Summary</li>
              <li>✓ Company Overview</li>
              <li>✓ Financial Analysis</li>
              <li>✓ Valuation Methods</li>
              <li>✓ SWOT Analysis</li>
              <li>✓ Market Positioning</li>
              <li>✓ Risk Assessment</li>
              <li>✓ Recommendations</li>
              <li>✓ Appendices</li>
            </ul>
          </div>
        </div>

        <div className="card mt-3">
          <div className="card-header">
            <h6>Actions</h6>
          </div>
          <div className="card-body">
            <button className="btn btn-info btn-block mb-2">
              Email Report
            </button>
            <button className="btn btn-warning btn-block mb-2">
              Schedule Follow-up
            </button>
            <button className="btn btn-secondary btn-block" onClick={onPrev}>
              Back to Results
            </button>
          </div>
        </div>

        <div className="card mt-3">
          <div className="card-header">
            <h6>Next Steps</h6>
          </div>
          <div className="card-body">
            <small>
              <p>• Review the valuation with stakeholders</p>
              <p>• Consider market positioning strategies</p>
              <p>• Prepare for buyer presentations</p>
              <p>• Update business improvements</p>
            </small>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ReportGenerator;