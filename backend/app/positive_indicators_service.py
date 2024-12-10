# app/services/positive_indicators_service.py

import pandas as pd
import numpy as np
from app.models import BalanceSheet, IncomeStatement, CashFlow

class PositiveIndicatorsService:
    def get_financial_data_as_dataframe(self, ticker):
        # Fetch data from the database
        balance_sheets = BalanceSheet.query.filter_by(ticker=ticker).all()
        income_statements = IncomeStatement.query.filter_by(ticker=ticker).all()
        cash_flows = CashFlow.query.filter_by(ticker=ticker).all()

        # Initialize a dictionary to store the data
        data = {
            'calendarYear': [],

            # Balance Sheet

            # Balance Sheet

            # Balance Sheet
            'totalCurrentAssets': [],
            'cashAndCashEquivalents': [],
            'netReceivables': [],
            'inventory': [],
            'totalAssets': [],
            'totalCurrentLiabilities': [],
            'accountPayables': [],
            'totalDebt': [],
            'deferredRevenue': [],
            'totalStockholdersEquity': [],
            
            # Income Statement
            'revenue': [],
            'costOfRevenue': [],
            'grossProfit': [],
            'researchAndDevelopmentExpenses': [],
            'operatingExpenses': [],
            'operatingIncome': [],
            'interestExpense': [],
            'netIncome': [],
            
            # Cash Flow Statement
            # Income Statement
            'revenue': [],
            'costOfRevenue': [],
            'grossProfit': [],
            'researchAndDevelopmentExpenses': [],
            'operatingExpenses': [],
            'operatingIncome': [],
            'interestExpense': [],
            'netIncome': [],
            
            # Cash Flow Statement
            'operatingCashFlow': [],
            'capitalExpenditure': [],
            'freeCashFlow': [],
        }

        # Populate data from BalanceSheet, IncomeStatement, and CashFlow tables
        for record in balance_sheets:
            data['calendarYear'].append(record.date[:4])
            data['totalCurrentAssets'].append(record.total_current_assets or np.nan)
            data['cashAndCashEquivalents'].append(record.cash_and_cash_equivalents or np.nan)
            data['netReceivables'].append(record.net_receivables or np.nan)
            data['inventory'].append(record.inventory or np.nan)
            data['totalAssets'].append(record.total_assets or np.nan)
            data['totalCurrentLiabilities'].append(record.total_current_liabilities or np.nan)
            data['accountPayables'].append(record.account_payables or np.nan)
            data['totalDebt'].append(record.total_debt or np.nan)
            data['deferredRevenue'].append(record.deferred_revenue or np.nan)
            data['totalStockholdersEquity'].append(record.total_stockholders_equity or np.nan)

        for record in income_statements:
            data['revenue'].append(record.revenue or np.nan)
            data['costOfRevenue'].append(record.cost_of_revenue or np.nan)
            data['grossProfit'].append(record.gross_profit or np.nan)
            data['researchAndDevelopmentExpenses'].append(record.research_and_development_expenses or np.nan)
            data['operatingExpenses'].append(record.operating_expenses or np.nan)
            data['operatingIncome'].append(record.operating_income or np.nan)
            data['interestExpense'].append(record.interest_expense or np.nan)
            data['netIncome'].append(record.net_income or np.nan)

        for record in cash_flows:
            data['operatingCashFlow'].append(record.operating_cash_flow or np.nan)
            data['capitalExpenditure'].append(record.capital_expenditure or np.nan)
            data['freeCashFlow'].append(record.free_cash_flow or np.nan)

        # Create DataFrame from the dictionary
        df = pd.DataFrame(data)
        return df

    def analyze_positive_indicators(self, ticker):
        data = self.get_financial_data_as_dataframe(ticker)
                
        # Sort data by calendar year to ensure chronological order
        data = data.sort_values('calendarYear').reset_index(drop=True)

        results = []

        # List of analysis functions to execute
        analysis_functions = [
            self.analyze_increasing_free_cash_flow,
            self.analyze_reducing_debt_levels,
            self.analyze_improving_efficiency_ratios,
            self.analyze_expanding_gross_profit_margins,
            self.analyze_consistent_revenue_growth,
            self.analyze_increasing_roe_roa,
            self.analyze_healthy_interest_coverage,
            self.analyze_cash_reserves_accumulation,
            self.analyze_operating_expenses,
            self.analyze_positive_changes_working_capital,
            self.analyze_investment_in_capex,
            self.analyze_strong_operating_cash_flow,
            self.analyze_decreasing_dpo,
            self.analyze_increase_in_deferred_revenue,
            self.analyze_rd_investments
        ]

        for function in analysis_functions:
            result = function(data)
            if result:
                results.append(result)
                results.append("_____________________________________")

        return "\n\n".join(results) if results else "No positive indicators identified."

    def format_number(self, num):
        if abs(num) >= 1_000_000_000:
            value = round(num / 1_000_000_000, 2)
            return f"{value:.2f}".rstrip('0').rstrip('.') + " billion"
        elif abs(num) >= 1_000_000:
            value = round(num / 1_000_000, 2)
            return f"{value:.2f}".rstrip('0').rstrip('.') + " million"
        else:
            value = round(num, 2)
            return f"{value:.2f}".rstrip('0').rstrip('.')
    
    def format_percent(self, percent):
        formatted = f"{round(percent, 2):.2f}".rstrip('0').rstrip('.')
        return formatted

    # Individual positive indicator analysis functions

    ############################ PI1 ############################

    def analyze_increasing_free_cash_flow(self, data):
        
        # Ensure necessary columns are present
        if 'freeCashFlow' not in data.columns or 'netIncome' not in data.columns:
            return "FCF and Net Income analysis requires 'freeCashFlow' and 'netIncome' columns."

        # Suppress FutureWarning by using fill_method=None
        data['FCF_Change'] = data['freeCashFlow'].replace(0, np.nan).pct_change() * 100
        data['NetIncome_Change'] = data['netIncome'].replace(0, np.nan).pct_change() * 100

        # Condition: FCF increasing while Net Income change is minimal (stable)
        stable_net_income = (data['NetIncome_Change'].abs() <= 10)  # within ±10% change
        increasing_fcf = (data['FCF_Change'] > 0)

        # Additional check: Ensure FCF is positive after increase
        positive_fcf = (data['freeCashFlow'] > 0)
        valid_fcf_increase = increasing_fcf & positive_fcf
        positive_indicators = valid_fcf_increase & stable_net_income

        # Check if there are any positive indicators
        if not any(positive_indicators):
            return None  # Return None if no indicators are triggered

        # Generate detailed report
        report = [
            "✓✓✓ Increasing Free Cash Flow Despite Stable Net Income\n",
            "Improved cash efficiency, indicating that the company is generating more cash from operations.",
            "Suggests strong cash management, potential for reinvestment or debt reduction.",
            "Net Income change is minimal (±10%)\n"
        ]

        for i in range(1, len(data)):
            if positive_indicators[i]:
                year = data['calendarYear'][i]
                fcf = data['freeCashFlow'][i]
                fcf_change = data['FCF_Change'][i]
                net_income = data['netIncome'][i]
                net_income_change = data['NetIncome_Change'][i]

                # Format the net income change to indicate up or down
                ni_direction = "↑" if net_income_change >= 0 else "↓"

                # Append the formatted fiscal year report
                report.append(
                    f"FY {year}: Free Cash Flow = {self.format_number(fcf)} (↑ {self.format_percent(fcf_change)}%), Net Income = {self.format_number(net_income)} ({ni_direction} {self.format_percent(abs(net_income_change))}%)"
                )

        return "\n".join(report)

    ############################ PI2 ############################

    def analyze_reducing_debt_levels(self, data):
        
        # Ensure necessary columns are present
        if 'totalDebt' not in data.columns:
            return "Debt analysis requires 'totalDebt' column."        

        # Calculate the percentage change in total debt
        data['Debt_Change'] = data['totalDebt'].replace(0, np.nan).pct_change() * 100

        # Identify significant reductions and general trend
        significant_reduction = data['Debt_Change'] < -5
        overall_trend_downward = (data['totalDebt'].replace(0, np.nan).diff().dropna() < 0).all()

        # Return None if the overall trend is not downward
        if not overall_trend_downward:
            return None

        # Prepare report header
        report = [
            "✓✓✓ Reducing Debt Levels\n",
            "Deleveraging strategy, enhancing financial stability and reducing interest expenses.",
            "This strengthens the balance sheet, lowers financial risk, and increases the company's flexibility to invest in growth opportunities.\n"
        ]
        initial_report_lines = len(report)

        # Identify and append significant reductions
        for i in range(1, len(data)):
            if significant_reduction.iloc[i]:
                year = data['calendarYear'].iloc[i]
                debt = data['totalDebt'].iloc[i]
                debt_change = data['Debt_Change'].iloc[i]
                report.append(
                    f"FY {year}: Total Debt = {self.format_number(debt)} (↓ {self.format_percent(abs(debt_change))}%)"
                )

        # Return None if no significant reductions were found
        if len(report) == initial_report_lines:
            return None

        return "\n".join(report)

    ############################ PI3 ############################

    def analyze_improving_efficiency_ratios(self, data):
        
        # Ensure necessary columns are present
        if not all(col in data.columns for col in ['costOfRevenue', 'inventory', 'revenue', 'netReceivables']):
            return "Efficiency Ratio analysis requires 'costOfRevenue', 'inventory', 'revenue', 'netReceivables' columns."

        # Calculate Inventory Turnover and Receivables Turnover
        data['Inventory_Turnover'] = data['costOfRevenue'] / data['inventory'].replace(0, np.nan)
        data['Receivables_Turnover'] = data['revenue'] / data['netReceivables'].replace(0, np.nan)
        
        # Calculate percentage changes in the ratios
        data['Inventory_Turnover_Change'] = data['Inventory_Turnover'].pct_change() * 100
        data['Receivables_Turnover_Change'] = data['Receivables_Turnover'].pct_change() * 100

        # Generate detailed report
        report = [
            "✓✓✓ Improving Efficiency Ratios\n",
            "Enhanced operational performance, suggesting better management of assets.",
            "Improved efficiency ratios indicate the company is effectively utilizing its resources to generate sales.\n"
        ]

        # Track if any year meets the criteria
        improvement_found = False
        
        for i in range(1, len(data)):
            year = data['calendarYear'].iloc[i]
            inventory_turnover = data['Inventory_Turnover'].iloc[i]
            inventory_change = data['Inventory_Turnover_Change'].iloc[i]
            receivables_turnover = data['Receivables_Turnover'].iloc[i]
            receivables_change = data['Receivables_Turnover_Change'].iloc[i]

            # Check for improvements in both ratios
            if inventory_change > 0 and receivables_change > 0:
                report.append(
                    f"FY {year}: Inventory Turnover = {inventory_turnover:.2f} (↑ {self.format_percent(inventory_change)}%),"
                    f" Receivables Turnover = {receivables_turnover:.2f} (↑ {self.format_percent(receivables_change)}%)"
                )
                improvement_found = True

        if not improvement_found:
            return None
        
        return "\n".join(report)

    ############################ PI4 ############################

    def analyze_expanding_gross_profit_margins(self, data, threshold=5):
        
        # Ensure necessary columns are present
        if 'grossProfit' not in data.columns or 'revenue' not in data.columns:
            return "Gross Profit Margin analysis requires 'grossProfit' and 'revenue' columns."

        # Calculate Gross Profit Margin
        data['Gross_Profit_Margin'] = (data['grossProfit'] / data['revenue'].replace(0, np.nan)) * 100
        
        # Calculate percentage changes in Gross Profit Margin
        data['Gross_Profit_Margin_Change'] = data['Gross_Profit_Margin'].pct_change() * 100

        # Check overall trend (ensure all changes are positive)
        overall_trend_positive = all(data['Gross_Profit_Margin_Change'].dropna() > 0)

        # Generate detailed report
        report = [
            "✓✓✓ Expanding Gross Profit Margins\n",
            "Increased pricing power or cost control, leading to higher profitability.",
            "This may result from innovation, brand strength, or economies of scale, indicating a strong competitive position and effective management strategies.\n"
        ]

        # Track if any year meets the criteria
        improvement_found = False
        
        for i in range(1, len(data)):
            year = data['calendarYear'].iloc[i]
            gross_profit_margin = data['Gross_Profit_Margin'].iloc[i]
            gross_profit_margin_change = data['Gross_Profit_Margin_Change'].iloc[i]

            # Check for improvement in Gross Profit Margin and if it meets the threshold
            if overall_trend_positive and gross_profit_margin_change > threshold:
                report.append(
                    f"FY {year}: Gross Profit Margin = {gross_profit_margin:.2f}% (↑ {self.format_percent(gross_profit_margin_change)}%)"
                )
                improvement_found = True

        if not improvement_found:
            return None
        
        return "\n".join(report)

    ############################ PI5 ############################

    def analyze_consistent_revenue_growth(self, data, threshold=4):
        
        # Ensure necessary columns are present
        if 'revenue' not in data.columns:
            return "Revenue Growth analysis requires 'revenue' column."        

        # Calculate YoY percentage change in revenue
        data['Revenue_Growth'] = data['revenue'].replace(0, np.nan).pct_change() * 100
        
        # Check if revenue growth is consistent (positive in all periods)
        consistent_growth = all(data['Revenue_Growth'].dropna() > threshold)

        # Generate detailed report
        report = [
            "✓✓✓ Consistent Revenue Growth\n",
            "Strong market demand and successful business strategies, demonstrating the company's ability to grow its customer base and market share.",
            "Consistent growth can lead to economies of scale and attract investment.\n"
        ]
        
        if consistent_growth:
            for i in range(1, len(data)):
                year = data['calendarYear'].iloc[i]
                revenue = data['revenue'].iloc[i]
                revenue_growth = data['Revenue_Growth'].iloc[i]
                report.append(f"FY {year}: Revenue = {self.format_number(revenue)} (↑ {self.format_percent(revenue_growth)}%)")
        else:
            return None
        
        return "\n".join(report)

    ############################ PI6 ############################

    def analyze_increasing_roe_roa(self, data):
        
        # Ensure necessary columns are present
        if not all(col in data.columns for col in ['netIncome', 'totalStockholdersEquity', 'totalAssets']):
            return "ROE & ROA analysis requires 'netIncome', 'totalStockholdersEquity', 'totalAssets' columns."    

        # Calculate Return on Equity (ROE) and Return on Assets (ROA)
        data['ROE'] = (data['netIncome'] / data['totalStockholdersEquity'].replace(0, np.nan)) * 100
        data['ROA'] = (data['netIncome'] / data['totalAssets'].replace(0, np.nan)) * 100

        # Calculate YoY changes for ROE and ROA
        data['ROE_Change'] = data['ROE'].pct_change() * 100
        data['ROA_Change'] = data['ROA'].pct_change() * 100

        # Generate detailed report
        report = [
            "✓✓✓ Increasing Return on Equity and Assets\n",
            "Efficient use of capital and assets, indicating management is generating higher returns from available resources.",
            "This suggests profitability and effectiveness in deploying capital, enhancing shareholder value.\n"
        ]
        
        # Check only positive ROE and ROA improvements
        improvement_found = False
        for i in range(1, len(data)):
            year = data['calendarYear'].iloc[i]
            roe = data['ROE'].iloc[i]
            roe_change = data['ROE_Change'].iloc[i]
            roa = data['ROA'].iloc[i]
            roa_change = data['ROA_Change'].iloc[i]

            # Only consider cases where ROE and ROA are positive
            if roe > 0 and roa > 0 and roe_change > 0 and roa_change > 0:
                report.append(
                    f"FY {year}: ROE = {self.format_percent(roe)}% (↑ {self.format_percent(roe_change)}%), "
                    f"ROA = {self.format_percent(roa)}% (↑ {self.format_percent(roa_change)}%)"
                )
                improvement_found = True

        if improvement_found:
            return "\n".join(report)
        else:
            return None

    ############################ PI7 ############################

    def analyze_healthy_interest_coverage(self, data, healthy_threshold=2.5):
        
        # Ensure necessary columns are present
        if 'operatingIncome' not in data.columns or 'interestExpense' not in data.columns:
            return "Interest Coverage analysis requires 'operatingIncome' and 'interestExpense' columns."            

        # Calculate Interest Coverage Ratio
        data['Interest_Coverage_Ratio'] = data['operatingIncome'] / data['interestExpense'].replace(0, np.nan)

        # Calculate YoY changes in Interest Coverage Ratio
        data['Interest_Coverage_Change'] = data['Interest_Coverage_Ratio'].pct_change() * 100

        # Positive Indicator Report
        report = [
            "✓✓✓ Healthy Interest Coverage Ratio\n",
            "Strong ability to service debt, reducing financial risk.",
            "A high ratio indicates ample earnings to cover interest obligations, providing comfort to lenders and investors about the company's solvency and financial health.\n"
        ]
        
        # Check if the trend is overall positive and if it starts from a healthy range
        healthy_found = False
        positive_trend = True

        for i in range(1, len(data)):
            year = data['calendarYear'].iloc[i]
            interest_coverage = data['Interest_Coverage_Ratio'].iloc[i]
            coverage_change = data['Interest_Coverage_Change'].iloc[i]

            # Interest Coverage must start in healthy range and have positive YoY changes
            if interest_coverage >= healthy_threshold:
                if coverage_change > 0:
                    direction = '↑'
                    report.append(
                        f"FY {year}: Interest Coverage = {interest_coverage:.2f} ({direction} {self.format_percent(abs(coverage_change))}%)"
                    )
                    healthy_found = True
                elif coverage_change < 0:
                    # If there's a decline, we mark the trend as non-positive
                    positive_trend = False

        # Only trigger the report if overall trend is positive and ratio is consistently in the healthy range
        if healthy_found and positive_trend:
            return "\n".join(report)
        else:
            return None

    ############################ PI8 ############################

    def analyze_cash_reserves_accumulation(self, data):

        # Ensure necessary columns are present
        required_columns = ['cashAndCashEquivalents', 'calendarYear']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            return f"Cash Reserve analysis requires the following missing columns: {', '.join(missing_columns)}."

        # Check if the dataset is valid (no missing or incorrect values)
        if data['cashAndCashEquivalents'].isnull().any():
            return "Dataset contains missing values in 'cashAndCashEquivalents'. Please clean the data and retry."

        # Calculate percentage change in cash and cash equivalents
        data['Cash_Change'] = data['cashAndCashEquivalents'].pct_change() * 100

        # Check if cash reserves are consistently increasing
        increasing_cash_reserves = data['Cash_Change'] > 0

        # Generate detailed report
        report = [
            "✓✓✓ Accumulation of Cash Reserves\n",
            "Improved liquidity and financial flexibility, enabling the company to invest in growth opportunities,",
            "weather economic downturns, or return value to shareholders through dividends or buybacks.",
            "A strong cash position enhances strategic options.\n"
        ]

        # Track if any year meets the criteria
        improvement_found = False

        for i in range(1, len(data)):  # Start at 1 to skip the first year
            if increasing_cash_reserves.iloc[i]:
                year = data['calendarYear'].iloc[i]
                cash = data['cashAndCashEquivalents'].iloc[i]
                cash_change = data['Cash_Change'].iloc[i]

                # Append the formatted report for years with increasing cash reserves
                report.append(
                    f"FY {year}: Cash and Cash Equivalents = {self.format_number(cash)} "
                    f"(↑ {self.format_percent(cash_change)}%)"
                )
                improvement_found = True

        # Only return report if any accumulation was found
        if improvement_found:
            return "\n".join(report)
        else:
            return None


    ############################ PI9 ############################

    def analyze_operating_expenses(self, data):
        
        # Ensure necessary columns are present
        if 'operatingExpenses' not in data.columns or 'revenue' not in data.columns:
            return "Operating Expense analysis requires 'operatingExpenses' and 'revenue' columns."            

        # Calculate the Operating Expenses to Sales Ratio
        data['Operating_Expenses_to_Sales_Ratio'] = data['operatingExpenses'] / data['revenue'].replace(0, np.nan)
        
        # Check for reduction in operating expenses and analyze the ratio
        reduction_in_expenses = data['operatingExpenses'].replace(0, np.nan).pct_change() < 0  # Negative change means reduction
        ratio_improvement = data['Operating_Expenses_to_Sales_Ratio'].pct_change() < 0  # Ratio should decrease
        
        # Calculate percentage change in the Operating Expenses to Sales Ratio
        data['Operating_Expenses_to_Sales_Ratio_Change'] = data['Operating_Expenses_to_Sales_Ratio'].pct_change() * 100
        
        # Check if there are any positive indicators
        if not any(reduction_in_expenses & ratio_improvement):
            return None  # Return None if no reduction is detected

        # Generate detailed report
        report = [
            "✓✓✓ Reduction in Operating Expenses\n",
            "Enhanced operational efficiency, leading to higher profit margins.",
            "Cost reductions without sacrificing revenue can indicate effective cost management and process improvements, contributing to sustainable profitability.\n"
        ]
        
        for i in range(1, len(data)):
            if reduction_in_expenses.iloc[i] and ratio_improvement.iloc[i]:
                year = data['calendarYear'].iloc[i]
                ratio = data['Operating_Expenses_to_Sales_Ratio'].iloc[i]
                ratio_change = data['Operating_Expenses_to_Sales_Ratio_Change'].iloc[i]
                
                # Append the formatted fiscal year report with percentage decrease in ratio
                report.append(
                    f"FY {year}: Operating Expenses to Sales = {ratio:.2f} (↓ {self.format_percent(abs(ratio_change))}%)"
                )
        
        return "\n".join(report)

    ############################ PI10 ############################

    def analyze_positive_changes_working_capital(self, data, ratio_threshold=5):
        
        # Ensure necessary columns are present
        if 'totalCurrentAssets' not in data.columns or 'totalCurrentLiabilities' not in data.columns:
            return "Net Working Capital analysis requires 'totalCurrentAssets' and 'totalCurrentLiabilities' columns."            

        # Calculate Current Ratio
        data['Current_Ratio'] = data['totalCurrentAssets'] / data['totalCurrentLiabilities'].replace(0, np.nan)
        
        # Calculate Net Working Capital
        data['Net_Working_Capital'] = data['totalCurrentAssets'] - data['totalCurrentLiabilities'].replace(0, np.nan)
        
        # Calculate percentage change in Current Ratio and Net Working Capital
        data['Current_Ratio_Change'] = data['Current_Ratio'].pct_change() * 100
        data['Net_Working_Capital_Change'] = data['Net_Working_Capital'].pct_change() * 100
        
        # Check for overall improvements in Net Working Capital and Current Ratio
        positive_working_capital = data['Net_Working_Capital_Change'] > 0
        notable_current_ratio_change = data['Current_Ratio_Change'] > ratio_threshold

        # Generate detailed report
        report = [
            "✓✓✓ Positive Changes in Working Capital\n",
            "Improved short-term financial health, suggesting effective management of receivables, payables, and inventory.",
            "Positive changes can enhance liquidity, reduce reliance on external financing, and indicate operational efficiency.\n"
        ]

        improvement_found = False
        
        for i in range(1, len(data)):
            if positive_working_capital.iloc[i] and notable_current_ratio_change.iloc[i]:
                year = data['calendarYear'].iloc[i]
                current_ratio = data['Current_Ratio'].iloc[i]
                current_ratio_change = data['Current_Ratio_Change'].iloc[i]
                net_working_capital = data['Net_Working_Capital'].iloc[i]
                nwc_change = data['Net_Working_Capital_Change'].iloc[i]
                
                # Append the formatted report with NWC percentage increase
                report.append(
                    f"FY {year}: Current Ratio = {current_ratio:.2f} (↑ {current_ratio_change:.2f}%),"
                    f" Net Working Capital = {self.format_number(net_working_capital)} (↑ {self.format_percent(nwc_change)}%)"
                )
                improvement_found = True

        if not improvement_found:
            return None
        
        return "\n".join(report)

    ############################ PI11 ############################

    def analyze_investment_in_capex(self, data, capex_threshold=5):
        
        # Ensure necessary columns are present
        if 'capitalExpenditure' not in data.columns:
            return "CapEx analysis requires 'capitalExpenditure' column."            

        # Calculate percentage change in Capital Expenditures (CapEx)
        data['CapEx_Change'] = data['capitalExpenditure'].replace(0, np.nan).pct_change() * 100
        
        # Generate detailed report
        report = [
            "✓✓✓ Investment in Capital Expenditures (CapEx)\n",
            "Commitment to future growth and competitiveness through investment in assets.",
            "Increased CapEx can signal expansion, modernization, or entry into new markets, potentially leading to higher future revenues and market share.\n"
        ]

        improvement_found = False
        
        for i in range(1, len(data)):
            year = data['calendarYear'].iloc[i]
            capex = data['capitalExpenditure'].iloc[i]
            capex_change = data['CapEx_Change'].iloc[i]

            # Check for notable increase in CapEx (greater than the specified threshold)
            if capex_change > capex_threshold:
                report.append(
                    f"FY {year}: Capital Expenditures = {self.format_number(abs(capex))} (↑ {self.format_percent(capex_change)}%)"
                )
                improvement_found = True

        if not improvement_found:
            return None
        
        return "\n".join(report)

    ############################ PI12 ############################

    def analyze_strong_operating_cash_flow(self, data, cash_flow_threshold=5):
        
        # Ensure necessary columns are present
        if 'operatingCashFlow' not in data.columns:
            return "Operating Cash Flow analysis requires 'operatingCashFlow' column."    

        # Calculate percentage change in Operating Cash Flow
        data['Operating_Cash_Flow_Change'] = data['operatingCashFlow'].replace(0, np.nan).pct_change() * 100
        
        # Generate detailed report
        report = [
            "✓✓✓ Strong Operating Cash Flow\n",
            "Robust core business performance, indicating that the company's operations are generating sufficient cash.",
            "This provides a solid foundation for growth and financial stability without relying on external financing.\n"
        ]

        improvement_found = False
        
        for i in range(1, len(data)):
            year = data['calendarYear'].iloc[i]
            cash_flow = data['operatingCashFlow'].iloc[i]
            cash_flow_change = data['Operating_Cash_Flow_Change'].iloc[i]

            # Check for notable increase in Operating Cash Flow (greater than the specified threshold)
            if cash_flow_change > cash_flow_threshold:
                report.append(
                    f"FY {year}: Operating Cash Flow = {self.format_number(cash_flow)} (↑ {self.format_percent(cash_flow_change)}%)"
                )
                improvement_found = True

        if not improvement_found:
            return None
        
        return "\n".join(report)

    ############################ PI13 ############################

    def analyze_decreasing_dpo(self, data, dpo_threshold=5):
        
        # Ensure necessary columns are present
        if 'accountPayables' not in data.columns or 'costOfRevenue' not in data.columns:
            return "DPO analysis requires 'accountPayables' and 'costOfRevenue' columns."            

        # Calculate Days Payable Outstanding (DPO)
        data['DPO'] = (data['accountPayables'] / data['costOfRevenue'].replace(0, np.nan)) * 365
        
        # Calculate percentage change in DPO
        data['DPO_Change'] = data['DPO'].pct_change() * 100
        
        # Generate detailed report
        report = [
            "✓✓✓ Decreasing Days Payable Outstanding (DPO)\n",
            "Strengthened supplier relationships and potential cost savings, as timely payments can lead to better terms or discounts.",
            "A balance is necessary to maintain optimal cash flow management without straining liquidity.\n"
        ]

        improvement_found = False
        
        for i in range(1, len(data)):
            year = data['calendarYear'].iloc[i]
            dpo = data['DPO'].iloc[i]
            dpo_change = data['DPO_Change'].iloc[i]

            # Check for notable decrease in DPO (greater than the specified threshold)
            if dpo_change < -dpo_threshold:  # DPO is decreasing by more than the threshold
                report.append(
                    f"FY {year}: DPO = {dpo:.2f} days (↓ {self.format_percent(abs(dpo_change))}%)"
                )
                improvement_found = True

        if not improvement_found:
            return None
        
        return "\n".join(report)
    
    ############################ PI14 ############################

    def analyze_increase_in_deferred_revenue(self, data, revenue_threshold=5):
        
        # Ensure necessary columns are present
        if 'deferredRevenue' not in data.columns:
            return "Deferred Revenue analysis requires 'deferredRevenue' column."    
        
        # Calculate percentage change in Deferred Revenue
        data['Deferred_Revenue_Change'] = data['deferredRevenue'].replace(0, np.nan).pct_change() * 100
        
        # Generate detailed report
        report = [
            "✓✓✓ Increase in Deferred Revenue\n",
            "Future revenue assurance, as deferred revenue represents payments received for services or products to be delivered.",
            "An increase suggests strong sales and customer commitment, providing predictability in future earnings.\n"
        ]

        improvement_found = False
        
        for i in range(1, len(data)):
            year = data['calendarYear'].iloc[i]
            deferred_revenue = data['deferredRevenue'].iloc[i]
            deferred_revenue_change = data['Deferred_Revenue_Change'].iloc[i]

            # Check for notable increase in Deferred Revenue (greater than the specified threshold)
            if deferred_revenue_change > revenue_threshold:
                report.append(
                    f"FY {year}: Deferred Revenue = {self.format_number(deferred_revenue)} (↑ {self.format_percent(deferred_revenue_change)}%)"
                )
                improvement_found = True

        if not improvement_found:
            return None
        
        return "\n".join(report)

    ############################ PI15 ############################

    def analyze_rd_investments(self, data, rd_threshold=5):
        
        # Ensure necessary columns are present
        if 'researchAndDevelopmentExpenses' not in data.columns:
            return "R&D Expense analysis requires 'researchAndDevelopmentExpenses' column."            

        # Calculate percentage change in R&D Expenses
        data['R&D_Change'] = data['researchAndDevelopmentExpenses'].replace(0, np.nan).pct_change() * 100
        
        # Generate detailed report
        report = [
            "✓✓✓ Patent Acquisitions or R&D Investments\n",
            "Investment in innovation and long-term growth, positioning the company to develop new products or improve existing ones.",
            "This can lead to competitive advantages, entry into new markets, and enhanced profitability through proprietary technologies.\n"
        ]

        improvement_found = False
        
        for i in range(1, len(data)):
            year = data['calendarYear'].iloc[i]
            rd_expenses = data['researchAndDevelopmentExpenses'].iloc[i]
            rd_change = data['R&D_Change'].iloc[i]

            # Check for notable increase in R&D Expenses (greater than the specified threshold)
            if rd_change > rd_threshold:
                report.append(
                    f"FY {year}: R&D Expenses = {self.format_number(rd_expenses)} (↑ {self.format_percent(rd_change)}%)"
                )
                improvement_found = True

        if not improvement_found:
            return None
        
        return "\n".join(report)
    