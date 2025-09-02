
import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

class BusinessValuationEngine:
    """
    Core business valuation engine supporting multiple valuation methods
    """
    
    def __init__(self):
        self.company_data = {}
        self.financial_data = {}
        self.valuation_results = {}
        self.industry_multiples = {
            'manufacturing': {'revenue': 0.8, 'ebitda': 4.5, 'sde': 3.2},
            'technology': {'revenue': 3.0, 'ebitda': 12.0, 'sde': 4.5},
            'retail': {'revenue': 0.5, 'ebitda': 6.0, 'sde': 2.8},
            'services': {'revenue': 1.2, 'ebitda': 8.0, 'sde': 3.5},
            'construction': {'revenue': 0.6, 'ebitda': 5.5, 'sde': 3.0}
        }
    
    def load_company_data(self, data: Dict):
        """Load company data from CIM or manual input"""
        self.company_data = data
        self.extract_financial_data()
    
    def extract_financial_data(self):
        """Extract and normalize financial data"""
        self.financial_data = {
            'revenue': self.company_data.get('revenue', 0),
            'gross_profit': self.company_data.get('gross_profit', 0),
            'ebitda': self.company_data.get('ebitda', 0),
            'sde': self.company_data.get('sde', 0),
            'net_income': self.company_data.get('net_income', 0),
            'total_assets': self.company_data.get('total_assets', 0),
            'inventory': self.company_data.get('inventory', 0),
            'accounts_receivable': self.company_data.get('accounts_receivable', 0),
            'cash': self.company_data.get('cash', 0),
            'total_liabilities': self.company_data.get('total_liabilities', 0)
        }
    
    def calculate_asset_based_valuation(self) -> float:
        """Calculate asset-based valuation"""
        tangible_assets = (
            self.financial_data['inventory'] + 
            self.financial_data['accounts_receivable'] + 
            self.financial_data['cash']
        )
        
        # Adjust for equipment/machinery (estimated at 60% of book value)
        equipment_value = self.company_data.get('equipment_value', 0) * 0.6
        
        total_assets = tangible_assets + equipment_value
        total_liabilities = self.financial_data['total_liabilities']
        
        return max(0, total_assets - total_liabilities)
    
    def calculate_income_based_valuation(self, growth_rate: float = 0.03, 
                                       discount_rate: float = 0.12) -> Dict:
        """Calculate DCF and capitalization of earnings"""
        
        # DCF Calculation
        base_cash_flow = self.financial_data['ebitda']
        if base_cash_flow <= 0:
            base_cash_flow = self.financial_data['sde']
        
        # Project 5 years of cash flows
        projected_flows = []
        for year in range(1, 6):
            flow = base_cash_flow * ((1 + growth_rate) ** year)
            projected_flows.append(flow)
        
        # Terminal value (Gordon Growth Model)
        terminal_value = projected_flows[-1] * (1 + growth_rate) / (discount_rate - growth_rate)
        
        # Discount all flows to present value
        dcf_value = 0
        for i, flow in enumerate(projected_flows):
            dcf_value += flow / ((1 + discount_rate) ** (i + 1))
        
        # Add discounted terminal value
        dcf_value += terminal_value / ((1 + discount_rate) ** 5)
        
        # Capitalization of Earnings
        cap_earnings = base_cash_flow / discount_rate
        
        return {
            'dcf_value': dcf_value,
            'capitalization_value': cap_earnings,
            'projected_flows': projected_flows,
            'terminal_value': terminal_value
        }
    
    def calculate_market_based_valuation(self) -> Dict:
        """Calculate market-based valuation using industry multiples"""
        industry = self.company_data.get('industry', 'services').lower()
        multiples = self.industry_multiples.get(industry, self.industry_multiples['services'])
        
        revenue = self.financial_data['revenue']
        ebitda = self.financial_data['ebitda']
        sde = self.financial_data['sde']
        
        return {
            'revenue_multiple': revenue * multiples['revenue'],
            'ebitda_multiple': ebitda * multiples['ebitda'] if ebitda > 0 else 0,
            'sde_multiple': sde * multiples['sde'] if sde > 0 else 0,
            'multiples_used': multiples
        }
    
    def detect_anomalies(self) -> List[str]:
        """Detect financial anomalies and red flags"""
        anomalies = []
        
        # Revenue checks
        if self.financial_data['revenue'] <= 0:
            anomalies.append("Zero or negative revenue detected")
        
        # Profitability checks
        if self.financial_data['ebitda'] < 0 and self.financial_data['sde'] < 0:
            anomalies.append("Negative profitability (EBITDA and SDE)")
        
        # Margin checks
        if self.financial_data['revenue'] > 0:
            gross_margin = self.financial_data['gross_profit'] / self.financial_data['revenue']
            if gross_margin < 0.1:
                anomalies.append("Very low gross margin (<10%)")
            elif gross_margin > 0.8:
                anomalies.append("Unusually high gross margin (>80%) - verify data")
        
        # Asset checks
        if self.financial_data['inventory'] > self.financial_data['revenue']:
            anomalies.append("Inventory exceeds annual revenue - potential overstock")
        
        # Receivables check
        if self.financial_data['accounts_receivable'] > (self.financial_data['revenue'] * 0.25):
            anomalies.append("High accounts receivable (>25% of revenue) - collection issues?")
        
        return anomalies
    
    def calculate_comprehensive_valuation(self) -> Dict:
        """Calculate all valuation methods and provide range"""
        
        # Calculate all methods
        asset_value = self.calculate_asset_based_valuation()
        income_values = self.calculate_income_based_valuation()
        market_values = self.calculate_market_based_valuation()
        
        # Collect all valuation estimates
        estimates = []
        
        if asset_value > 0:
            estimates.append(asset_value)
        
        if income_values['dcf_value'] > 0:
            estimates.append(income_values['dcf_value'])
        
        if income_values['capitalization_value'] > 0:
            estimates.append(income_values['capitalization_value'])
        
        if market_values['revenue_multiple'] > 0:
            estimates.append(market_values['revenue_multiple'])
        
        if market_values['ebitda_multiple'] > 0:
            estimates.append(market_values['ebitda_multiple'])
        
        if market_values['sde_multiple'] > 0:
            estimates.append(market_values['sde_multiple'])
        
        # Calculate range
        if estimates:
            low_estimate = min(estimates) * 0.85  # 15% discount for low
            high_estimate = max(estimates) * 1.15  # 15% premium for high
            mid_estimate = sum(estimates) / len(estimates)  # Use mean instead of median
        else:
            low_estimate = high_estimate = mid_estimate = 0
        
        # Detect anomalies
        anomalies = self.detect_anomalies()
        
        self.valuation_results = {
            'asset_based': asset_value,
            'income_based': income_values,
            'market_based': market_values,
            'valuation_range': {
                'low': low_estimate,
                'mid': mid_estimate,
                'high': high_estimate
            },
            'all_estimates': estimates,
            'anomalies': anomalies,
            'valuation_date': datetime.now().isoformat(),
            'methodology_notes': self.get_methodology_notes()
        }
        
        return self.valuation_results
    
    def get_methodology_notes(self) -> Dict:
        """Provide notes on methodology used"""
        return {
            'asset_based': 'Book value adjusted for market conditions, equipment at 60% of book',
            'dcf': 'Discounted Cash Flow with 3% growth, 12% discount rate',
            'market_multiples': f"Industry multiples for {self.company_data.get('industry', 'services')}",
            'assumptions': [
                'Growth rate: 3% annually',
                'Discount rate: 12%',
                'Terminal growth: 3%',
                'Equipment depreciation: 40%'
            ]
        }
    
    def generate_executive_summary(self) -> str:
        """Generate executive summary of valuation"""
        company_name = self.company_data.get('company_name', 'The Company')
        revenue = self.financial_data['revenue']
        valuation_range = self.valuation_results['valuation_range']
        
        summary = f"""
EXECUTIVE SUMMARY - BUSINESS VALUATION

Company: {company_name}
Valuation Date: {datetime.now().strftime('%B %d, %Y')}
Annual Revenue: ${revenue:,.0f}

VALUATION RANGE:
Low Estimate:  ${valuation_range['low']:,.0f}
Mid Estimate:  ${valuation_range['mid']:,.0f}
High Estimate: ${valuation_range['high']:,.0f}

The valuation is based on multiple approaches including asset-based, income-based (DCF), 
and market-based methodologies. The range reflects different scenarios and market conditions.
        """
        
        return summary.strip()
