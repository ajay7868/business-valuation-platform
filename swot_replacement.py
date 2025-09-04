@app.route('/api/swot', methods=['POST'])
def generate_swot():
    """Generate dynamic SWOT analysis using OpenAI with fallback to rule-based analysis"""
    try:
        print("🤖 Dynamic SWOT analysis request received")
        data = request.get_json()
        print(f"📊 SWOT Analysis - Received data keys: {list(data.keys()) if data else 'None'}")
        print(f"📊 SWOT Analysis - extracted_data: {data.get('extracted_data') if data else 'None'}")
        
        # Get basic company info
        company_name = data.get('company_name', 'Unknown Company')
        industry = data.get('industry', 'General')
        
        # Get extracted file data if available (prioritize this over form data)
        extracted_data = data.get('extracted_data', {})
        if extracted_data is None:
            extracted_data = {}
        mapped_fields = extracted_data.get('mapped_fields', {}) if extracted_data else {}
        
        # Use extracted data if available, otherwise fall back to form data
        revenue = mapped_fields.get('revenue') or data.get('revenue', 0)
        ebitda = mapped_fields.get('ebitda') or data.get('ebitda', 0)
        net_income = mapped_fields.get('net_income') or data.get('net_income', 0)
        total_assets = mapped_fields.get('total_assets') or data.get('total_assets', 0)
        total_liabilities = mapped_fields.get('total_liabilities') or data.get('total_liabilities', 0)
        employees = mapped_fields.get('employees') or data.get('employees', 0)
        cash = mapped_fields.get('cash') or data.get('cash', 0)
        inventory = mapped_fields.get('inventory') or data.get('inventory', 0)
        accounts_receivable = mapped_fields.get('accounts_receivable') or data.get('accounts_receivable', 0)
        
        # Additional financial metrics from extracted data
        cost_of_goods_sold = mapped_fields.get('cost_of_goods_sold', 0)
        gross_profit = mapped_fields.get('gross_profit', 0)
        operating_expenses = mapped_fields.get('operating_expenses', 0)
        equipment = mapped_fields.get('equipment', 0)
        fitout = mapped_fields.get('fitout', 0)
        
        print(f"📊 SWOT Analysis - Using extracted data: Revenue=${revenue}, Net Income=${net_income}, Assets=${total_assets}")
        
        # Convert to numeric values for analysis
        revenue = float(revenue) if revenue else 0
        ebitda = float(ebitda) if ebitda else 0
        net_income = float(net_income) if net_income else 0
        total_assets = float(total_assets) if total_assets else 0
        total_liabilities = float(total_liabilities) if total_liabilities else 0
        employees = int(employees) if employees else 0
        cash = float(cash) if cash else 0
        inventory = float(inventory) if inventory else 0
        accounts_receivable = float(accounts_receivable) if accounts_receivable else 0
        cost_of_goods_sold = float(cost_of_goods_sold) if cost_of_goods_sold else 0
        gross_profit = float(gross_profit) if gross_profit else 0
        operating_expenses = float(operating_expenses) if operating_expenses else 0
        equipment = float(equipment) if equipment else 0
        fitout = float(fitout) if fitout else 0
        
        # Calculate comprehensive financial ratios for analysis
        ebitda_margin = (ebitda / revenue * 100) if revenue > 0 else 0
        net_margin = (net_income / revenue * 100) if revenue > 0 else 0
        gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
        operating_margin = ((revenue - cost_of_goods_sold - operating_expenses) / revenue * 100) if revenue > 0 else 0
        debt_to_assets = (total_liabilities / total_assets * 100) if total_assets > 0 else 0
        debt_to_equity = (total_liabilities / (total_assets - total_liabilities) * 100) if (total_assets - total_liabilities) > 0 else 0
        revenue_per_employee = (revenue / employees) if employees > 0 else 0
        current_ratio = ((cash + accounts_receivable) / total_liabilities) if total_liabilities > 0 else 0
        quick_ratio = ((cash + accounts_receivable) / total_liabilities) if total_liabilities > 0 else 0
        inventory_turnover = (cost_of_goods_sold / inventory) if inventory > 0 else 0
        asset_turnover = (revenue / total_assets) if total_assets > 0 else 0
        roa = (net_income / total_assets * 100) if total_assets > 0 else 0
        roe = (net_income / (total_assets - total_liabilities) * 100) if (total_assets - total_liabilities) > 0 else 0
        
        # Prepare company data for dynamic analysis
        company_data = {
            'company_name': company_name,
            'industry': industry,
            'revenue': revenue,
            'ebitda': ebitda,
            'net_income': net_income,
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'employees': employees,
            'cash': cash,
            'inventory': inventory,
            'accounts_receivable': accounts_receivable,
            'cost_of_goods_sold': cost_of_goods_sold,
            'gross_profit': gross_profit,
            'operating_expenses': operating_expenses,
            'equipment': equipment,
            'fitout': fitout
        }
        
        # Prepare financial metrics
        financial_metrics = {
            'ebitda_margin': ebitda_margin,
            'net_margin': net_margin,
            'gross_margin': gross_margin,
            'operating_margin': operating_margin,
            'debt_to_assets': debt_to_assets,
            'debt_to_equity': debt_to_equity,
            'revenue_per_employee': revenue_per_employee,
            'current_ratio': current_ratio,
            'quick_ratio': quick_ratio,
            'inventory_turnover': inventory_turnover,
            'asset_turnover': asset_turnover,
            'roa': roa,
            'roe': roe
        }
        
        # Try dynamic AI-powered SWOT analysis first
        print("🤖 Attempting AI-powered SWOT analysis...")
        ai_swot = swot_analyzer.generate_dynamic_swot(company_data, financial_metrics)
        
        if ai_swot:
            print("✅ AI-powered SWOT analysis completed successfully")
            # Add financial metrics to the response
            ai_swot['financial_metrics'] = financial_metrics
            ai_swot['company_name'] = company_name
            ai_swot['industry'] = industry
            
            return jsonify({
                'status': 'success',
                'swot_analysis': ai_swot,
                'analysis_type': 'AI-Generated'
            })
        else:
            print("⚠️ AI analysis failed, falling back to rule-based analysis")
            # Fallback to rule-based analysis
            return generate_rule_based_swot(company_data, financial_metrics)
        
    except Exception as e:
        print(f"❌ SWOT analysis error: {str(e)}")
        return jsonify({'error': f'SWOT analysis failed: {str(e)}'}), 500

def generate_rule_based_swot(company_data, financial_metrics):
    """Fallback rule-based SWOT analysis when AI is unavailable"""
    try:
        print("📊 Generating rule-based SWOT analysis...")
        
        # Extract metrics
        ebitda_margin = financial_metrics.get('ebitda_margin', 0)
        net_margin = financial_metrics.get('net_margin', 0)
        gross_margin = financial_metrics.get('gross_margin', 0)
        operating_margin = financial_metrics.get('operating_margin', 0)
        debt_to_assets = financial_metrics.get('debt_to_assets', 0)
        debt_to_equity = financial_metrics.get('debt_to_equity', 0)
        revenue_per_employee = financial_metrics.get('revenue_per_employee', 0)
        current_ratio = financial_metrics.get('current_ratio', 0)
        roa = financial_metrics.get('roa', 0)
        roe = financial_metrics.get('roe', 0)
        asset_turnover = financial_metrics.get('asset_turnover', 0)
        
        # Generate SWOT analysis
        strengths = []
        weaknesses = []
        opportunities = []
        threats = []
        
        # STRENGTHS Analysis
        if ebitda_margin > 15:
            strengths.append(f"Strong EBITDA margin of {ebitda_margin:.1f}% indicates efficient operations")
        elif ebitda_margin > 10:
            strengths.append(f"Healthy EBITDA margin of {ebitda_margin:.1f}% shows good operational efficiency")
        
        if net_margin > 10:
            strengths.append(f"Excellent net profit margin of {net_margin:.1f}% demonstrates strong profitability")
        elif net_margin > 5:
            strengths.append(f"Good net profit margin of {net_margin:.1f}% shows solid financial performance")
        
        if gross_margin > 40:
            strengths.append(f"Strong gross margin of {gross_margin:.1f}% indicates effective cost management")
        elif gross_margin > 30:
            strengths.append(f"Healthy gross margin of {gross_margin:.1f}% shows good pricing power")
        
        if debt_to_assets < 30:
            strengths.append(f"Low debt-to-assets ratio of {debt_to_assets:.1f}% indicates strong financial stability")
        elif debt_to_assets < 50:
            strengths.append(f"Moderate debt-to-assets ratio of {debt_to_assets:.1f}% shows manageable leverage")
        
        if revenue_per_employee > 200000:
            strengths.append(f"High revenue per employee of ${revenue_per_employee:,.0f} indicates efficient workforce")
        elif revenue_per_employee > 100000:
            strengths.append(f"Good revenue per employee of ${revenue_per_employee:,.0f} shows productive operations")
        
        if current_ratio > 2:
            strengths.append(f"Strong liquidity position with current ratio of {current_ratio:.1f}")
        elif current_ratio > 1.5:
            strengths.append(f"Good liquidity position with current ratio of {current_ratio:.1f}")
        
        if roa > 10:
            strengths.append(f"Strong return on assets of {roa:.1f}% indicates efficient asset utilization")
        elif roa > 5:
            strengths.append(f"Good return on assets of {roa:.1f}% shows effective asset management")
        
        # WEAKNESSES Analysis
        if ebitda_margin < 5:
            weaknesses.append(f"Low EBITDA margin of {ebitda_margin:.1f}% indicates operational inefficiencies")
        elif ebitda_margin < 10:
            weaknesses.append(f"Below-average EBITDA margin of {ebitda_margin:.1f}% suggests room for improvement")
        
        if net_margin < 2:
            weaknesses.append(f"Low net profit margin of {net_margin:.1f}% indicates profitability challenges")
        elif net_margin < 5:
            weaknesses.append(f"Below-average net profit margin of {net_margin:.1f}% suggests cost management issues")
        
        if debt_to_assets > 70:
            weaknesses.append(f"High debt-to-assets ratio of {debt_to_assets:.1f}% indicates significant financial risk")
        elif debt_to_assets > 50:
            weaknesses.append(f"Elevated debt-to-assets ratio of {debt_to_assets:.1f}% suggests financial stress")
        
        if revenue_per_employee < 50000:
            weaknesses.append(f"Low revenue per employee of ${revenue_per_employee:,.0f} indicates operational inefficiency")
        elif revenue_per_employee < 100000:
            weaknesses.append(f"Below-average revenue per employee of ${revenue_per_employee:,.0f} suggests productivity issues")
        
        if current_ratio < 1:
            weaknesses.append(f"Low current ratio of {current_ratio:.1f} indicates liquidity concerns")
        elif current_ratio < 1.5:
            weaknesses.append(f"Below-average current ratio of {current_ratio:.1f} suggests cash flow challenges")
        
        # OPPORTUNITIES Analysis
        if ebitda_margin > 10:
            opportunities.append("Strong operational efficiency provides foundation for expansion and growth")
        
        if debt_to_assets < 40:
            opportunities.append("Low debt levels provide capacity for strategic investments and acquisitions")
        
        if revenue_per_employee > 150000:
            opportunities.append("High productivity enables scaling operations without proportional headcount increases")
        
        if current_ratio > 2:
            opportunities.append("Strong liquidity position enables opportunistic investments and market expansion")
        
        # Add industry-specific opportunities
        industry = company_data.get('industry', 'General')
        if industry.lower() in ['technology', 'software']:
            opportunities.append("Digital transformation trends create opportunities for technology adoption")
        elif industry.lower() in ['manufacturing', 'industrial']:
            opportunities.append("Industry 4.0 and automation trends present efficiency improvement opportunities")
        elif industry.lower() in ['healthcare', 'medical']:
            opportunities.append("Aging population and healthcare digitization create growth opportunities")
        
        # THREATS Analysis
        if debt_to_assets > 60:
            threats.append("High debt levels increase vulnerability to interest rate changes and economic downturns")
        
        if current_ratio < 1.2:
            threats.append("Low liquidity position increases risk during economic uncertainty or market disruptions")
        
        if ebitda_margin < 8:
            threats.append("Low operational efficiency makes the company vulnerable to competitive pressure")
        
        # Add general market threats
        threats.append("Economic uncertainty and market volatility pose ongoing risks")
        threats.append("Competitive pressure and market saturation in key segments")
        threats.append("Regulatory changes and compliance requirements may impact operations")
        
        # Ensure we have at least some content in each category
        if not strengths:
            strengths.append("Company shows potential for operational improvements")
        if not weaknesses:
            weaknesses.append("Limited financial data available for comprehensive weakness analysis")
        if not opportunities:
            opportunities.append("Market conditions present various growth opportunities")
        if not threats:
            threats.append("General market and economic risks apply to all businesses")
        
        swot_analysis = {
            'company_name': company_data.get('company_name', 'Unknown Company'),
            'industry': company_data.get('industry', 'General'),
            'generated_at': datetime.now().isoformat(),
            'analysis_type': 'Rule-Based',
            'financial_metrics': financial_metrics,
            'strengths': strengths[:8],  # Limit to top 8
            'weaknesses': weaknesses[:8],
            'opportunities': opportunities[:8],
            'threats': threats[:8]
        }
        
        return jsonify({
            'status': 'success',
            'swot_analysis': swot_analysis,
            'analysis_type': 'Rule-Based'
        })
        
    except Exception as e:
        print(f"❌ Rule-based SWOT analysis error: {str(e)}")
        return jsonify({'error': f'Rule-based SWOT analysis failed: {str(e)}'}), 500
