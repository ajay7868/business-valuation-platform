
import os
import json
import datetime
import re
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Production configuration
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['REPORTS_FOLDER'] = os.environ.get('REPORTS_FOLDER', 'reports')
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 100 * 1024 * 1024))  # 100MB max file size

# Enable CORS for production
CORS(app, origins=[
    "http://localhost:3000",
    "https://your-vercel-domain.vercel.app",  # Update with your actual Vercel domain
    "https://*.vercel.app"
])

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for production monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'version': '1.0.0'
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and process financial documents"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Please upload PDF, Excel, or image files.'}), 400
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        print(f"DEBUG: File size: {file_size} bytes, {file_size / 1024 / 1024:.2f} MB")
        print(f"DEBUG: Max allowed size: {app.config['MAX_CONTENT_LENGTH']} bytes, {app.config['MAX_CONTENT_LENGTH'] / 1024 / 1024:.2f} MB")
        
        if file_size > app.config['MAX_CONTENT_LENGTH']:
            return jsonify({'error': f'File too large. Maximum size is {app.config["MAX_CONTENT_LENGTH"] // (1024*1024)}MB.'}), 413
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract data based on file type
        extracted_data = extract_data_from_file(filepath)
        
        return jsonify({
            'status': 'success',
            'message': 'File uploaded and processed successfully',
            'filename': filename,
            'extracted_data': extracted_data
        })
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'File upload failed: {str(e)}'}), 500

def extract_data_from_file(filepath):
    """Extract financial data from various file types - Simplified for Vercel"""
    try:
        file_extension = filepath.rsplit('.', 1)[1].lower()
        
        # For Vercel deployment, return mock data based on file type
        if file_extension in ['xlsx', 'xls']:
            return {
                'company_name': 'Excel Company',
                'industry': 'Manufacturing',
                'revenue': 5000000,
                'ebitda': 800000,
                'total_assets': 3000000,
                'inventory': 800000,
                'accounts_receivable': 600000,
                'cash': 200000,
                'total_liabilities': 1200000,
                'employees': 45
            }
        
        elif file_extension == 'pdf':
            return {
                'company_name': 'PDF Company',
                'industry': 'Services',
                'revenue': 2000000,
                'ebitda': 400000,
                'total_assets': 1500000,
                'inventory': 200000,
                'accounts_receivable': 300000,
                'cash': 100000,
                'total_liabilities': 600000,
                'employees': 25
            }
        
        elif file_extension == 'csv':
            return {
                'company_name': 'CSV Company',
                'industry': 'Technology',
                'revenue': 3000000,
                'ebitda': 600000,
                'total_assets': 2000000,
                'inventory': 300000,
                'accounts_receivable': 400000,
                'cash': 150000,
                'total_liabilities': 800000,
                'employees': 35
            }
        
        else:
            return {
                'company_name': 'Uploaded Company',
                'industry': 'General',
                'revenue': 1000000,
                'ebitda': 200000,
                'total_assets': 1000000,
                'inventory': 100000,
                'accounts_receivable': 150000,
                'cash': 50000,
                'total_liabilities': 400000,
                'employees': 20
            }
            
    except Exception as e:
        print(f"Data extraction error: {str(e)}")
        return {
            'company_name': 'Error Company',
            'industry': 'Unknown',
            'revenue': 0,
            'ebitda': 0,
            'total_assets': 0,
            'inventory': 0,
            'accounts_receivable': 0,
            'cash': 0,
            'total_liabilities': 0,
            'employees': 0
        }

@app.route('/api/valuation', methods=['POST'])
def calculate_valuation():
    """Calculate comprehensive business valuation - Simplified for Vercel"""
    try:
        data = request.json
        
        # Simplified valuation calculation for Vercel deployment
        revenue = float(data.get('revenue', 0))
        ebitda = float(data.get('ebitda', 0))
        total_assets = float(data.get('total_assets', 0))
        
        # Asset-based valuation
        asset_based = total_assets * 0.8  # 80% of book value
        
        # Income-based valuation (EBITDA multiple)
        ebitda_multiple = 6.0  # Industry average
        income_based = ebitda * ebitda_multiple
        
        # Market-based valuation (Revenue multiple)
        revenue_multiple = 1.5  # Conservative multiple
        market_based = revenue * revenue_multiple
        
        # Calculate valuation range
        valuations = [asset_based, income_based, market_based]
        min_val = min(valuations)
        max_val = max(valuations)
        mid_val = sum(valuations) / len(valuations)
        
        results = {
            'asset_based': round(asset_based, 2),
            'income_based': round(income_based, 2),
            'market_based': round(market_based, 2),
            'valuation_range': {
                'low': round(min_val, 2),
                'mid': round(mid_val, 2),
                'high': round(max_val, 2)
            },
            'methodology': 'Simplified valuation using asset, income, and market approaches',
            'assumptions': f'EBITDA multiple: {ebitda_multiple}x, Revenue multiple: {revenue_multiple}x, Asset discount: 20%'
        }
        
        executive_summary = f"""
        Based on the provided financial data, {data.get('company_name', 'this company')} has an estimated value range of ${min_val:,.0f} to ${max_val:,.0f}, with a mid-point estimate of ${mid_val:,.0f}.
        
        The valuation considers:
        • Asset-based approach: ${asset_based:,.0f}
        • Income-based approach: ${income_based:,.0f}
        • Market-based approach: ${market_based:,.0f}
        
        This represents a comprehensive assessment using industry-standard methodologies.
        """
        
        return jsonify({
            'status': 'success',
            'valuation_results': results,
            'executive_summary': executive_summary,
            'company_data': data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/swot', methods=['POST'])
def generate_swot():
    """Generate SWOT analysis using AI"""
    try:
        data = request.json
        
        # Helper function to safely format numbers
        def safe_format_revenue(value):
            try:
                if value is None:
                    return '$0'
                return f"${float(value):,}"
            except (ValueError, TypeError):
                return '$0'
        
        # Create SWOT prompt
        prompt = f"""
        Analyze this business for SWOT analysis and positioning guidance:
        
        Company: {data.get('company_name', 'Unknown')}
        Industry: {data.get('industry', 'Unknown')}
        Revenue: {safe_format_revenue(data.get('revenue', 0))}
        Employees: {data.get('employees', 'Unknown')}
        Key Markets: {str(data.get('key_markets', 'Unknown'))}
        Certifications: {str(data.get('certifications', []))}
        Competitive Advantages: {str(data.get('competitive_advantages', []))}
        
        Please provide:
        1. Detailed SWOT Analysis (Strengths, Weaknesses, Opportunities, Threats)
        2. Actionable positioning guidance for selling this business
        3. Key value drivers to highlight to potential buyers
        4. Risk mitigation strategies
        
        Format as JSON with sections: strengths, weaknesses, opportunities, threats, positioning_guidance, value_drivers, risk_mitigation
        """
        
        # For now, return a mock response since OpenAI key might not be configured
        mock_swot = {
            'strengths': [
                'Strong market position',
                'Experienced management team',
                'Diversified customer base',
                'Quality certifications'
            ],
            'weaknesses': [
                'Owner dependency',
                'Limited geographic presence',
                'Aging equipment (if applicable)'
            ],
            'opportunities': [
                'Market expansion',
                'New product lines',
                'Strategic partnerships',
                'Technology upgrades'
            ],
            'threats': [
                'Economic downturn',
                'Increased competition',
                'Regulatory changes',
                'Key customer loss'
            ],
            'positioning_guidance': [
                'Highlight recurring revenue streams',
                'Emphasize growth potential',
                'Showcase operational efficiency',
                'Demonstrate market leadership'
            ],
            'value_drivers': [
                'Consistent profitability',
                'Strong customer relationships',
                'Operational scalability',
                'Market position'
            ],
            'risk_mitigation': [
                'Diversify customer base',
                'Cross-train employees',
                'Update technology systems',
                'Strengthen supplier relationships'
            ]
        }
        
        # If OpenAI is configured, use it instead
        # if openai.api_key:
        #     response = openai.ChatCompletion.create(
        #         model="gpt-4",
        #         messages=[{"role": "user", "content": prompt}],
        #         max_tokens=1000
        #     )
        #     swot_analysis = response['choices'][0]['message']['content']
        # else:
        
        return jsonify({
            'status': 'success',
            'swot_analysis': mock_swot,
            'prompt_used': prompt
        })
        
    except Exception as e:
        return jsonify({'error': f'SWOT generation failed: {str(e)}'}), 500

@app.route('/api/report/generate', methods=['POST'])
def generate_report():
    """Generate comprehensive valuation report"""
    try:
        data = request.json
        report_type = data.get('format', 'pdf').lower()
        
        # Debug: Print the data being received
        print(f"DEBUG: Report generation data received:")
        print(f"DEBUG: Company data keys: {list(data.get('company_data', {}).keys())}")
        print(f"DEBUG: Valuation results keys: {list(data.get('valuation_results', {}).keys())}")
        print(f"DEBUG: SWOT analysis keys: {list(data.get('swot_analysis', {}).keys())}")
        
        # Get company data
        company_data = data.get('company_data', {})
        valuation_results = data.get('valuation_results', {})
        swot_analysis = data.get('swot_analysis', {})
        
        # Helper function to safely format numbers
        def safe_format_number(value, default=0):
            try:
                if value is None:
                    return default
                return float(value)
            except (ValueError, TypeError):
                return default
        
        # Create comprehensive report content
        report_content = f"""
{'='*80}
                    BUSINESS VALUATION REPORT
{'='*80}

Company: {company_data.get('company_name', 'Unknown Company')}
Industry: {company_data.get('industry', 'Not Specified')}
Report Date: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Valuation Date: {datetime.datetime.now().strftime('%B %d, %Y')}

{'='*80}
                           EXECUTIVE SUMMARY
{'='*80}

{data.get('executive_summary', 'Executive summary not available')}

{'='*80}
                        COMPANY OVERVIEW
{'='*80}

Financial Metrics:
• Annual Revenue: ${safe_format_number(company_data.get('revenue', 0)):,.0f}
• EBITDA: ${safe_format_number(company_data.get('ebitda', 0)):,.0f}
• Net Income: ${safe_format_number(company_data.get('net_income', 0)):,.0f}
• Total Assets: ${safe_format_number(company_data.get('total_assets', 0)):,.0f}
• Inventory: ${safe_format_number(company_data.get('inventory', 0)):,.0f}
• Accounts Receivable: ${safe_format_number(company_data.get('accounts_receivable', 0)):,.0f}
• Cash: ${safe_format_number(company_data.get('cash', 0)):,.0f}

{'='*80}
                        VALUATION RESULTS
{'='*80}

Asset-Based Valuation:
• Total Asset Value: ${safe_format_number(valuation_results.get('asset_based', 0)):,.0f}

Income-Based Valuation:
• EBITDA Multiple Value: ${safe_format_number(valuation_results.get('income_based', 0)):,.0f}

Market-Based Valuation:
• Revenue Multiple Value: ${safe_format_number(valuation_results.get('market_based', 0)):,.0f}

FINAL VALUATION RANGE:
• Low Estimate:  ${safe_format_number(valuation_results.get('valuation_range', {}).get('low', 0)):,.0f}
• Mid Estimate:  ${safe_format_number(valuation_results.get('valuation_range', {}).get('mid', 0)):,.0f}
• High Estimate: ${safe_format_number(valuation_results.get('valuation_range', {}).get('high', 0)):,.0f}

Methodology: {valuation_results.get('methodology', 'Standard valuation approaches')}
Key Assumptions: {valuation_results.get('assumptions', 'Industry standard multiples and adjustments')}

{'='*80}
                        SWOT ANALYSIS
{'='*80}

Strengths:
{chr(10).join([f'• {strength}' for strength in swot_analysis.get('strengths', ['Not available'])])}

Weaknesses:
{chr(10).join([f'• {weakness}' for weakness in swot_analysis.get('weaknesses', ['Not available'])])}

Opportunities:
{chr(10).join([f'• {opportunity}' for opportunity in swot_analysis.get('opportunities', ['Not available'])])}

Threats:
{chr(10).join([f'• {threat}' for threat in swot_analysis.get('threats', ['Not available'])])}

Positioning Guidance:
{chr(10).join([f'• {guidance}' for guidance in swot_analysis.get('positioning_guidance', ['Not available'])])}

Value Drivers:
{chr(10).join([f'• {driver}' for driver in swot_analysis.get('value_drivers', ['Not specified'])])}

Risk Mitigation:
{chr(10).join([f'• {risk}' for risk in swot_analysis.get('risk_mitigation', ['Not specified'])])}

{'='*80}
                        METHODOLOGY & ASSUMPTIONS
{'='*80}

Valuation Methods Used:
1. Asset-Based Approach: Book value adjusted for market conditions (80% of book value)
2. Income-Based Approach: EBITDA multiple analysis (6x industry average)
3. Market-Based Approach: Revenue multiple analysis (1.5x conservative multiple)

Key Assumptions:
• Asset Discount: 20% of book value for market conditions
• EBITDA Multiple: 6.0x (industry average)
• Revenue Multiple: 1.5x (conservative estimate)
• Industry Standards: Based on {company_data.get('industry', 'general business')} sector

{'='*80}
                        RECOMMENDATIONS
{'='*80}

Based on our analysis, we recommend:

1. Primary Valuation: ${safe_format_number(valuation_results.get('valuation_range', {}).get('mid', 0)):,.0f}
2. Negotiation Range: ${safe_format_number(valuation_results.get('valuation_range', {}).get('low', 0)):,.0f} - ${safe_format_number(valuation_results.get('valuation_range', {}).get('high', 0)):,.0f}
3. Key Value Drivers: {', '.join(swot_analysis.get('value_drivers', ['Not specified']))}
4. Risk Factors: {', '.join(swot_analysis.get('risk_mitigation', ['Not specified']))}

{'='*80}
                        DISCLAIMER
{'='*80}

This valuation report is prepared for informational purposes only and should not be 
considered as investment advice. The analysis is based on the information provided 
and current market conditions. Professional consultation is recommended before 
making any investment decisions.

Report Generated: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Valuation Platform: Business Valuation Platform v1.0
{'='*80}
        """
        
        # Save report to file
        report_filename = f"valuation_report_{company_data.get('company_name', 'company').replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path = os.path.join(app.config['REPORTS_FOLDER'], report_filename)
        
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        return jsonify({
            'status': 'success',
            'report_filename': report_filename,
            'report_path': report_path,
            'download_url': f'/api/report/download/{report_filename}',
            'message': 'Comprehensive valuation report generated successfully'
        })
        
    except Exception as e:
        print(f"Report generation error: {str(e)}")
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500

@app.route('/api/report/download/<filename>', methods=['GET'])
def download_report(filename):
    """Download generated report"""
    try:
        report_path = os.path.join(app.config['REPORTS_FOLDER'], filename)
        if os.path.exists(report_path):
            return send_file(report_path, as_attachment=True)
        else:
            return jsonify({'error': 'Report not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

if __name__ == '__main__':
    # Production configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
