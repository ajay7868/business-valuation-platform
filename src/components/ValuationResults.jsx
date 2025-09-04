import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

function ValuationResults({ 
  valuationResults, 
  companyData, 
  swotAnalysis, 
  onPrev, 
  onNext 
}) {
  if (!valuationResults) {
    return (
      <div className="container mt-4">
        <div className="row justify-content-center">
          <div className="col-md-8">
            <div className="card">
              <div className="card-body text-center">
                <h5>No Valuation Results Available</h5>
                <p className="text-muted">Please generate a valuation first.</p>
                <button className="btn btn-primary" onClick={onPrev}>
                  Go Back to Dashboard
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <div className="row">
        <div className="col-12">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2>📊 Valuation Results & Analysis</h2>
            <div className="d-flex gap-2">
              <button className="btn btn-outline-secondary" onClick={onPrev}>
                ← Back to Dashboard
              </button>
              {onNext && (
                <button className="btn btn-primary" onClick={onNext}>
                  Continue →
                </button>
              )}
            </div>
          </div>

          {/* Valuation Summary Card */}
          <div className="card mb-4">
            <div className="card-header bg-success text-white">
              <h5 className="mb-0">💰 Valuation Summary</h5>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-6">
                  <h6>Company: {valuationResults.company_name}</h6>
                  <p className="mb-2"><strong>Calculated Value:</strong> ${valuationResults.calculated_value.toLocaleString()}</p>
                  <p className="mb-2"><strong>Method:</strong> {valuationResults.method}</p>
                  {valuationResults.ebitda_multiple && (
                    <p className="mb-2"><strong>EBITDA Multiple:</strong> {valuationResults.ebitda_multiple}x</p>
                  )}
                  {valuationResults.asset_value && (
                    <p className="mb-2"><strong>Asset Value:</strong> ${valuationResults.asset_value.toLocaleString()}</p>
                  )}
                </div>
                <div className="col-md-6">
                  <p className="mb-0 text-muted">
                    <small>Calculated: {new Date(valuationResults.calculated_at).toLocaleString()}</small>
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Valuation Charts */}
          <div className="row mb-4">
            <div className="col-md-6">
              <div className="card">
                <div className="card-header">
                  <h6>📈 Valuation Breakdown</h6>
                </div>
                <div className="card-body">
                  <Bar
                    data={{
                      labels: ['EBITDA Value', 'Asset Value', 'Final Value'],
                      datasets: [
                        {
                          label: 'Value ($)',
                          data: [
                            valuationResults.ebitda_multiple ? (companyData.ebitda || 0) * valuationResults.ebitda_multiple : 0,
                            valuationResults.asset_value || 0,
                            valuationResults.calculated_value
                          ],
                          backgroundColor: [
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 99, 132, 0.8)',
                            'rgba(75, 192, 192, 0.8)'
                          ],
                          borderColor: [
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 99, 132, 1)',
                            'rgba(75, 192, 192, 1)'
                          ],
                          borderWidth: 1
                        }
                      ]
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        title: {
                          display: true,
                          text: 'Valuation Components'
                        },
                        legend: {
                          display: false
                        }
                      },
                      scales: {
                        y: {
                          beginAtZero: true,
                          ticks: {
                            callback: function(value) {
                              return '$' + value.toLocaleString();
                            }
                          }
                        }
                      }
                    }}
                  />
                </div>
              </div>
            </div>
            
            <div className="col-md-6">
              <div className="card">
                <div className="card-header">
                  <h6>🥧 Value Distribution</h6>
                </div>
                <div className="card-body">
                  <Doughnut
                    data={{
                      labels: ['EBITDA Component', 'Asset Component'],
                      datasets: [
                        {
                          data: [
                            valuationResults.ebitda_multiple ? (companyData.ebitda || 0) * valuationResults.ebitda_multiple : 0,
                            valuationResults.asset_value || 0
                          ],
                          backgroundColor: [
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 99, 132, 0.8)'
                          ],
                          borderColor: [
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 99, 132, 1)'
                          ],
                          borderWidth: 1
                        }
                      ]
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        title: {
                          display: true,
                          text: 'Value Sources'
                        },
                        legend: {
                          position: 'bottom'
                        }
                      }
                    }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Financial Metrics Summary */}
          {companyData.revenue && (
            <div className="row mb-4">
              <div className="col-12">
                <div className="card">
                  <div className="card-header">
                    <h6>📊 Key Financial Metrics</h6>
                  </div>
                  <div className="card-body">
                    <div className="row">
                      <div className="col-md-3">
                        <div className="card bg-light">
                          <div className="card-body text-center">
                            <h6 className="card-title">Revenue</h6>
                            <p className="card-text h5 text-primary">
                              ${(companyData.revenue || 0).toLocaleString()}
                            </p>
                          </div>
                        </div>
                      </div>
                      <div className="col-md-3">
                        <div className="card bg-light">
                          <div className="card-body text-center">
                            <h6 className="card-title">EBITDA</h6>
                            <p className="card-text h5 text-success">
                              ${(companyData.ebitda || 0).toLocaleString()}
                            </p>
                          </div>
                        </div>
                      </div>
                      <div className="col-md-3">
                        <div className="card bg-light">
                          <div className="card-body text-center">
                            <h6 className="card-title">Assets</h6>
                            <p className="card-text h5 text-info">
                              ${(companyData.total_assets || 0).toLocaleString()}
                            </p>
                          </div>
                        </div>
                      </div>
                      <div className="col-md-3">
                        <div className="card bg-light">
                          <div className="card-body text-center">
                            <h6 className="card-title">Valuation</h6>
                            <p className="card-text h5 text-warning">
                              ${(valuationResults.calculated_value || 0).toLocaleString()}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* SWOT Analysis Results */}
          {swotAnalysis && (
            <div className="row mb-4">
              <div className="col-12">
                <div className="card">
                  <div className="card-header bg-info text-white">
                    <h6 className="mb-0">🧠 SWOT Analysis</h6>
                  </div>
                  <div className="card-body">
                    <div className="row">
                      <div className="col-md-6">
                        <h6 className="text-success">Strengths</h6>
                        <ul className="list-unstyled">
                          {swotAnalysis.strengths?.map((strength, index) => (
                            <li key={index} className="mb-1">
                              <span className="badge bg-success me-2">✓</span>
                              {strength}
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div className="col-md-6">
                        <h6 className="text-danger">Weaknesses</h6>
                        <ul className="list-unstyled">
                          {swotAnalysis.weaknesses?.map((weakness, index) => (
                            <li key={index} className="mb-1">
                              <span className="badge bg-danger me-2">⚠</span>
                              {weakness}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                    <div className="row mt-3">
                      <div className="col-md-6">
                        <h6 className="text-primary">Opportunities</h6>
                        <ul className="list-unstyled">
                          {swotAnalysis.opportunities?.map((opportunity, index) => (
                            <li key={index} className="mb-1">
                              <span className="badge bg-primary me-2">🚀</span>
                              {opportunity}
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div className="col-md-6">
                        <h6 className="text-warning">Threats</h6>
                        <ul className="list-unstyled">
                          {swotAnalysis.threats?.map((threat, index) => (
                            <li key={index} className="mb-1">
                              <span className="badge bg-warning me-2">⚠</span>
                              {threat}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="row">
            <div className="col-12">
              <div className="card">
                <div className="card-body text-center">
                  <h6>Next Steps</h6>
                  <p className="text-muted">Review your valuation results and SWOT analysis above.</p>
                  <div className="d-flex gap-2 justify-content-center">
                    <button className="btn btn-outline-secondary" onClick={onPrev}>
                      ← Back to Dashboard
                    </button>
                    {onNext && (
                <button className="btn btn-primary" onClick={onNext}>
                  Continue →
                </button>
              )}
                    {/* <button className="btn btn-success">
                      📄 Generate Report
                    </button>
                    <button className="btn btn-primary">
                      💾 Save Results
                    </button> */}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ValuationResults;