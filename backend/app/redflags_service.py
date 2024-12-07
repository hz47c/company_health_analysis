# app/services/redflags_service.py

import pandas as pd
import numpy as np
from app.models import BalanceSheet, IncomeStatement, CashFlow

class RedFlagsService:
    
    def get_financial_data_as_dataframe(self, ticker):
        # Fetch data from the database
        balance_sheets = BalanceSheet.query.filter_by(ticker=ticker).all()
        income_statements = IncomeStatement.query.filter_by(ticker=ticker).all()
        cash_flows = CashFlow.query.filter_by(ticker=ticker).all()

        # Initialize dictionary to hold the data
        data = {
            'calendarYear': [],

            # Balance Sheet
            'totalCurrentAssets': [],
            'cashAndCashEquivalents': [],
            'netReceivables': [],
            'inventory': [],
            'goodwill': [],
            'intangibleAssets': [],
            'totalAssets': [],
            'totalCurrentLiabilities': [],
            'accountPayables': [],
            'shortTermDebt': [],
            'totalDebt': [],
            'deferredRevenue': [],
            'totalStockholdersEquity': [],
            
            # Income Statement
            'Revenue': [],
            'Cost of Revenue': [],
            'Gross Profit': [],
            'Operating Expenses': [],
            'EBIT': [],
            'Interest Expense': [],
            'Net Income': [],
            'weightedAverageShsOut': [],
            
            # Cash Flow Statement
            'operatingCashFlow': [],
            'capitalExpenditure': [],
            'freeCashFlow': [],
            'dividendsPaid': []
        }

        # Populate data from BalanceSheet, IncomeStatement, and CashFlow tables
        for record in balance_sheets:
            data['calendarYear'].append(record.date[:4])
            data['totalCurrentAssets'].append(record.total_current_assets or np.nan)
            data['cashAndCashEquivalents'].append(record.cash_and_cash_equivalents or np.nan)
            data['netReceivables'].append(record.net_receivables or np.nan)
            data['inventory'].append(record.inventory or np.nan)
            data['goodwill'].append(record.goodwill or np.nan)
            data['intangibleAssets'].append(record.intangible_assets or np.nan)
            data['totalAssets'].append(record.total_assets or np.nan)
            data['totalCurrentLiabilities'].append(record.total_current_liabilities or np.nan)
            data['accountPayables'].append(record.account_payables or np.nan)
            data['shortTermDebt'].append(record.short_term_debt or np.nan)
            data['totalDebt'].append(record.total_debt or np.nan)
            data['deferredRevenue'].append(record.deferred_revenue or np.nan)
            data['totalStockholdersEquity'].append(record.total_stockholders_equity or np.nan)

        for record in income_statements:
            data['Revenue'].append(record.revenue or np.nan)
            data['Cost of Revenue'].append(record.cost_of_revenue or np.nan)
            data['Gross Profit'].append(record.gross_profit or np.nan)
            data['Operating Expenses'].append(record.operating_expenses or np.nan)
            data['EBIT'].append(record.operating_income or np.nan)
            data['Interest Expense'].append(record.interest_expense or np.nan)
            data['Net Income'].append(record.net_income or np.nan)
            data['weightedAverageShsOut'].append(record.weighted_average_shs_out or np.nan)

        for record in cash_flows:
            data['operatingCashFlow'].append(record.operating_cash_flow or np.nan)
            data['capitalExpenditure'].append(record.capital_expenditure or np.nan)
            data['freeCashFlow'].append(record.free_cash_flow or np.nan)
            data['dividendsPaid'].append(record.dividends_paid or np.nan)

        # Create a DataFrame from the dictionary
        df = pd.DataFrame(data)
        return df

    def analyze_red_flags(self, ticker):
        data = self.get_financial_data_as_dataframe(ticker)
        results = []

        # List of analysis functions to execute
        analysis_functions = [
            self.analyze_declining_revenue_increasing_income,
            self.analyze_debt_to_equity_ratio,
            self.analyze_cash_flow_vs_net_income,
            self.analyze_accounts_receivable_vs_sales,
            self.analyze_gross_profit_margin,
            self.analyze_inventory_turnover,
            self.analyze_goodwill_increase,
            self.analyze_interest_coverage,
            self.analyze_increasing_dso,
            self.analyze_negative_free_cash_flow,
            self.analyze_high_dividend_payout_poor_cash_flow,
            self.analyze_frequent_equity_issuances,
            self.analyze_short_term_debt
        ]

        for function in analysis_functions:
            result = function(data)
            if result:
                results.append(result)

        return "\n\n".join(results) if results else "No red flags identified."

    ############################ RF1 ############################

    def analyze_declining_revenue_increasing_income(self, data):
        # Calculate percentage change for Revenue and Net Income
        revenue_pct_change = data['Revenue'].pct_change(fill_method=None).fillna(0)
        income_pct_change = data['Net Income'].pct_change(fill_method=None).fillna(0)

        # Check for declining revenue and increasing net income
        declining_revenue = revenue_pct_change < 0
        increasing_income = income_pct_change > 0

        # Find the years where both conditions are met
        red_flag_years = data.loc[declining_revenue & increasing_income, 'calendarYear'].tolist()
        revenue_changes = revenue_pct_change[declining_revenue & increasing_income].tolist()
        income_changes = income_pct_change[declining_revenue & increasing_income].tolist()

        if red_flag_years:
            red_flags = []
            for year, rev_change, inc_change in zip(red_flag_years, revenue_changes, income_changes):
                red_flags.append(f"     > FY {year}: Revenue ↓ {abs(rev_change)*100:.2f}%, Net Income ↑ {inc_change*100:.2f}%")

            # Format the output
            details = "\n".join(red_flags)
            return (
                " ! Declining Revenue with Increasing Net Income\n\n"
                "   • Possible reliance on non-operational income (e.g., asset sales) or aggressive cost-cutting measures that may not be sustainable.\n"
                "   • It may mask underlying issues in the core business operations, indicating potential future declines in profitability once temporary measures fade.\n\n"
                f"{details}"
            )
        return None  # Return None if no red flag

    ############################ RF2 ############################

    def analyze_debt_to_equity_ratio(self, data):
        # Define the threshold for high leverage (adjustable based on industry)
        high_leverage_threshold = 2  # Example: Debt-to-Equity ratio above 2 is considered high

        # Ensure necessary columns are present
        if 'totalDebt' not in data.columns or 'totalStockholdersEquity' not in data.columns:
            return "Debt-to-Equity analysis requires 'totalDebt' and 'totalStockholdersEquity' columns."

        # Calculate Debt-to-Equity Ratio
        debt_to_equity = data['totalDebt'] / data['totalStockholdersEquity']

        # Calculate percentage change in Debt-to-Equity Ratio
        debt_to_equity_pct_change = debt_to_equity.pct_change(fill_method=None).fillna(0)
        increasing_ratio = debt_to_equity_pct_change > 0

        # Find the years where the ratio is already high or went from moderate to high
        red_flag_years = []
        ratio_changes = []

        for i in range(1, len(debt_to_equity)):
            if debt_to_equity[i] > high_leverage_threshold and increasing_ratio[i]:
                # Triggered when the ratio increases and is already in the high leverage zone
                red_flag_years.append(data['calendarYear'].iloc[i])
                ratio_changes.append(debt_to_equity_pct_change.iloc[i])
            elif debt_to_equity[i-1] <= high_leverage_threshold and debt_to_equity[i] > high_leverage_threshold:
                # Triggered when the ratio shifts from moderate to high
                red_flag_years.append(data['calendarYear'].iloc[i])
                ratio_changes.append(debt_to_equity_pct_change.iloc[i])

        if red_flag_years:
            red_flags = []
            for year, change in zip(red_flag_years, ratio_changes):
                ratio_value = debt_to_equity[data['calendarYear'] == year].values[0]
                red_flags.append(f"     > FY {year}: Debt-to-Equity Ratio = {ratio_value:.2f} (↑ {change*100:.2f}%)")

            # Format the output
            details = "\n".join(red_flags)
            return (
                " ! High or Increasing Debt Levels Relative to Equity\n\n"
                "   • Heightened financial risk due to increased leverage.\n"
                "   • The company may be over-reliant on debt financing, making it vulnerable to interest rate hikes and economic downturns.\n"
                "   • This can limit future borrowing capacity and increase default risk.\n\n"
                f"{details}"
            )
        return None  # Return None if no red flag

    ############################ RF3 ############################

    def analyze_cash_flow_vs_net_income(self, data):
        # Ensure necessary columns are present
        if 'operatingCashFlow' not in data.columns or 'Net Income' not in data.columns:
            return "Cash flow analysis requires 'operatingCashFlow' and 'Net Income' columns."

        # Calculate percentage change for Operating Cash Flow and Net Income
        cash_flow_pct_change = data['operatingCashFlow'].pct_change(fill_method=None).fillna(0)
        income_pct_change = data['Net Income'].pct_change(fill_method=None).fillna(0)

        # Check for declining cash flow and increasing net income
        declining_cash_flow = cash_flow_pct_change < 0
        increasing_income = income_pct_change > 0

        # Find the years where the red flag condition is met
        red_flag_years = data.loc[declining_cash_flow & increasing_income, 'calendarYear'].tolist()
        cash_flow_changes = cash_flow_pct_change[declining_cash_flow & increasing_income].tolist()
        income_changes = income_pct_change[declining_cash_flow & increasing_income].tolist()

        if red_flag_years:
            red_flags = []
            for year, cash_change, inc_change in zip(red_flag_years, cash_flow_changes, income_changes):
                red_flags.append(f"     > FY {year}: Net Income ↑ {inc_change*100:.2f}%, Cash Flow ↓ {abs(cash_change)*100:.2f}%")

            # Format the output
            details = "\n".join(red_flags)
            return (
                " ! Decreasing Cash Flow from Operations with Rising Net Income\n\n"
                "   • Potential earnings quality issues, suggesting that reported net income isn't translating into actual cash.\n"
                "   • This discrepancy could be due to non-cash revenue recognition or changes in working capital, raising concerns about the sustainability of earnings.\n\n"
                f"{details}"
            )
        return None  # Return None if no red flag

    ############################ RF4 ############################

    def analyze_accounts_receivable_vs_sales(self, data, caution_threshold=0.10, red_flag_threshold=0.20, critical_threshold=0.30):
        # Ensure necessary columns are present
        if 'netReceivables' not in data.columns or 'Revenue' not in data.columns:
            return "Accounts Receivable analysis requires 'netReceivables' and 'Revenue' columns."

        # Calculate the Accounts Receivable to Sales Ratio
        receivable_to_sales_ratio = data['netReceivables'] / data['Revenue']

        # Calculate percentage change in Accounts Receivable to Sales Ratio
        receivable_to_sales_pct_change = receivable_to_sales_ratio.pct_change(fill_method=None).fillna(0)

        # Classify years based on the value of Accounts Receivable to Sales Ratio
        caution_years = data.loc[(receivable_to_sales_ratio >= caution_threshold) & (receivable_to_sales_ratio < red_flag_threshold), 'calendarYear'].tolist()
        caution_ratios = receivable_to_sales_ratio[(receivable_to_sales_ratio >= caution_threshold) & (receivable_to_sales_ratio < red_flag_threshold)].tolist()
        caution_changes = receivable_to_sales_pct_change[(receivable_to_sales_ratio >= caution_threshold) & (receivable_to_sales_ratio < red_flag_threshold)].tolist()

        red_flag_years = data.loc[(receivable_to_sales_ratio >= red_flag_threshold) & (receivable_to_sales_ratio < critical_threshold), 'calendarYear'].tolist()
        red_flag_ratios = receivable_to_sales_ratio[(receivable_to_sales_ratio >= red_flag_threshold) & (receivable_to_sales_ratio < critical_threshold)].tolist()
        red_flag_changes = receivable_to_sales_pct_change[(receivable_to_sales_ratio >= red_flag_threshold) & (receivable_to_sales_ratio < critical_threshold)].tolist()

        critical_years = data.loc[receivable_to_sales_ratio >= critical_threshold, 'calendarYear'].tolist()
        critical_ratios = receivable_to_sales_ratio[receivable_to_sales_ratio >= critical_threshold].tolist()
        critical_changes = receivable_to_sales_pct_change[receivable_to_sales_ratio >= critical_threshold].tolist()

        output = []

        # Prepare output for all zones only if bad ratio is met
        if caution_years or red_flag_years or critical_years:
            output.append(" ! Growing Accounts Receivable as a Percentage of Sales\n")
            output.append("   • Indicates worsening collection issues or overly loose credit terms, potentially leading to cash flow problems.")
            output.append("   • Suggests rising bad debt expenses and declining credit quality of customers.\n")

        # Caution zone output
        if caution_years:
            caution_flags = []
            for year, ratio, change in zip(caution_years, caution_ratios, caution_changes):
                if change != 0:  # Skip 0% change
                    arrow = "↑" if change > 0 else "↓"
                    caution_flags.append(f"     > FY {year}: Accounts Receivable to Sales = {ratio*100:.2f}% ({arrow} {abs(change)*100:.2f}%)")
                else:
                    caution_flags.append(f"     > FY {year}: Accounts Receivable to Sales = {ratio*100:.2f}%")  # Display only ratio if 0% change
            if caution_flags:
                output.append(f"\n     Caution Zone: Accounts Receivable to Sales between 10%-20%\n{'\n'.join(caution_flags)}")

        # Red flag zone output
        if red_flag_years:
            red_flags = []
            for year, ratio, change in zip(red_flag_years, red_flag_ratios, red_flag_changes):
                if change != 0:  # Skip 0% change
                    arrow = "↑" if change > 0 else "↓"
                    red_flags.append(f"     > FY {year}: Accounts Receivable to Sales = {ratio*100:.2f}% ({arrow} {abs(change)*100:.2f}%)")
                else:
                    red_flags.append(f"     > FY {year}: Accounts Receivable to Sales = {ratio*100:.2f}%")  # Display only ratio if 0% change
            if red_flags:
                output.append(f"\n     Red Flag: Accounts Receivable to Sales between 20%-30%\n{'\n'.join(red_flags)}")

        # Critical zone output
        if critical_years:
            critical_flags = []
            for year, ratio, change in zip(critical_years, critical_ratios, critical_changes):
                if change != 0:  # Skip 0% change
                    arrow = "↑" if change > 0 else "↓"
                    critical_flags.append(f"     > FY {year}: Accounts Receivable to Sales = {ratio*100:.2f}% ({arrow} {abs(change)*100:.2f}%)")
                else:
                    critical_flags.append(f"     > FY {year}: Accounts Receivable to Sales = {ratio*100:.2f}%")  # Display only ratio if 0% change
            if critical_flags:
                output.append(f"\n     Critical Zone: Accounts Receivable to Sales above 30%\n{'\n'.join(critical_flags)}")

        # Join the output list into a single string
        return '\n'.join(output) if output else None  # Return formatted output or None if no caution or red flags

    ############################ RF5 ############################

    def analyze_gross_profit_margin(self, data, caution_threshold=-0.10, red_flag_threshold=-0.20, critical_threshold=-0.30):
        # Ensure necessary columns are present
        if 'Gross Profit' not in data.columns or 'Revenue' not in data.columns:
            return "Gross Profit Margin analysis requires 'Gross Profit' and 'Revenue' columns."

        # Calculate the Gross Profit Margin for each year
        gross_profit_margin = data['Gross Profit'] / data['Revenue']

        # Calculate percentage change in Gross Profit Margin year-over-year
        margin_pct_change = gross_profit_margin.pct_change(fill_method=None).fillna(0)

        # Identify years for Caution, Red Flag, and Critical Zones
        caution_years = data.loc[(margin_pct_change <= caution_threshold) & (margin_pct_change > red_flag_threshold), 'calendarYear'].tolist()
        caution_changes = margin_pct_change[(margin_pct_change <= caution_threshold) & (margin_pct_change > red_flag_threshold)].tolist()

        red_flag_years = data.loc[(margin_pct_change <= red_flag_threshold) & (margin_pct_change > critical_threshold), 'calendarYear'].tolist()
        red_flag_changes = margin_pct_change[(margin_pct_change <= red_flag_threshold) & (margin_pct_change > critical_threshold)].tolist()

        critical_years = data.loc[margin_pct_change <= critical_threshold, 'calendarYear'].tolist()
        critical_changes = margin_pct_change[margin_pct_change <= critical_threshold].tolist()

        output = []

        # Prepare output for all zones
        if caution_years or red_flag_years or critical_years:
            output.append(" ! Decreasing Gross Profit Margins\n")
            output.append("   • Suggests worsening efficiency or rising costs of goods sold, which can erode profitability.")
            output.append("   • It may indicate market pressures or competitive challenges affecting pricing power, requiring a strategic review to address cost management.\n")

        # Caution zone output
        if caution_years:
            caution_flags = []
            for year, change in zip(caution_years, caution_changes):
                caution_flags.append(f"     > FY {year}: Gross Profit Margin ↓ {abs(change) * 100:.2f}%")
            output.append(f"\n     Caution Zone: Gross Profit Margin decreased between 10%-20%\n{'\n'.join(caution_flags)}")

        # Red flag zone output
        if red_flag_years:
            red_flags = []
            for year, change in zip(red_flag_years, red_flag_changes):
                red_flags.append(f"     > FY {year}: Gross Profit Margin ↓ {abs(change) * 100:.2f}%")
            output.append(f"\n     Red Flag: Gross Profit Margin decreased above 20%\n{'\n'.join(red_flags)}")

        # Critical zone output
        if critical_years:
            critical_flags = []
            for year, change in zip(critical_years, critical_changes):
                critical_flags.append(f"     > FY {year}: Gross Profit Margin ↓ {abs(change) * 100:.2f}%")
            output.append(f"\n     Critical Zone: Gross Profit Margin decreased above 30%\n{'\n'.join(critical_flags)}")

        # Join the output list into a single string
        return '\n'.join(output) if output else None  # Return formatted output or None if no caution or red flags

    ############################ RF6 ############################

    def analyze_inventory_turnover(self, data, caution_threshold=-0.05, red_flag_threshold=-0.10, critical_threshold=-0.20):
        # Ensure necessary columns are present
        if 'inventory' not in data.columns or 'Cost of Revenue' not in data.columns:
            return "Inventory Turnover analysis requires 'inventory' and 'Cost of Revenue' columns."

        # Calculate Inventory Turnover Ratio
        inventory_turnover = data['Cost of Revenue'] / data['inventory']

        # Calculate percentage change in Inventory Turnover Ratio
        turnover_pct_change = inventory_turnover.pct_change(fill_method=None).fillna(0)

        # Identify years where turnover decreased in Caution, Red Flag, and Critical Zones
        caution_years = data.loc[(turnover_pct_change <= caution_threshold) & (turnover_pct_change > red_flag_threshold), 'calendarYear'].tolist()
        caution_changes = turnover_pct_change[(turnover_pct_change <= caution_threshold) & (turnover_pct_change > red_flag_threshold)].tolist()

        red_flag_years = data.loc[(turnover_pct_change <= red_flag_threshold) & (turnover_pct_change > critical_threshold), 'calendarYear'].tolist()
        red_flag_changes = turnover_pct_change[(turnover_pct_change <= red_flag_threshold) & (turnover_pct_change > critical_threshold)].tolist()

        critical_years = data.loc[turnover_pct_change <= critical_threshold, 'calendarYear'].tolist()
        critical_changes = turnover_pct_change[turnover_pct_change <= critical_threshold].tolist()

        output = []

        # Prepare output for decreasing turnover ratios
        if caution_years or red_flag_years or critical_years:
            output.append(" ! Increasing Inventory Levels Relative to Sales\n")
            output.append("   • Indicates potential overstocking or declining demand for products, which can lead to obsolescence.")
            output.append("   • It can tie up capital that could be used for growth or other investments, posing risks to cash flow and profitability.\n")

        # Caution zone output
        if caution_years:
            caution_flags = []
            for year, change in zip(caution_years, caution_changes):
                caution_flags.append(f"     > FY {year}: Inventory Turnover ↓ {abs(change) * 100:.2f}%")
            output.append(f"\n     Caution Zone: Inventory Turnover decreased between 5%-10%\n{'\n'.join(caution_flags)}")

        # Red flag zone output
        if red_flag_years:
            red_flags = []
            for year, change in zip(red_flag_years, red_flag_changes):
                red_flags.append(f"     > FY {year}: Inventory Turnover ↓ {abs(change) * 100:.2f}%")
            output.append(f"\n     Red Flag: Inventory Turnover decreased above 10%\n{'\n'.join(red_flags)}")

        # Critical zone output
        if critical_years:
            critical_flags = []
            for year, change in zip(critical_years, critical_changes):
                critical_flags.append(f"     > FY {year}: Inventory Turnover ↓ {abs(change) * 100:.2f}%")
            output.append(f"\n     Critical Zone: Inventory Turnover decreased above 20%\n{'\n'.join(critical_flags)}")

        # Join the output list into a single string
        return '\n'.join(output) if output else None  # Return formatted output or None if no issues

    ############################ RF7 ############################

    def analyze_goodwill_increase(self, data, caution_threshold=0.10, red_flag_threshold=0.20):

        # Calculate year-over-year percentage change in Goodwill
        goodwill_pct_change = data['goodwill'].pct_change(fill_method=None).fillna(0)

        # Identify years where the YoY increase falls within the caution or red flag thresholds
        caution_years = data.loc[(goodwill_pct_change > caution_threshold) & (goodwill_pct_change <= red_flag_threshold), 'calendarYear'].tolist()
        caution_changes = goodwill_pct_change[(goodwill_pct_change > caution_threshold) & (goodwill_pct_change <= red_flag_threshold)].tolist()
        
        red_flag_years = data.loc[goodwill_pct_change > red_flag_threshold, 'calendarYear'].tolist()
        red_flag_changes = goodwill_pct_change[goodwill_pct_change > red_flag_threshold].tolist()
        
        output = []

        # Caution zone output
        if caution_years:
            caution_flags = []
            for year, change in zip(caution_years, caution_changes):
                caution_flags.append(f"     > FY {year}: Goodwill ↑ {change * 100:.2f}%")
            output.append(f"\n     Caution Zone: Goodwill increased between 10%-20%\n{'\n'.join(caution_flags)}")

        # Red flag zone output
        if red_flag_years:
            red_flags = []
            for year, change in zip(red_flag_years, red_flag_changes):
                red_flags.append(f"     > FY {year}: Goodwill ↑ {change * 100:.2f}%")
            output.append(f"\n     Red Flag: Goodwill increased above 20%\n{'\n'.join(red_flags)}")

        # If there are caution or red flags, add the warning text
        if output:
            warning_text = (
                " ! Large Increases in Goodwill or Intangible Assets\n\n"
                "   • Risk of overpaying for acquisitions, leading to future impairment charges if expected synergies or performance do not materialize\n"
                "   • This can negatively impact future earnings and may suggest aggressive growth strategies without adequate due diligence\n\n"
            )
            
            return f"{warning_text}{''.join(output)}"
        return None  # Return None if no red flag

    ############################ RF8 ############################

    def analyze_interest_coverage(self, data, caution_threshold=2.5, red_flag_threshold=1.5, critical_threshold=1.0):
        # Ensure necessary columns are present
        if 'EBIT' not in data.columns or 'Interest Expense' not in data.columns:
            return "Interest Coverage analysis requires 'EBIT' and 'Interest Expense' columns."

        # Calculate Interest Coverage Ratio
        data['Interest Coverage'] = data['EBIT'] / data['Interest Expense']

        # Identify years where the coverage falls into caution, red flag, or critical zones
        caution_years = data.loc[(data['Interest Coverage'] <= caution_threshold) & (data['Interest Coverage'] > red_flag_threshold), 'calendarYear'].tolist()
        caution_values = data.loc[(data['Interest Coverage'] <= caution_threshold) & (data['Interest Coverage'] > red_flag_threshold), 'Interest Coverage'].tolist()
        
        red_flag_years = data.loc[(data['Interest Coverage'] <= red_flag_threshold) & (data['Interest Coverage'] > critical_threshold), 'calendarYear'].tolist()
        red_flag_values = data.loc[(data['Interest Coverage'] <= red_flag_threshold) & (data['Interest Coverage'] > critical_threshold), 'Interest Coverage'].tolist()
        
        critical_years = data.loc[data['Interest Coverage'] <= critical_threshold, 'calendarYear'].tolist()
        critical_values = data.loc[data['Interest Coverage'] <= critical_threshold, 'Interest Coverage'].tolist()

        output = []

        # Prepare output
        if caution_years or red_flag_years or critical_years:
            output.append(" ! Declining Interest Coverage Ratio\n")
            output.append("   • Signals growing difficulties in meeting interest obligations, raising default risk.")
            output.append("   • A declining ratio can impact credit ratings and future borrowing costs, potentially limiting financial flexibility.\n")

        # Caution zone output
        if caution_years:
            caution_flags = []
            for i, year in enumerate(caution_years):
                previous_year_value = data.loc[data['calendarYear'] == year - 1, 'Interest Coverage'].values[0] if year - 1 in data['calendarYear'].values else None
                
                # Calculate change for the current caution year
                if previous_year_value is not None:
                    change = (caution_values[i] - previous_year_value) / previous_year_value * 100
                    direction = "↓" if change < 0 else "↑"
                    if change != 0:  # Skip 0% change
                        caution_flags.append(f"     > FY {year}: Interest Coverage = {caution_values[i]:.2f} ({direction} {abs(change):.2f}%)")
                    else:
                        caution_flags.append(f"     > FY {year}: Interest Coverage = {caution_values[i]:.2f}")
                else:
                    caution_flags.append(f"     > FY {year}: Interest Coverage = {caution_values[i]:.2f}")
            
            output.append(f"\n     Caution Zone: Interest Coverage between {red_flag_threshold}-{caution_threshold}\n{'\n'.join(caution_flags)}")

        # Red flag zone output
        if red_flag_years:
            red_flags = []
            for i, year in enumerate(red_flag_years):
                previous_year_value = data.loc[data['calendarYear'] == year - 1, 'Interest Coverage'].values[0] if year - 1 in data['calendarYear'].values else None
                
                # Calculate change for the current red flag year
                if previous_year_value is not None:
                    change = (red_flag_values[i] - previous_year_value) / previous_year_value * 100
                    direction = "↓" if change < 0 else "↑"
                    if change != 0:  # Skip 0% change
                        red_flags.append(f"     > FY {year}: Interest Coverage = {red_flag_values[i]:.2f} ({direction} {abs(change):.2f}%)")
                    else:
                        red_flags.append(f"     > FY {year}: Interest Coverage = {red_flag_values[i]:.2f}")
                else:
                    red_flags.append(f"     > FY {year}: Interest Coverage = {red_flag_values[i]:.2f}")
            
            output.append(f"\n     Red Flag: Interest Coverage between {critical_threshold}-{red_flag_threshold}\n{'\n'.join(red_flags)}")

        # Critical zone output
        if critical_years:
            critical_flags = []
            for i, year in enumerate(critical_years):
                previous_year_value = data.loc[data['calendarYear'] == year - 1, 'Interest Coverage'].values[0] if year - 1 in data['calendarYear'].values else None
                
                # Calculate change for the current critical year
                if previous_year_value is not None:
                    change = (critical_values[i] - previous_year_value) / previous_year_value * 100
                    direction = "↓" if change < 0 else "↑"
                    if change != 0:  # Skip 0% change
                        critical_flags.append(f"     > FY {year}: Interest Coverage = {critical_values[i]:.2f} ({direction} {abs(change):.2f}%)")
                    else:
                        critical_flags.append(f"     > FY {year}: Interest Coverage = {critical_values[i]:.2f}")
                else:
                    critical_flags.append(f"     > FY {year}: Interest Coverage = {critical_values[i]:.2f}")
            
            output.append(f"\n     Critical Zone: Interest Coverage below {critical_threshold}\n{'\n'.join(critical_flags)}")

        # Join the output list into a single string
        return '\n'.join(output) if output else None  # Return formatted output or None if no caution or red flags

    ############################ RF9 ############################

    def analyze_increasing_dso(self, data, bad_dso_threshold=60):
        # Calculate DSO
        data['DSO'] = (data['netReceivables'] / data['Revenue']) * 365

        # Check if DSO is already bad
        bad_dso = data['DSO'] > bad_dso_threshold

        # Calculate year-over-year percentage change in DSO
        dso_pct_change = data['DSO'].pct_change(fill_method=None).fillna(0) * 100

        # Filter for years where DSO is bad
        caution_zone = dso_pct_change[(dso_pct_change > 5) & (dso_pct_change <= 10) & bad_dso]
        red_flag_zone = dso_pct_change[(dso_pct_change > 10) & bad_dso]

        # Prepare output
        output = []

        # Caution Zone
        if not caution_zone.empty:
            output.append("\n     Caution Zone: DSO increased between 5%-10%")
            for idx in caution_zone.index:
                year = data['calendarYear'].iloc[idx]
                change = caution_zone[idx]
                dso_value = data['DSO'].iloc[idx]
                output.append(f"     > FY {year}: DSO = {dso_value:.2f} (↑ {change:.2f}%)")

        # \n     Red Flag Zone
        if not red_flag_zone.empty:
            output.append("\n     Red Flag: DSO increased above 10%")
            for idx in red_flag_zone.index:
                year = data['calendarYear'].iloc[idx]
                change = red_flag_zone[idx]
                dso_value = data['DSO'].iloc[idx]
                output.append(f"     > FY {year}: DSO = {dso_value:.2f} (↑ {change:.2f}%)")

        # Check for output presence
        if output:
            return (
                " ! Increasing Days Sales Outstanding\n\n"
                "   • Delayed cash inflows, affecting liquidity\n"
                "   • An increasing DSO suggests the company is taking longer to collect payments, which may be due to customer financial strain\n" 
                "     or ineffective collection processes, potentially leading to cash shortages\n\n" +
                "\n".join(output)
            )
        else:
            return None  # Return None if no red flag

    ############################ RF10 ############################

    def analyze_negative_free_cash_flow(self, data):

        # Check for negative Free Cash Flow
        negative_fcf = data[data['freeCashFlow'] < 0]

        # Prepare output
        output = []

        if not negative_fcf.empty:
            for year, fcf in zip(negative_fcf['calendarYear'], negative_fcf['freeCashFlow']):
                output.append(f"     > FY {year}: Free Cash Flow = {fcf:.0f}")

        # Check for output presence
        if output:
            return (
                " ! Negative Free Cash Flow\n\n"
                "   • Insufficient internal funds to support operations and growth, potentially requiring external financing\n"
                "   • Persistent negative free cash flow can indicate unsustainable business models or overinvestment without adequate returns, increasing financial risk\n\n" +
                "\n".join(output).replace('-', '-$')
            )
        else:
            return None  # Return None if no red flag

    ############################ RF11 ############################

    def analyze_high_dividend_payout_poor_cash_flow(self, data):
        output = []
        
        # Calculate Dividend Payout Ratio
        data['payout_ratio'] = data['dividendsPaid'] / data['Net Income']

        # Calculate the percentage change in payout ratio
        payout_ratio_pct_change = data['payout_ratio'].pct_change(fill_method=None).fillna(0)

        # Filter for companies with payout ratio > 50% and operating cash flow < dividends paid
        high_payout_poor_cash_flow = data[
            (data['payout_ratio'] > 0.5) & 
            (data['operatingCashFlow'] < data['dividendsPaid'])
        ]
        
        # Prepare output
        if not high_payout_poor_cash_flow.empty:
            for idx, row in high_payout_poor_cash_flow.iterrows():
                pct_change = payout_ratio_pct_change[idx] * 100  # Convert to percentage
                change_symbol = "↑" if pct_change > 0 else "↓"
                output.append(
                    f"     > FY {int(row['calendarYear'])}: Payout Ratio = {row['payout_ratio']:.2f} ({change_symbol} {abs(pct_change):.2f}%), "
                    f"Operating Cash Flow = {int(row['operatingCashFlow'])}, Dividends Paid = {int(row['dividendsPaid'])}"
                )

        # Check for output presence
        if output:
            return (
                " ! High Dividend Payout with Poor Cash Flow\n\n"
                "   • Unsustainable dividend policy, possibly leading to increased debt or depletion of cash reserves.\n"
                "   • This situation may indicate management's attempt to maintain investor confidence at the expense of long-term financial stability.\n\n" +
                "\n".join(output)
            )
        else:
            return None  # Return None if no red flag

    ############################ RF12 ############################

    def analyze_frequent_equity_issuances(self, data):

        # Calculate year-over-year change in shares outstanding
        data['shares_change'] = data['weightedAverageShsOut'].pct_change(fill_method=None)

        # Filter for significant increases in shares outstanding (e.g., more than 5% increase)
        equity_issuances = data[data['shares_change'] > 0.05]

        # Prepare output
        output = []
        
        if not equity_issuances.empty:
            for year, change, shares in zip(equity_issuances['calendarYear'], equity_issuances['shares_change'], equity_issuances['weightedAverageShsOut']):
                output.append(f"     > FY {year}: Shares Outstanding ↑ {change:.2%}")

        # Check if any red flags are found
        if output:
            return (
                " ! Frequent Equity Issuances\n\n"
                "   • Dilution of existing shareholders' equity and potential signal of cash flow problems.\n"
                "   • Reliance on issuing new shares may indicate that the company cannot generate sufficient internal funds.\n"
                "   • This may undermine investor confidence and negatively affect earnings per share (EPS).\n\n" +
                "\n".join(output)
            )
        else:
            return None  # Return None if no red flags are found
        
    ############################ RF13 ############################

    def analyze_short_term_debt(self, data, caution_threshold=0.10, red_flag_threshold=0.15):
        # Calculate year-over-year percentage change in short-term debt
        short_term_debt_pct_change = data['shortTermDebt'].pct_change(fill_method=None).fillna(0)

        # Identify years where the YoY increase falls within the caution or red flag thresholds
        caution_years = data.loc[(short_term_debt_pct_change > caution_threshold) & 
                                (short_term_debt_pct_change <= red_flag_threshold), 'calendarYear'].tolist()
        caution_changes = short_term_debt_pct_change[(short_term_debt_pct_change > caution_threshold) & 
                                                    (short_term_debt_pct_change <= red_flag_threshold)].tolist()
        
        red_flag_years = data.loc[short_term_debt_pct_change > red_flag_threshold, 'calendarYear'].tolist()
        red_flag_changes = short_term_debt_pct_change[short_term_debt_pct_change > red_flag_threshold].tolist()
        
        output = []

        # Add warning text
        warning_text = (
            " ! Unusual Increase in Short-Term Debt\n\n"
            "   • Potential liquidity crunch, as reliance on short-term financing may indicate cash flow issues.\n"
            "   • Short-term debt often carries higher rollover risk and may reflect difficulties in securing long-term financing, raising concerns about financial stability.\n\n"
        )
        
        # Caution zone output
        if caution_years:
            caution_flags = []
            for year, change in zip(caution_years, caution_changes):
                caution_flags.append(f"     > FY {year}: Short-Term Debt ↑ {change * 100:.2f}%")
            output.append(f"\n     Caution Zone: Short-Term Debt increased between 10%-15%\n{'\n'.join(caution_flags)}")

        # Red flag zone output
        if red_flag_years:
            red_flags = []
            for year, change in zip(red_flag_years, red_flag_changes):
                red_flags.append(f"     > FY {year}: Short-Term Debt ↑ {change * 100:.2f}%")
            output.append(f"\n     Red Flag: Short-Term Debt increased above 15%\n{'\n'.join(red_flags)}")

        # Combine warning text with output
        if output:
            return f"{warning_text}{'\n'.join(output)}"
        
        return None  # Return None if no red flag is found
