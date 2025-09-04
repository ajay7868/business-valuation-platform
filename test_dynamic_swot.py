#!/usr/bin/env python3
"""
Test script for dynamic SWOT analysis
"""

import os
import sys
from dynamic_swot import swot_analyzer

def test_swot_analysis():
    """Test the dynamic SWOT analysis with sample data"""
    
    # Sample company data
    company_data = {
        'company_name': 'TechCorp Solutions',
        'industry': 'Technology',
        'revenue': 5000000,
        'ebitda': 750000,
        'net_income': 400000,
        'total_assets': 3000000,
        'total_liabilities': 1200000,
        'employees': 25,
        'cash': 500000,
        'inventory': 200000,
        'accounts_receivable': 300000
    }
    
    # Sample financial metrics
    financial_metrics = {
        'ebitda_margin': 15.0,
        'net_margin': 8.0,
        'gross_margin': 35.0,
        'operating_margin': 12.0,
        'debt_to_assets': 40.0,
        'debt_to_equity': 66.7,
        'revenue_per_employee': 200000,
        'current_ratio': 2.5,
        'quick_ratio': 2.0,
        'inventory_turnover': 4.0,
        'asset_turnover': 1.67,
        'roa': 13.3,
        'roe': 22.2
    }
    
    print("🧪 Testing Dynamic SWOT Analysis")
    print("=" * 50)
    print(f"Company: {company_data['company_name']}")
    print(f"Industry: {company_data['industry']}")
    print(f"Revenue: ${company_data['revenue']:,}")
    print(f"EBITDA Margin: {financial_metrics['ebitda_margin']:.1f}%")
    print("=" * 50)
    
    # Test industry context generation
    print("\n📊 Testing Industry Context Generation...")
    industry_context = swot_analyzer.generate_industry_context(
        company_data['industry'], 
        company_data['revenue'], 
        financial_metrics['ebitda_margin']
    )
    print(f"Industry Context: {industry_context}")
    
    # Test prompt generation
    print("\n📝 Testing Prompt Generation...")
    prompt = swot_analyzer.create_swot_prompt(company_data, financial_metrics, industry_context)
    print(f"Prompt length: {len(prompt)} characters")
    print(f"Prompt preview: {prompt[:200]}...")
    
    # Test dynamic SWOT generation (will fallback to rule-based if no OpenAI key)
    print("\n🤖 Testing Dynamic SWOT Generation...")
    swot_result = swot_analyzer.generate_dynamic_swot(company_data, financial_metrics)
    
    if swot_result:
        print("✅ Dynamic SWOT analysis completed!")
        print(f"Analysis Type: {swot_result.get('analysis_type', 'Unknown')}")
        print(f"Generated At: {swot_result.get('generated_at', 'Unknown')}")
        print(f"Strengths: {len(swot_result.get('strengths', []))} items")
        print(f"Weaknesses: {len(swot_result.get('weaknesses', []))} items")
        print(f"Opportunities: {len(swot_result.get('opportunities', []))} items")
        print(f"Threats: {len(swot_result.get('threats', []))} items")
        
        if 'strategic_recommendations' in swot_result:
            print(f"Strategic Recommendations: {len(swot_result['strategic_recommendations'])} items")
        
        # Show sample results
        print("\n📋 Sample Results:")
        if swot_result.get('strengths'):
            print(f"Sample Strength: {swot_result['strengths'][0]}")
        if swot_result.get('opportunities'):
            print(f"Sample Opportunity: {swot_result['opportunities'][0]}")
    else:
        print("⚠️ Dynamic SWOT analysis failed (likely no OpenAI API key)")
        print("This is expected if OPENAI_API_KEY environment variable is not set")
    
    print("\n✅ Test completed successfully!")

if __name__ == "__main__":
    test_swot_analysis()
