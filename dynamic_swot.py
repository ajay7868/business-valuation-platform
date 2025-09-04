#!/usr/bin/env python3
"""
Dynamic SWOT Analysis with OpenAI Integration
"""

import openai
import json
import os
from datetime import datetime

class DynamicSWOTAnalyzer:
    def __init__(self):
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def generate_industry_context(self, industry, revenue, ebitda_margin):
        """Generate industry-specific context and benchmarks"""
        industry_contexts = {
            'Technology': {
                'avg_ebitda_margin': 15,
                'avg_revenue_growth': 20,
                'key_metrics': ['R&D investment', 'user acquisition cost', 'churn rate'],
                'trends': ['AI/ML adoption', 'cloud migration', 'cybersecurity focus']
            },
            'Manufacturing': {
                'avg_ebitda_margin': 12,
                'avg_revenue_growth': 5,
                'key_metrics': ['production efficiency', 'supply chain optimization', 'quality control'],
                'trends': ['Industry 4.0', 'sustainability', 'automation']
            },
            'Healthcare': {
                'avg_ebitda_margin': 18,
                'avg_revenue_growth': 8,
                'key_metrics': ['patient outcomes', 'regulatory compliance', 'cost per patient'],
                'trends': ['telemedicine', 'AI diagnostics', 'personalized medicine']
            },
            'Retail': {
                'avg_ebitda_margin': 8,
                'avg_revenue_growth': 3,
                'key_metrics': ['inventory turnover', 'customer acquisition', 'same-store sales'],
                'trends': ['e-commerce growth', 'omnichannel', 'sustainability']
            },
            'Financial Services': {
                'avg_ebitda_margin': 25,
                'avg_revenue_growth': 6,
                'key_metrics': ['net interest margin', 'loan loss provisions', 'capital adequacy'],
                'trends': ['fintech disruption', 'digital banking', 'regulatory changes']
            }
        }
        
        return industry_contexts.get(industry, {
            'avg_ebitda_margin': 10,
            'avg_revenue_growth': 5,
            'key_metrics': ['operational efficiency', 'market share', 'customer satisfaction'],
            'trends': ['digital transformation', 'sustainability', 'innovation']
        })
    
    def create_swot_prompt(self, company_data, financial_metrics, industry_context):
        """Create a comprehensive prompt for OpenAI SWOT analysis"""
        
        prompt = f"""
You are a senior business analyst and strategic consultant. Analyze the following company data and provide a comprehensive, actionable SWOT analysis.

COMPANY INFORMATION:
- Company Name: {company_data.get('company_name', 'Unknown')}
- Industry: {company_data.get('industry', 'General')}
- Revenue: ${company_data.get('revenue', 0):,.0f}
- EBITDA: ${company_data.get('ebitda', 0):,.0f}
- Net Income: ${company_data.get('net_income', 0):,.0f}
- Total Assets: ${company_data.get('total_assets', 0):,.0f}
- Total Liabilities: ${company_data.get('total_liabilities', 0):,.0f}
- Employees: {company_data.get('employees', 0):,}

FINANCIAL METRICS:
- EBITDA Margin: {financial_metrics.get('ebitda_margin', 0):.1f}%
- Net Margin: {financial_metrics.get('net_margin', 0):.1f}%
- Gross Margin: {financial_metrics.get('gross_margin', 0):.1f}%
- Operating Margin: {financial_metrics.get('operating_margin', 0):.1f}%
- Debt-to-Assets: {financial_metrics.get('debt_to_assets', 0):.1f}%
- Debt-to-Equity: {financial_metrics.get('debt_to_equity', 0):.1f}%
- Revenue per Employee: ${financial_metrics.get('revenue_per_employee', 0):,.0f}
- Current Ratio: {financial_metrics.get('current_ratio', 0):.1f}
- Return on Assets: {financial_metrics.get('roa', 0):.1f}%
- Return on Equity: {financial_metrics.get('roe', 0):.1f}%
- Asset Turnover: {financial_metrics.get('asset_turnover', 0):.1f}x

INDUSTRY CONTEXT:
- Industry Average EBITDA Margin: {industry_context.get('avg_ebitda_margin', 10)}%
- Industry Average Revenue Growth: {industry_context.get('avg_revenue_growth', 5)}%
- Key Industry Metrics: {', '.join(industry_context.get('key_metrics', []))}
- Industry Trends: {', '.join(industry_context.get('trends', []))}

Please provide a detailed SWOT analysis in the following JSON format:

{{
    "strengths": [
        "Specific strength with supporting data/metrics",
        "Another strength with context"
    ],
    "weaknesses": [
        "Specific weakness with supporting data/metrics", 
        "Another weakness with context"
    ],
    "opportunities": [
        "Specific opportunity with market context",
        "Another opportunity with growth potential"
    ],
    "threats": [
        "Specific threat with risk assessment",
        "Another threat with impact analysis"
    ],
    "strategic_recommendations": [
        "Actionable recommendation 1",
        "Actionable recommendation 2"
    ],
    "key_risks": [
        "Primary risk with mitigation strategy",
        "Secondary risk with monitoring approach"
    ],
    "competitive_positioning": "Overall competitive position assessment",
    "growth_potential": "Growth potential analysis with supporting factors"
}}

Requirements:
1. Be specific and data-driven in your analysis
2. Compare metrics against industry benchmarks
3. Consider current market trends and conditions
4. Provide actionable insights, not generic statements
5. Focus on strategic implications for business decisions
6. Ensure each point is supported by the financial data provided
7. Consider both internal capabilities and external market factors

Respond ONLY with valid JSON. Do not include any explanatory text outside the JSON structure.
"""
        return prompt
    
    def parse_openai_response(self, response_text):
        """Parse OpenAI response and extract SWOT data"""
        try:
            # Clean the response text
            response_text = response_text.strip()
            
            # Remove any markdown formatting
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            # Parse JSON
            swot_data = json.loads(response_text)
            
            # Validate required fields
            required_fields = ['strengths', 'weaknesses', 'opportunities', 'threats']
            for field in required_fields:
                if field not in swot_data:
                    swot_data[field] = []
            
            return swot_data
            
        except json.JSONDecodeError as e:
            print(f"Error parsing OpenAI response: {e}")
            return None
        except Exception as e:
            print(f"Error processing OpenAI response: {e}")
            return None
    
    def generate_dynamic_swot(self, company_data, financial_metrics):
        """Generate dynamic SWOT analysis using OpenAI"""
        
        if not self.openai_api_key:
            print("OpenAI API key not found, falling back to rule-based analysis")
            return None
        
        try:
            # Get industry context
            industry = company_data.get('industry', 'General')
            revenue = company_data.get('revenue', 0)
            ebitda_margin = financial_metrics.get('ebitda_margin', 0)
            industry_context = self.generate_industry_context(industry, revenue, ebitda_margin)
            
            # Create prompt
            prompt = self.create_swot_prompt(company_data, financial_metrics, industry_context)
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a senior business analyst specializing in strategic analysis and SWOT assessments. Provide detailed, data-driven insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            # Extract response
            response_text = response['choices'][0]['message']['content']
            
            # Parse response
            swot_data = self.parse_openai_response(response_text)
            
            if swot_data:
                # Add metadata
                swot_data['generated_at'] = datetime.now().isoformat()
                swot_data['analysis_type'] = 'AI-Generated'
                swot_data['model_used'] = 'gpt-3.5-turbo'
                
                return swot_data
            else:
                print("Failed to parse OpenAI response")
                return None
                
        except Exception as e:
            print(f"Error generating dynamic SWOT: {e}")
            return None

# Global instance
swot_analyzer = DynamicSWOTAnalyzer()
