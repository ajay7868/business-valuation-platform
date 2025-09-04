#!/usr/bin/env python3
"""
Create a test Excel file with multiple sheets for testing dynamic field mapping
"""

import pandas as pd

# Sheet 1: Financial Summary
financial_data = {
    'Entity_Name': ['XYZ Corp', 'XYZ Corp', 'XYZ Corp'],
    'Gross_Revenue': [3000000, 3200000, 3500000],
    'Operating_Earnings': [600000, 640000, 700000],
    'Net_Result': [450000, 480000, 525000],
    'Asset_Total': [12000000, 12500000, 13000000],
    'Workforce_Size': [35, 38, 40],
    'Business_Category': ['Manufacturing', 'Manufacturing', 'Manufacturing']
}

# Sheet 2: Detailed P&L (less relevant for mapping)
pl_data = {
    'Month': ['Jan', 'Feb', 'Mar'],
    'Revenue': [250000, 275000, 300000],
    'Expenses': [200000, 220000, 240000],
    'Profit': [50000, 55000, 60000]
}

# Sheet 3: Balance Sheet (more relevant for mapping)
bs_data = {
    'Account': ['Cash', 'Inventory', 'Accounts Receivable', 'Total Assets'],
    'Amount': [2000000, 1500000, 1000000, 12000000],
    'Type': ['Asset', 'Asset', 'Asset', 'Asset']
}

# Create Excel file with multiple sheets
with pd.ExcelWriter('test_dynamic_mapping.xlsx', engine='openpyxl') as writer:
    # Write sheets
    pd.DataFrame(financial_data).to_excel(writer, sheet_name='Financial Summary', index=False)
    pd.DataFrame(pl_data).to_excel(writer, sheet_name='P&L Detail', index=False)
    pd.DataFrame(bs_data).to_excel(writer, sheet_name='Balance Sheet', index=False)

print("✅ Test Excel file created: test_dynamic_mapping.xlsx")
print("📊 Sheets created:")
print("  - Financial Summary (should map best)")
print("  - P&L Detail (partial mapping)")
print("  - Balance Sheet (limited mapping)")
print("\n🎯 Expected mapping:")
print("  - Entity_Name → company_name")
print("  - Gross_Revenue → revenue")
print("  - Operating_Earnings → ebitda")
print("  - Net_Result → net_income")
print("  - Asset_Total → total_assets")
print("  - Workforce_Size → employees")
print("  - Business_Category → industry")
