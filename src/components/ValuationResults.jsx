import React from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

function ValuationResults({ results, swotAnalysis, onNext, onPrev }) {
  if (!results) {
    return (
      <div className="text-center">
        <h5>No valuation results available</h5>
        <p>Please complete the valuation process first.</p>
        <button className="btn btn-secondary" onClick={onPrev}>
          Go Back
        </button>
      </div>
    );
  }

  const valuationData = {
    labels: ['Asset-Based', 'DCF Value', 'Revenue Multiple', 'EBITDA Multiple'],
    datasets: [
      {
        data: [
          results.asset_based || 0,
          results.income_based?.dcf_value || 0,
          results.market_based?.revenue_multiple || 0,
          results.market_based?.ebitda_multiple || 0
        ],
        backgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0'
        ],
        hoverBackgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0'
        ]
      }
    ]
  };

  const rangeData = {
    labels: ['Low', 'Mid', 'High'],
    datasets: [
      {
        label: 'Valuation Range',
        data: [
          results.valuation_range?.low || 0,
          results.valuation_range?.mid || 0,
          results.valuation_range?.high || 0
        ],
        backgroundColor: ['#FF6384', '#36A2EB', '#4BC0C0'],
      }
    ]
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
      <div className="col-12">
        {/* Valuation Range Cards */}
        <div className="row mb-4">
          <div className="col-md-4">
            <div className="card valuation-card text-white">
              <div className="card-body text-center">
                <div className="valuation-amount">
                  {formatCurrency(results.valuation_range?.low || 0)}
                </div>
                <div className="valuation-label">Low Estimate</div>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card valuation-card text-white">
              <div className="card-body text-center">
                <div className="valuation-amount">
                  {formatCurrency(results.valuation_range?.mid || 0)}
                </div>
                <div className="valuation-label">Mid Estimate</div>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card valuation-card text-white">
              <div className="card-body text-center">
                <div className="valuation-amount">
                  {formatCurrency(results.valuation_range?.high || 0)}
                </div>
                <div className="valuation-label">High Estimate</div>
              </div>
            </div>
          </div>
        </div>

        {/* Charts */}
        <div className="row mb-4">
          <div className="col-md-6">
            <div className="card">
              <div className="card-header">
                <h6>Valuation Methods Breakdown</h6>
              </div>
              <div className="card-body">
                <Doughnut data={valuationData} />
              </div>
            </div>
          </div>
          <div className="col-md-6">
            <div className="card">
              <div className="card-header">
                <h6>Valuation Range</h6>
              </div>
              <div className="card-body">
                <Bar data={rangeData} />
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Results */}
        <div className="row mb-4">
          <div className="col-md-6">
            <div className="card">
              <div className="card-header">
                <h6>Valuation Methods Detail</h6>
              </div>
              <div className="card-body">
                <table className="table table-sm">
                  <tbody>
                    <tr>
                      <td><strong>Asset-Based Value:</strong></td>
                      <td>{formatCurrency(results.asset_based || 0)}</td>
                    </tr>
                    <tr>
                      <td><strong>DCF Value:</strong></td>
                      <td>{formatCurrency(results.income_based?.dcf_value || 0)}</td>
                    </tr>
                    <tr>
                      <td><strong>Revenue Multiple:</strong></td>
                      <td>{formatCurrency(results.market_based?.revenue_multiple || 0)}</td>
                    </tr>
                    <tr>
                      <td><strong>EBITDA Multiple:</strong></td>
                      <td>{formatCurrency(results.market_based?.ebitda_multiple || 0)}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          <div className="col-md-6">
            <div className="card">
              <div className="card-header">
                <h6>Key Assumptions</h6>
              </div>
              <div className="card-body">
                {results.methodology_notes?.assumptions && (
                  <ul className="list-unstyled">
                    {results.methodology_notes.assumptions.map((assumption, index) => (
                      <li key={index}>• {assumption}</li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* SWOT Analysis */}
        {swotAnalysis && (
          <div className="row mb-4">
            <div className="col-12">
              <div className="card">
                <div className="card-header">
                  <h6>SWOT Analysis</h6>
                </div>
                <div className="card-body">
                  <div className="row">
                    <div className="col-md-6">
                      <div className="swot-section strengths">
                        <h6 className="text-success">Strengths</h6>
                        {swotAnalysis.strengths?.map((item, index) => (
                          <div key={index} className="swot-item">{item}</div>
                        ))}
                      </div>
                      <div className="swot-section opportunities">
                        <h6 className="text-info">Opportunities</h6>
                        {swotAnalysis.opportunities?.map((item, index) => (
                          <div key={index} className="swot-item">{item}</div>
                        ))}
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="swot-section weaknesses">
                        <h6 className="text-danger">Weaknesses</h6>
                        {swotAnalysis.weaknesses?.map((item, index) => (
                          <div key={index} className="swot-item">{item}</div>
                        ))}
                      </div>
                      <div className="swot-section threats">
                        <h6 className="text-warning">Threats</h6>
                        {swotAnalysis.threats?.map((item, index) => (
                          <div key={index} className="swot-item">{item}</div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Anomalies */}
        {results.anomalies && results.anomalies.length > 0 && (
          <div className="row mb-4">
            <div className="col-12">
              <div className="card border-warning">
                <div className="card-header bg-warning">
                  <h6 className="mb-0">⚠️ Anomalies Detected</h6>
                </div>
                <div className="card-body">
                  <ul className="list-unstyled mb-0">
                    {results.anomalies.map((anomaly, index) => (
                      <li key={index} className="mb-2">
                        <i className="fas fa-exclamation-triangle text-warning mr-2"></i>
                        {anomaly}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="row">
          <div className="col-12">
            <div className="d-flex justify-content-between">
              <button className="btn btn-secondary" onClick={onPrev}>
                Previous
              </button>
              <button className="btn btn-primary" onClick={onNext}>
                Generate Report
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ValuationResults;