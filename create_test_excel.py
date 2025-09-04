#!/usr/bin/env python3
"""
Create a test Excel file for testing file upload
"""

import pandas as pd

# Create sample financial data
data = {
    'Company': ['Test Corp', 'Test Corp', 'Test Corp'],
    'Revenue': [1000000, 1100000, 1200000],
    'EBITDA': [200000, 220000, 240000],
    'Year': [2022, 2023, 2024]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save as Excel file
df.to_excel('test_financial.xlsx', index=False, sheet_name='Financial Data')

print("✅ Test Excel file created: test_financial.xlsx")
print("📊 Data preview:")
print(df)
