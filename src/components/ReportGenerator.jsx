import React, { useState } from 'react';
import { toast } from 'react-toastify';
import { generateReport, downloadReport } from '../services/api';

function ReportGenerator({ companyData, valuationResults, swotAnalysis, onPrev }) {
  const [generating, setGenerating] = useState(false);
  const [reportFormat, setReportFormat] = useState('txt');
  const [generatedReports, setGeneratedReports] = useState([]);

  const handleGenerateReport = async () => {
    setGenerating(true);
    
    try {
      const reportData = {
        format: reportFormat,
        company_name: companyData.company_name || 'Company',
        executive_summary: generateExecutiveSummary(),
        calculated_value: valuationResults?.calculated_value || 0,
        asset_value: valuationResults?.asset_value || 0,
        ebitda_multiple: valuationResults?.ebitda_multiple || 0,
        method: valuationResults?.method || 'Standard Valuation',
        swot_analysis: swotAnalysis,
        company_data: companyData,
        valuation_results: valuationResults
      };

      const response = await generateReport(reportData);
      
      if (response && response.report_filename) {
        setGeneratedReports(prev => [...prev, {
          filename: response.report_filename,
          format: reportFormat,
          generated_at: new Date().toLocaleString(),
          download_url: response.download_url || `/api/report/download/${response.report_filename}`
        }]);
        
        toast.success('Report generated successfully!');
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('📄 Report generation error:', error);
      toast.error('Failed to generate report: ' + error.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleDownloadReport = async (filename) => {
    try {
      console.log('📄 Downloading report:', filename);
      
      // Use the API service to download the report
      const response = await downloadReport(filename);
      
      // Create blob URL for download
      const blob = new Blob([response], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      
      // Create download link
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      link.style.display = 'none';
      
      // Add to DOM, click, and remove
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Clean up the blob URL
      window.URL.revokeObjectURL(url);
      
      toast.success('Report downloaded successfully!');
    } catch (error) {
      console.error('📄 Download error:', error);
      toast.error('Failed to download report: ' + error.message);
    }
  };

  const generateExecutiveSummary = () => {
    const company = companyData.company_name || 'The Company';
    const revenue = companyData.revenue || 0;
    const calculatedValue = valuationResults?.calculated_value || 0;
    const method = valuationResults?.method || 'Standard Valuation';
    
    return `${company} is a ${companyData.industry || 'business'} company with annual revenue of $${revenue.toLocaleString()}. Based on our comprehensive analysis using ${method}, we estimate the fair market value to be approximately $${calculatedValue.toLocaleString()}.`;
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
                      <td>Calculated Value:</td>
                      <td><strong>{formatCurrency(valuationResults?.calculated_value || 0)}</strong></td>
                    </tr>
                    <tr>
                      <td>Asset Value:</td>
                      <td>{formatCurrency(valuationResults?.asset_value || 0)}</td>
                    </tr>
                    <tr>
                      <td>EBITDA Multiple:</td>
                      <td>{valuationResults?.ebitda_multiple || 0}x</td>
                    </tr>
                    <tr>
                      <td>Method:</td>
                      <td>{valuationResults?.method || 'Standard Valuation'}</td>
                    </tr>
                  </tbody>
                </table>
                
                <p className="mt-3">
                  <strong>Executive Summary:</strong> {generateExecutiveSummary()}
                </p>
              </div>
            </div>

            {/* Report Format Note */}
            <div className="mb-4">
              <div className="alert alert-info">
                <h6 className="mb-2">📄 Report Format</h6>
                <p className="mb-0">
                  Reports are generated as <strong>.txt files</strong> for maximum compatibility and to prevent file corruption issues. 
                  You can easily convert them to PDF, Word, or Excel format using any text editor or online converter.
                </p>
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