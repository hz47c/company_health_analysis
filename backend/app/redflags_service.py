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
            'revenue': [],
            'costOfRevenue': [],
            'grossProfit': [],
            'operatingExpenses': [],
            'operatingIncome': [],
            'interestExpense': [],
            'netIncome': [],
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
            data['revenue'].append(record.revenue or np.nan)
            data['costOfRevenue'].append(record.cost_of_revenue or np.nan)
            data['grossProfit'].append(record.gross_profit or np.nan)
            data['operatingExpenses'].append(record.operating_expenses or np.nan)
            data['operatingIncome'].append(record.operating_income or np.nan)
            data['interestExpense'].append(record.interest_expense or np.nan)
            data['netIncome'].append(record.net_income or np.nan)
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

        # Sort data by calendar year to ensure chronological order
        data = data.sort_values('calendarYear').reset_index(drop=True)

        results = []

        # List of analysis functions to execute
        analysis_functions = [
            self.analyze_declining_revenue_increasing_income,
            self.analyze_debt_to_equity_ratio,
            self.analyze_declining_operating_cash_flow_increasing_income,
            self.analyze_accounts_receivable_vs_sales,
            self.analyze_gross_profit_margin,
            self.analyze_inventory_turnover,
            self.analyze_goodwill_increase,
            self.analyze_interest_coverage,
            self.analyze_increasing_dso,
            self.analyze_negative_free_cash_flow,
            self.analyze_high_dividend_payout_poor_cash_flow,
            self.analyze_large_equity_issuances,
            self.analyze_short_term_debt
        ]

        for function in analysis_functions:
            result = function(data)
            if result:
                results.append(result)
                results.append("_____________________________________")

        return "\n\n".join(results) if results else "No red flags identified."

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

    # Individual red flag analysis functions

    ############################ RF1 ############################

    def analyze_declining_revenue_increasing_income(self, data):
        
        # Ensure necessary columns are present
        if 'revenue' not in data.columns or 'netIncome' not in data.columns:
            return "Revenue and Net Income analysis requires 'revenue' and 'netIncome' columns."
        
        # Calculate percentage change for Revenue and Net Income
        revenue_pct_change = data['revenue'].replace(0, np.nan).pct_change()
        income_pct_change = data['netIncome'].replace(0, np.nan).pct_change()
        
        # Check for declining revenue
        declining_revenue = revenue_pct_change < 0
        
        # Check for increasing or improving net income
        increasing_income = (income_pct_change > 0) & (data['netIncome'] > 0)
        worsening_income = (income_pct_change < 0) & (data['netIncome'] < 0)

        # Find the years where revenue declines but net income improves
        red_flag_years = data.loc[declining_revenue & increasing_income & ~worsening_income, 'calendarYear'].tolist()
        revenue_changes = revenue_pct_change[declining_revenue & increasing_income & ~worsening_income].tolist()
        income_changes = income_pct_change[declining_revenue & increasing_income & ~worsening_income].tolist()

        if red_flag_years:
            red_flags = []
            for year, rev_change, inc_change in zip(red_flag_years, revenue_changes, income_changes):
                revenue = data.loc[data['calendarYear'] == year, 'revenue'].values[0]
                netIncome = data.loc[data['calendarYear'] == year, 'netIncome'].values[0]
                red_flags.append(f"FY {year}: Revenue = {self.format_number(revenue)} (↓ {self.format_percent(abs(rev_change) * 100)}%), Net Income = {self.format_number(netIncome)} (↑ {self.format_percent(inc_change * 100)}%)")

            # Format the output
            details = "\n".join(red_flags)
            return (
                "!!! Declining Revenue with Increasing Net Income\n\n"
                "Possible reliance on non-operational income (e.g., asset sales) or aggressive cost-cutting measures that may not be sustainable.\n"
                "It may mask underlying issues in the core business operations, indicating potential future declines in profitability once temporary measures fade.\n\n"
                f"{details}"
            )
        return None

    ############################ RF2 ############################

    def analyze_debt_to_equity_ratio(self, data):

        # Ensure necessary columns are present
        if 'totalDebt' not in data.columns or 'totalStockholdersEquity' not in data.columns:
            return "Debt-to-Equity analysis requires 'totalDebt' and 'totalStockholdersEquity' columns."
        
        # Define the threshold for high leverage (adjustable based on industry)
        high_leverage_threshold = 2  # Example: Debt-to-Equity ratio above 2 is considered high

        # Calculate Debt-to-Equity Ratio
        debt_to_equity = data['totalDebt'] / data['totalStockholdersEquity'].replace(0, np.nan)

        # Calculate percentage change in Debt-to-Equity Ratio
        debt_to_equity_pct_change = debt_to_equity.pct_change()
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
                red_flags.append(f"FY {year}: Debt-to-Equity Ratio = {ratio_value:.2f} (↑ {self.format_percent(change * 100)}%)")

            # Format the output
            details = "\n".join(red_flags)
            return (
                "!!! High or Increasing Debt Levels Relative to Equity\n\n"
                "Heightened financial risk due to increased leverage.\n"
                "The company may be over-reliant on debt financing, making it vulnerable to interest rate hikes and economic downturns.\n"
                "This can limit future borrowing capacity and increase default risk.\n\n"
                f"{details}"
            )
        return None

    ############################ RF3 ############################

    def analyze_declining_operating_cash_flow_increasing_income(self, data):
        
        # Ensure necessary columns are present
        if 'operatingCashFlow' not in data.columns or 'netIncome' not in data.columns:
            return "Operating Cash Flow and Net Income analysis requires 'operatingCashFlow' and 'netIncome' columns."
        
        # Calculate percentage change for Operating Cash Flow and Net Income
        operating_cash_flow_pct_change = data['operatingCashFlow'].replace(0, np.nan).pct_change()
        income_pct_change = data['netIncome'].replace(0, np.nan).pct_change()
        
        # Check for declining Operating Cash Flow
        declining_operating_cash_flow = operating_cash_flow_pct_change < 0
        
        # Check for increasing or improving net income
        increasing_income = (income_pct_change > 0) & (data['netIncome'] > 0)
        worsening_income = (income_pct_change < 0) & (data['netIncome'] < 0)

        # Find the years where Operating Cash Flow declines but net income improves
        red_flag_years = data.loc[declining_operating_cash_flow & increasing_income & ~worsening_income, 'calendarYear'].tolist()
        operating_cash_flow_changes = operating_cash_flow_pct_change[declining_operating_cash_flow & increasing_income & ~worsening_income].tolist()
        income_changes = income_pct_change[declining_operating_cash_flow & increasing_income & ~worsening_income].tolist()

        if red_flag_years:
            red_flags = []
            for year, rev_change, inc_change in zip(red_flag_years, operating_cash_flow_changes, income_changes):
                operatingCashFlow = data.loc[data['calendarYear'] == year, 'operatingCashFlow'].values[0]
                netIncome = data.loc[data['calendarYear'] == year, 'netIncome'].values[0]
                red_flags.append(f"FY {year}: Net Income = {self.format_number(netIncome)} (↑ {self.format_percent(inc_change * 100)}%), Operating Cash Flow = {self.format_number(operatingCashFlow)} (↓ {self.format_percent(abs(rev_change) * 100)}%)")

            # Format the output
            details = "\n".join(red_flags)
            return (
                "!!! Rising Net Income with Decreasing Cash Flow from Operations\n\n"
                "Potential earnings quality issues, suggesting that reported net income isn't translating into actual cash.\n"
                "This discrepancy could be due to non-cash revenue recognition or changes in working capital, raising concerns about the sustainability of earnings.\n\n"
                f"{details}"
            )
        return None

    ############################ RF4 ############################

    def analyze_accounts_receivable_vs_sales(self, data, caution_threshold=0.15, red_flag_threshold=0.20, critical_threshold=0.30):
        
        # Ensure necessary columns are present
        if 'netReceivables' not in data.columns or 'revenue' not in data.columns:
            return "Accounts Receivable analysis requires 'netReceivables' and 'revenue' columns."

        # Calculate the Accounts Receivable to Sales Ratio
        receivable_to_sales_ratio = data['netReceivables'] / data['revenue'].replace(0, np.nan)

        # Calculate percentage change in Accounts Receivable to Sales Ratio
        receivable_to_sales_pct_change = receivable_to_sales_ratio.pct_change()

        # Remove NaN changes (typically the first year) from the analysis
        receivable_to_sales_pct_change.iloc[0] = None  # Set the first year explicitly to None

        # Classify years based on the value of Accounts Receivable to Sales Ratio
        caution_years = data.loc[(receivable_to_sales_ratio >= caution_threshold) & (receivable_to_sales_ratio < red_flag_threshold) & receivable_to_sales_pct_change.notna(), 'calendarYear'].tolist()
        caution_ratios = receivable_to_sales_ratio[(receivable_to_sales_ratio >= caution_threshold) & (receivable_to_sales_ratio < red_flag_threshold) & receivable_to_sales_pct_change.notna()].tolist()
        caution_changes = receivable_to_sales_pct_change[(receivable_to_sales_ratio >= caution_threshold) & (receivable_to_sales_ratio < red_flag_threshold) & receivable_to_sales_pct_change.notna()].tolist()

        red_flag_years = data.loc[(receivable_to_sales_ratio >= red_flag_threshold) & (receivable_to_sales_ratio < critical_threshold) & receivable_to_sales_pct_change.notna(), 'calendarYear'].tolist()
        red_flag_ratios = receivable_to_sales_ratio[(receivable_to_sales_ratio >= red_flag_threshold) & (receivable_to_sales_ratio < critical_threshold) & receivable_to_sales_pct_change.notna()].tolist()
        red_flag_changes = receivable_to_sales_pct_change[(receivable_to_sales_ratio >= red_flag_threshold) & (receivable_to_sales_ratio < critical_threshold) & receivable_to_sales_pct_change.notna()].tolist()

        critical_years = data.loc[(receivable_to_sales_ratio >= critical_threshold) & receivable_to_sales_pct_change.notna(), 'calendarYear'].tolist()
        critical_ratios = receivable_to_sales_ratio[(receivable_to_sales_ratio >= critical_threshold) & receivable_to_sales_pct_change.notna()].tolist()
        critical_changes = receivable_to_sales_pct_change[(receivable_to_sales_ratio >= critical_threshold) & receivable_to_sales_pct_change.notna()].tolist()

        output = []

        # Prepare output for all zones only if bad ratio is met
        if caution_years or red_flag_years or critical_years:
            output.append("!!! Growing Accounts Receivable as a Percentage of Sales\n")
            output.append("Indicates worsening collection issues or overly loose credit terms, potentially leading to cash flow problems.")
            output.append("Suggests rising bad debt expenses and declining credit quality of customers.")

        # Caution zone output
        if caution_years:
            caution_flags = []
            for year, ratio, change in zip(caution_years, caution_ratios, caution_changes):
                arrow = "↑" if change > 0 else "↓"
                caution_flags.append(f"FY {year}: Accounts Receivable to Sales = {self.format_percent(ratio * 100)}% ({arrow} {self.format_percent(abs(change) * 100)}%)")
            if caution_flags:
                output.append(f"\nCaution Zone: Accounts Receivable to Sales between 15%-20%\n{'\n'.join(caution_flags)}")

        # Red flag zone output
        if red_flag_years:
            red_flags = []
            for year, ratio, change in zip(red_flag_years, red_flag_ratios, red_flag_changes):
                arrow = "↑" if change > 0 else "↓"
                red_flags.append(f"FY {year}: Accounts Receivable to Sales = {self.format_percent(ratio * 100)}% ({arrow} {self.format_percent(abs(change) * 100)}%)")
            if red_flags:
                output.append(f"\nRed Flag: Accounts Receivable to Sales between 20%-30%\n{'\n'.join(red_flags)}")

        # Critical zone output
        if critical_years:
            critical_flags = []
            for year, ratio, change in zip(critical_years, critical_ratios, critical_changes):
                arrow = "↑" if change > 0 else "↓"
                critical_flags.append(f"FY {year}: Accounts Receivable to Sales = {self.format_percent(ratio * 100)}% ({arrow} {self.format_percent(abs(change) * 100)}%)")
            if critical_flags:
                output.append(f"\nCritical Zone: Accounts Receivable to Sales above 30%\n{'\n'.join(critical_flags)}")

        return '\n'.join(output) if output else None

    ############################ RF5 ############################

    def analyze_gross_profit_margin(self, data, caution_threshold=-0.10, red_flag_threshold=-0.20, critical_threshold=-0.30):
        
        # Ensure necessary columns are present
        if 'grossProfit' not in data.columns or 'revenue' not in data.columns:
            return "Gross Profit Margin analysis requires 'grossProfit' and 'revenue' columns."

        # Calculate the Gross Profit Margin for each year
        data['gross_profit_margin'] = data['grossProfit'] / data['revenue'].replace(0, np.nan)

        # Calculate percentage change in Gross Profit Margin year-over-year
        margin_pct_change = data['gross_profit_margin'].pct_change()

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
            output.append("!!! Decreasing Gross Profit Margins\n")
            output.append("Suggests worsening efficiency or rising costs of goods sold, which can erode profitability.")
            output.append("It may indicate market pressures or competitive challenges affecting pricing power, requiring a strategic review to address cost management.")

        # Caution zone output
        if caution_years:
            caution_flags = []
            for year, change in zip(caution_years, caution_changes):
                gross_profit_margin = data.loc[data['calendarYear'] == year, 'gross_profit_margin'].values[0]
                caution_flags.append(f"FY {year}: Gross Profit Margin = {self.format_percent(gross_profit_margin * 100)}% (↓ {self.format_percent(abs(change) * 100)}%)")
            output.append(f"\nCaution Zone: Gross Profit Margin decreased between 10%-20%\n{'\n'.join(caution_flags)}")

        # Red flag zone output
        if red_flag_years:
            red_flags = []
            for year, change in zip(red_flag_years, red_flag_changes):
                gross_profit_margin = data.loc[data['calendarYear'] == year, 'gross_profit_margin'].values[0]
                red_flags.append(f"FY {year}: Gross Profit Margin = {self.format_percent(gross_profit_margin * 100)}% (↓ {self.format_percent(abs(change) * 100)}%)")
            output.append(f"\nRed Flag: Gross Profit Margin decreased above 20%\n{'\n'.join(red_flags)}")

        # Critical zone output
        if critical_years:
            critical_flags = []
            for year, change in zip(critical_years, critical_changes):
                gross_profit_margin = data.loc[data['calendarYear'] == year, 'gross_profit_margin'].values[0]
                critical_flags.append(f"FY {year}: Gross Profit Margin = {self.format_percent(gross_profit_margin * 100)}% (↓ {self.format_percent(abs(change) * 100)}%)")
            output.append(f"\nCritical Zone: Gross Profit Margin decreased above 30%\n{'\n'.join(critical_flags)}")

        # Flag years with persistently negative gross profit margins
        negative_margin_years = data.loc[data['gross_profit_margin'] < 0, 'calendarYear'].tolist()
        if negative_margin_years:
            output.append("\n!!! Persistently Negative Gross Profit Margins\n")
            output.append("The following years had negative gross profit margins, indicating a loss on sales before other expenses:\n")
            output.append("   " + ", ".join([f"FY {year}" for year in negative_margin_years]))

        return '\n'.join(output) if output else None

    ############################ RF6 ############################

    def analyze_inventory_turnover(self, data, caution_threshold=-0.05, red_flag_threshold=-0.10, critical_threshold=-0.20):
        
        # Ensure necessary columns are present
        if 'inventory' not in data.columns or 'costOfRevenue' not in data.columns:
            return "Inventory Turnover analysis requires 'inventory' and 'costOfRevenue' columns."

        # Calculate Inventory Turnover Ratio
        data['inventory_turnover'] = data['costOfRevenue'] / data['inventory'].replace(0, np.nan)

        # Calculate percentage change in Inventory Turnover Ratio
        turnover_pct_change = data['inventory_turnover'].pct_change()

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
            output.append("!!! Increasing Inventory Levels Relative to Sales\n")
            output.append("Indicates potential overstocking or declining demand for products, which can lead to obsolescence.")
            output.append("It can tie up capital that could be used for growth or other investments, posing risks to cash flow and profitability.")

        # Caution zone output
        if caution_years:
            caution_flags = []
            for year, change in zip(caution_years, caution_changes):
                inventory_turnover = data.loc[data['calendarYear'] == year, 'inventory_turnover'].values[0]
                caution_flags.append(f"FY {year}: Inventory Turnover = {inventory_turnover:.2f} (↓ {self.format_percent(abs(change) * 100)}%)")
            output.append(f"\nCaution Zone: Inventory Turnover decreased between 5%-10%\n{'\n'.join(caution_flags)}")

        # Red flag zone output
        if red_flag_years:
            red_flags = []
            for year, change in zip(red_flag_years, red_flag_changes):
                inventory_turnover = data.loc[data['calendarYear'] == year, 'inventory_turnover'].values[0]
                red_flags.append(f"FY {year}: Inventory Turnover = {inventory_turnover:.2f} (↓ {self.format_percent(abs(change) * 100)}%)")
            output.append(f"\nRed Flag: Inventory Turnover decreased above 10%\n{'\n'.join(red_flags)}")

        # Critical zone output
        if critical_years:
            critical_flags = []
            for year, change in zip(critical_years, critical_changes):
                inventory_turnover = data.loc[data['calendarYear'] == year, 'inventory_turnover'].values[0]
                critical_flags.append(f"FY {year}: Inventory Turnover = {inventory_turnover:.2f} (↓ {self.format_percent(abs(change) * 100)}%)")
            output.append(f"\nCritical Zone: Inventory Turnover decreased above 20%\n{'\n'.join(critical_flags)}")

        return '\n'.join(output) if output else None

    ############################ RF7 ############################

    def analyze_goodwill_increase(self, data, caution_threshold=0.10, red_flag_threshold=0.20):
        
        # Ensure necessary columns are present
        if 'goodwill' not in data.columns:
            return "Goodwill analysis requires 'goodwill' column."
        
        # Calculate year-over-year percentage change in Goodwill
        goodwill_pct_change = data['goodwill'].replace(0, np.nan).pct_change()

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
                goodwill = data.loc[data['calendarYear'] == year, 'goodwill'].values[0]
                caution_flags.append(f"FY {year}: Goodwill = {self.format_number(goodwill)} (↑ {self.format_percent(change * 100)}%)")
            output.append(f"\n\nCaution Zone: Goodwill increased between 10%-20%\n{'\n'.join(caution_flags)}")

        # Red flag zone output
        if red_flag_years:
            red_flags = []
            for year, change in zip(red_flag_years, red_flag_changes):
                goodwill = data.loc[data['calendarYear'] == year, 'goodwill'].values[0]
                red_flags.append(f"FY {year}: Goodwill = {self.format_number(goodwill)} (↑ {self.format_percent(change * 100)}%)")
            output.append(f"\n\nRed Flag: Goodwill increased above 20%\n{'\n'.join(red_flags)}")

        # If there are caution or red flags, add the warning text
        if output:
            warning_text = (
                "!!! Large Increases in Goodwill or Intangible Assets\n\n"
                "Risk of overpaying for acquisitions, leading to future impairment charges if expected synergies or performance do not materialize.\n"
                "This can negatively impact future earnings and may suggest aggressive growth strategies without adequate due diligence."
            )
            
            return f"{warning_text}{''.join(output)}"
        return None

    ############################ RF8 ############################

    def analyze_interest_coverage(self, data, caution_threshold=2.5, red_flag_threshold=1.5, critical_threshold=1.0):
        
        # Ensure necessary columns are present
        if 'operatingIncome' not in data.columns or 'interestExpense' not in data.columns:
            return "Interest Coverage analysis requires 'operatingIncome' and 'interestExpense' columns."

        # Calculate Interest Coverage Ratio
        data['Interest Coverage'] = data['operatingIncome'] / data['interestExpense'].replace(0, np.nan)

        # Initialize output
        output = []

        # Function to generate report for a specific zone
        def generate_zone_report(zone_name, condition, threshold_range=None):
            flags = []
            for i, row in data[condition].iterrows():
                year = row['calendarYear']
                coverage = row['Interest Coverage']

                # Calculate percent change and direction from prior year
                if i > 0:
                    prev_coverage = data.iloc[i - 1]['Interest Coverage']
                    if not pd.isnull(prev_coverage):
                        change = (coverage - prev_coverage) / abs(prev_coverage) * 100
                        direction = "↓" if change < 0 else "↑"
                        flags.append(f"FY {year}: Interest Coverage = {coverage:.2f} ({direction} {self.format_percent(abs(change))}%)")
                        continue

                # For the first year or when no valid previous value exists
                flags.append(f"FY {year}: Interest Coverage = {coverage:.2f}")

            if flags:
                range_text = f" {threshold_range}" if threshold_range else ""
                output.append(f"\n\n{zone_name}{range_text}\n" + "\n".join(flags))

        # Generate reports for each zone
        generate_zone_report(
            "Caution Zone:",
            (data['Interest Coverage'] > red_flag_threshold) & (data['Interest Coverage'] <= caution_threshold),
            f"Coverage between {red_flag_threshold} and {caution_threshold}",
        )
        generate_zone_report(
            "Red Flag:",
            (data['Interest Coverage'] > critical_threshold) & (data['Interest Coverage'] <= red_flag_threshold),
            f"Coverage between {critical_threshold} and {red_flag_threshold}",
        )
        generate_zone_report(
            "Critical Zone:",
            (data['Interest Coverage'] > 0) & (data['Interest Coverage'] <= critical_threshold),
            f"Coverage below {critical_threshold}",
        )
        generate_zone_report(
            "Negative Interest Coverage:",
            data['Interest Coverage'] < 0,
            "Operating loss",
        )

        # If there are caution or red flags, add the warning text
        if output:
            warning_text = (
                "!!! Declining Interest Coverage Ratio:\n\n"
                "Indicates the company's ability to meet interest obligations from operating income.\n"
                "Persistent issues may indicate financial distress and risk of default."
            )
            
            return f"{warning_text}{''.join(output)}"
        return None

    ############################ RF9 ############################

    def analyze_increasing_dso(self, data, bad_dso_threshold=45):
        
        # Ensure necessary columns are present
        if 'netReceivables' not in data.columns or 'revenue' not in data.columns:
            return "Net Receivables and Revenue analysis requires 'netReceivables' and 'revenue' columns."

        # Calculate DSO
        data['DSO'] = (data['netReceivables'] / data['revenue'].replace(0, np.nan)) * 365

        # Check if DSO is already bad
        bad_dso = data['DSO'] > bad_dso_threshold

        # Calculate year-over-year percentage change in DSO
        dso_pct_change = data['DSO'].pct_change() * 100

        # Filter for years where DSO is bad
        caution_zone = dso_pct_change[(dso_pct_change > 5) & (dso_pct_change <= 10) & bad_dso]
        red_flag_zone = dso_pct_change[(dso_pct_change > 10) & bad_dso]

        # Prepare output
        output = []

        # Caution Zone
        if not caution_zone.empty:
            output.append("\nCaution Zone: DSO increased between 5%-10%")
            for idx in caution_zone.index:
                year = data['calendarYear'].iloc[idx]
                change = caution_zone[idx]
                dso_value = data['DSO'].iloc[idx]
                output.append(f"FY {year}: DSO = {dso_value:.2f} (↑ {self.format_percent(change)}%)")

        # \n   Red Flag Zone
        if not red_flag_zone.empty:
            output.append("\nRed Flag: DSO increased above 10%")
            for idx in red_flag_zone.index:
                year = data['calendarYear'].iloc[idx]
                change = red_flag_zone[idx]
                dso_value = data['DSO'].iloc[idx]
                output.append(f"FY {year}: DSO = {dso_value:.2f} (↑ {self.format_percent(change)}%)")

        # Check for output presence
        if output:
            return (
                "!!! Increasing Days Sales Outstanding\n\n"
                "Delayed cash inflows, affecting liquidity.\n"
                "An increasing DSO suggests the company is taking longer to collect payments, which may be due to customer financial strain\n" 
                "or ineffective collection processes, potentially leading to cash shortages.\n" +
                "\n".join(output)
            )
        else:
            return None

    ############################ RF10 ############################

    def analyze_negative_free_cash_flow(self, data):
        
        # Ensure necessary columns are present
        if 'freeCashFlow' not in data.columns:
            return "Free Cash Flow analysis requires 'freeCashFlow' column."

        # Check for negative Free Cash Flow
        negative_fcf = data[data['freeCashFlow'] < 0]

        # Prepare output
        output = []

        if not negative_fcf.empty:
            for year, fcf in zip(negative_fcf['calendarYear'], negative_fcf['freeCashFlow']):
                output.append(f"FY {year}: Free Cash Flow = {self.format_number(fcf)}")

        # Check for output presence
        if output:
            return (
                "!!! Negative Free Cash Flow\n\n"
                "Insufficient internal funds to support operations and growth, potentially requiring external financing.\n"
                "Persistent negative free cash flow can indicate unsustainable business models or overinvestment without adequate returns, increasing financial risk.\n\n" +
                "\n".join(output)
            )
        else:
            return None

    ############################ RF11 ############################

    def analyze_high_dividend_payout_poor_cash_flow(self, data, payout_threshold=0.75):

        # Ensure necessary columns are present
        if not all(col in data.columns for col in ['calendarYear', 'dividendsPaid', 'netIncome', 'freeCashFlow']):
            return "Dividend Payout and Free Cash Flow analysis requires 'dividendsPaid', 'netIncome', 'freeCashFlow' columns."

        # Calculate Dividend Payout Ratio
        data['payout_ratio'] = data['dividendsPaid'].abs() / data['netIncome'].replace(0, np.nan).abs()

        # Calculate the percentage change in payout ratio
        data['payout_ratio_pct_change'] = data['payout_ratio'].pct_change() * 100

        # Filter for companies with payout ratio > 75% and free cash flow < absolute dividends paid
        high_payout_poor_cash_flow = data[
            (data['payout_ratio'] > payout_threshold) &
            (data['freeCashFlow'] < data['dividendsPaid'].abs())
        ]

        # Prepare output
        if not high_payout_poor_cash_flow.empty:
            output = [
                "!!! High Dividend Payout with Poor Free Cash Flow\n",
                "Unsustainable dividend policy, possibly leading to increased debt or depletion of cash reserves.",
                "This situation may indicate management's attempt to maintain investor confidence at the expense of long-term financial stability.\n"
            ]
            for idx, row in high_payout_poor_cash_flow.iterrows():
                if idx == 0:  # Skip percentage change for the first row
                    output.append(
                        f"FY {int(row['calendarYear'])}: "
                        f"Payout Ratio = {row['payout_ratio']:.2f}, "
                        f"Free Cash Flow = {self.format_number(row['freeCashFlow'])}, "
                        f"Dividends Paid = {self.format_number(abs(row['dividendsPaid']))}"
                    )
                else:  # Include percentage change for subsequent rows
                    pct_change = row['payout_ratio_pct_change']
                    change_symbol = "↑" if pct_change > 0 else "↓"
                    pct_change_str = f"({change_symbol} {self.format_percent(abs(pct_change))}%)"
                    output.append(
                        f"FY {int(row['calendarYear'])}: "
                        f"Payout Ratio = {row['payout_ratio']:.2f} {pct_change_str}, "
                        f"Free Cash Flow = {self.format_number(row['freeCashFlow'])}, "
                        f"Dividends Paid = {self.format_number(abs(row['dividendsPaid']))}"
                    )
            return "\n".join(output)
        else:
            return None

    ############################ RF12 ############################

    def analyze_large_equity_issuances(self, data, issuance_threshold = 0.1):
        
        # Ensure necessary columns are present
        if 'weightedAverageShsOut' not in data.columns:
            return "Equity Issuances analysis requires 'weightedAverageShsOut' column."

        # Calculate year-over-year change in shares outstanding
        data['shares_change'] = data['weightedAverageShsOut'].replace(0, np.nan).pct_change()

        # Filter for significant increases in shares outstanding (e.g., more than 10% increase)
        equity_issuances = data[data['shares_change'] > issuance_threshold]

        # Prepare output
        output = []
        
        if not equity_issuances.empty:
            for year, change, shares in zip(equity_issuances['calendarYear'], equity_issuances['shares_change'], equity_issuances['weightedAverageShsOut']):
                output.append(f"FY {year}: Shares Outstanding = {self.format_number(shares)} (↑ {self.format_percent(change * 100)}%)")

        # Check if any red flags are found
        if output:
            return (
                "!!! Large Equity Issuances\n\n"
                "Dilution of existing shareholders' equity and potential signal of cash flow problems.\n"
                "Reliance on issuing new shares may indicate that the company cannot generate sufficient internal funds.\n"
                "This may undermine investor confidence and negatively affect earnings per share (EPS).\n\n" +
                "\n".join(output)
            )
        else:
            return None
        
    ############################ RF13 ############################

    def analyze_short_term_debt(self, data, caution_threshold=0.15, red_flag_threshold=0.30):
        
        # Ensure necessary columns are present
        if 'shortTermDebt' not in data.columns:
            return "Short-Term Debt analysis requires 'shortTermDebt' column."

        # Calculate year-over-year percentage change in short-term debt
        short_term_debt_pct_change = data['shortTermDebt'].replace(0, np.nan).pct_change()

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
            "!!! Unusual Increase in Short-Term Debt\n\n"
            "Potential liquidity crunch, as reliance on short-term financing may indicate cash flow issues.\n"
            "Short-term debt often carries higher rollover risk and may reflect difficulties in securing long-term financing, raising concerns about financial stability.\n"
        )
        
        # Caution zone output
        if caution_years:
            caution_flags = []
            for year, change in zip(caution_years, caution_changes):
                shortTermDebt = data.loc[data['calendarYear'] == year, 'shortTermDebt'].values[0]
                caution_flags.append(f"FY {year}: Short-Term Debt = {self.format_number(shortTermDebt)} (↑ {self.format_percent(change * 100)}%)")
            output.append(f"\nCaution Zone: Short-Term Debt increased between 15%-30%\n{'\n'.join(caution_flags)}")

        # Red flag zone output
        if red_flag_years:
            red_flags = []
            for year, change in zip(red_flag_years, red_flag_changes):
                shortTermDebt = data.loc[data['calendarYear'] == year, 'shortTermDebt'].values[0]
                red_flags.append(f"FY {year}: Short-Term Debt = {self.format_number(shortTermDebt)} (↑ {self.format_percent(change * 100)}%)")
            output.append(f"\nRed Flag: Short-Term Debt increased above 30%\n{'\n'.join(red_flags)}")

        # Combine warning text with output
        if output:
            return f"{warning_text}{'\n'.join(output)}"
        
        return None
