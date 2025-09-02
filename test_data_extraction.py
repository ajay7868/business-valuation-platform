#!/usr/bin/env python3
"""
Test script for enhanced data extraction functionality
This script demonstrates how the platform now extracts real data from various file types
"""

import os
import sys
import pandas as pd

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the extraction functions from app.py
from app import (
    extract_from_excel,
    extract_from_csv,
    extract_from_pdf,
    extract_company_info_from_dataframe,
    find_company_name,
    find_industry,
    extract_financial_metrics,
    find_employee_count
)

def create_test_excel():
    """Create a test Excel file with sample financial data"""
    print("📊 Creating test Excel file...")
    
    # Sample financial data
    data = {
        'Company Name': ['ABC Manufacturing Corp', '', '', '', ''],
        'Industry': ['Manufacturing', '', '', '', ''],
        'Revenue': ['$5,000,000', '', '', '', ''],
        'EBITDA': ['$800,000', '', '', '', ''],
        'Total Assets': ['$3,000,000', '', '', '', ''],
        'Inventory': ['$800,000', '', '', '', ''],
        'Accounts Receivable': ['$600,000', '', '', '', ''],
        'Cash': ['$200,000', '', '', '', ''],
        'Total Liabilities': ['$1,200,000', '', '', '', ''],
        'Employees': ['45', '', '', '', '']
    }
    
    df = pd.DataFrame(data)
    
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    
    # Save to Excel
    excel_path = 'uploads/test_financial_data.xlsx'
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Financial Summary', index=False)
        
        # Add another sheet with different data
        balance_sheet_data = {
            'Item': ['Cash', 'Accounts Receivable', 'Inventory', 'Total Current Assets', 'Fixed Assets', 'Total Assets'],
            'Amount': ['$200,000', '$600,000', '$800,000', '$1,600,000', '$1,400,000', '$3,000,000']
        }
        balance_df = pd.DataFrame(balance_sheet_data)
        balance_df.to_excel(writer, sheet_name='Balance Sheet', index=False)
    
    print(f"✅ Test Excel file created: {excel_path}")
    return excel_path

def create_test_csv():
    """Create a test CSV file with sample financial data"""
    print("📄 Creating test CSV file...")
    
    # Sample financial data
    data = {
        'Metric': ['Company Name', 'Industry', 'Revenue', 'EBITDA', 'Total Assets', 'Inventory', 'Accounts Receivable', 'Cash', 'Total Liabilities', 'Employees'],
        'Value': ['XYZ Technology Inc', 'Technology', '$3,000,000', '$600,000', '$2,000,000', '$300,000', '$400,000', '$150,000', '$800,000', '35']
    }
    
    df = pd.DataFrame(data)
    
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    
    # Save to CSV
    csv_path = 'uploads/test_financial_data.csv'
    df.to_csv(csv_path, index=False)
    
    print(f"✅ Test CSV file created: {csv_path}")
    return csv_path

def test_excel_extraction():
    """Test Excel file data extraction"""
    print("\n🔍 Testing Excel file extraction...")
    
    try:
        excel_path = create_test_excel()
        extracted_data = extract_from_excel(excel_path)
        
        print("📊 Extracted Excel Data:")
        for key, value in extracted_data.items():
            print(f"  {key}: {value}")
            
        return extracted_data
        
    except Exception as e:
        print(f"❌ Excel extraction failed: {str(e)}")
        return None

def test_csv_extraction():
    """Test CSV file data extraction"""
    print("\n🔍 Testing CSV file extraction...")
    
    try:
        csv_path = create_test_csv()
        extracted_data = extract_from_csv(csv_path)
        
        print("📄 Extracted CSV Data:")
        for key, value in extracted_data.items():
            print(f"  {key}: {value}")
            
        return extracted_data
        
    except Exception as e:
        print(f"❌ CSV extraction failed: {str(e)}")
        return None

def test_dataframe_extraction():
    """Test DataFrame data extraction directly"""
    print("\n🔍 Testing DataFrame extraction...")
    
    try:
        # Create sample DataFrame
        data = {
            'Company': ['Test Corp Inc', '', '', ''],
            'Sector': ['Manufacturing', '', '', ''],
            'Sales': ['$4,000,000', '', '', ''],
            'Operating Income': ['$700,000', '', '', ''],
            'Assets': ['$2,500,000', '', '', ''],
            'Staff': ['40', '', '', '']
        }
        
        df = pd.DataFrame(data)
        df_str = df.astype(str)
        
        # Extract company information
        company_data = extract_company_info_from_dataframe(df, df_str)
        
        print("📊 Extracted DataFrame Data:")
        for key, value in company_data.items():
            print(f"  {key}: {value}")
            
        return company_data
        
    except Exception as e:
        print(f"❌ DataFrame extraction failed: {str(e)}")
        return None

def test_individual_functions():
    """Test individual extraction functions"""
    print("\n🔍 Testing individual extraction functions...")
    
    try:
        # Create sample DataFrame
        data = {
            'Company Name': ['Sample Company LLC', '', '', ''],
            'Industry Type': ['Technology', '', '', ''],
            'Revenue Amount': ['$6,000,000', '', '', ''],
            'EBITDA Value': ['$1,000,000', '', '', ''],
            'Total Asset Value': ['$4,000,000', '', '', ''],
            'Employee Count': ['60', '', '', '']
        }
        
        df = pd.DataFrame(data)
        df_str = df.astype(str)
        
        print("🔍 Testing company name extraction...")
        company_name = find_company_name(df, df_str)
        print(f"  Company Name: {company_name}")
        
        print("🔍 Testing industry extraction...")
        industry = find_industry(df, df_str)
        print(f"  Industry: {industry}")
        
        print("🔍 Testing financial metrics extraction...")
        financial_metrics = extract_financial_metrics(df, df_str)
        print(f"  Financial Metrics: {financial_metrics}")
        
        print("🔍 Testing employee count extraction...")
        employees = find_employee_count(df, df_str)
        print(f"  Employees: {employees}")
        
    except Exception as e:
        print(f"❌ Individual function testing failed: {str(e)}")

def main():
    """Main test function"""
    print("🚀 Testing Enhanced Data Extraction Functionality")
    print("=" * 60)
    
    # Test Excel extraction
    excel_data = test_excel_extraction()
    
    # Test CSV extraction
    csv_data = test_csv_extraction()
    
    # Test DataFrame extraction
    df_data = test_dataframe_extraction()
    
    # Test individual functions
    test_individual_functions()
    
    print("\n" + "=" * 60)
    print("✅ Data extraction testing completed!")
    
    if excel_data:
        print(f"📊 Excel extraction: {len(excel_data)} fields extracted")
    if csv_data:
        print(f"📄 CSV extraction: {len(csv_data)} fields extracted")
    if df_data:
        print(f"📊 DataFrame extraction: {len(df_data)} fields extracted")

if __name__ == "__main__":
    main()
