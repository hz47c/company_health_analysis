import pandas as pd
import numpy as np

def analyze_red_flags(data):

    results = []
    
    # List of analysis functions
    analysis_functions = [
        analyze_declining_revenue_increasing_income,
        analyze_debt_to_equity_ratio,
        analyze_cash_flow_vs_net_income,
        analyze_accounts_receivable_vs_sales,
        analyze_gross_profit_margin,
        analyze_inventory_turnover,
        analyze_goodwill_increase,
        analyze_interest_coverage,
        analyze_increasing_dso,
        analyze_negative_free_cash_flow,
        analyze_high_dividend_payout_poor_cash_flow,
        analyze_frequent_equity_issuances,
        analyze_short_term_debt
    ]

    # Loop through analysis functions
    for function in analysis_functions:
        result = function(data)
        if result:
            results.append(result)

    return "\n\n".join(results)  # Return results separated by a line

################################################################################################## RF1 ##################################################################################################

def analyze_declining_revenue_increasing_income(data):
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
            red_flags.append(f"FY {year}: Revenue ↓ {abs(rev_change)*100:.2f}%, Net Income ↑ {inc_change*100:.2f}%")

        # Format the output
        details = "\n".join(red_flags)
        return (
            "Declining Revenue with Increasing Net Income\n"
            "— Possible reliance on non-operational income (e.g., asset sales) or aggressive cost-cutting measures that may not be sustainable.\n"
            "— It may mask underlying issues in the core business operations, indicating potential future declines in profitability once temporary measures fade.\n"
            f"{details}"
        )
    return None  # Return None if no red flag

################################################################################################## RF2 ##################################################################################################

def analyze_debt_to_equity_ratio(data):
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
            red_flags.append(f"FY {year}: Debt-to-Equity Ratio = {ratio_value:.2f} (↑ {change*100:.2f}%)")

        # Format the output
        details = "\n".join(red_flags)
        return (
            "High or Increasing Debt Levels Relative to Equity\n"
            "— Heightened financial risk due to increased leverage.\n"
            "— The company may be over-reliant on debt financing, making it vulnerable to interest rate hikes and economic downturns.\n"
            "— This can limit future borrowing capacity and increase default risk.\n"
            f"{details}"
        )
    return None  # Return None if no red flag

################################################################################################## RF3 ##################################################################################################

def analyze_cash_flow_vs_net_income(data):
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
            red_flags.append(f"FY {year}: Net Income ↑ {inc_change*100:.2f}%, Cash Flow ↓ {abs(cash_change)*100:.2f}%")

        # Format the output
        details = "\n".join(red_flags)
        return (
            "Decreasing Cash Flow from Operations with Rising Net Income\n"
            "— Potential earnings quality issues, suggesting that reported net income isn't translating into actual cash.\n"
            "— This discrepancy could be due to non-cash revenue recognition or changes in working capital, raising concerns about the sustainability of earnings.\n"
            f"{details}"
        )
    return None  # Return None if no red flag

################################################################################################## RF4 ##################################################################################################

def analyze_accounts_receivable_vs_sales(data, caution_threshold=0.10, red_flag_threshold=0.20, critical_threshold=0.30):
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
        output.append("Growing Accounts Receivable as a Percentage of Sales")
        output.append("— Indicates worsening collection issues or overly loose credit terms, potentially leading to cash flow problems.")
        output.append("— Suggests rising bad debt expenses and declining credit quality of customers.")

    # Caution zone output
    if caution_years:
        caution_flags = []
        for year, ratio, change in zip(caution_years, caution_ratios, caution_changes):
            if change != 0:  # Skip 0% change
                arrow = "↑" if change > 0 else "↓"
                caution_flags.append(f"FY {year}: Accounts Receivable to Sales = {ratio*100:.2f}% ({arrow} {abs(change)*100:.2f}%)")
            else:
                caution_flags.append(f"FY {year}: Accounts Receivable to Sales = {ratio*100:.2f}%")  # Display only ratio if 0% change
        if caution_flags:
            output.append(f"Caution Zone: Accounts Receivable to Sales between 10%-20%\n{'\n'.join(caution_flags)}")

    # Red flag zone output
    if red_flag_years:
        red_flags = []
        for year, ratio, change in zip(red_flag_years, red_flag_ratios, red_flag_changes):
            if change != 0:  # Skip 0% change
                arrow = "↑" if change > 0 else "↓"
                red_flags.append(f"FY {year}: Accounts Receivable to Sales = {ratio*100:.2f}% ({arrow} {abs(change)*100:.2f}%)")
            else:
                red_flags.append(f"FY {year}: Accounts Receivable to Sales = {ratio*100:.2f}%")  # Display only ratio if 0% change
        if red_flags:
            output.append(f"Red Flag: Accounts Receivable to Sales between 20%-30%\n{'\n'.join(red_flags)}")

    # Critical zone output
    if critical_years:
        critical_flags = []
        for year, ratio, change in zip(critical_years, critical_ratios, critical_changes):
            if change != 0:  # Skip 0% change
                arrow = "↑" if change > 0 else "↓"
                critical_flags.append(f"FY {year}: Accounts Receivable to Sales = {ratio*100:.2f}% ({arrow} {abs(change)*100:.2f}%)")
            else:
                critical_flags.append(f"FY {year}: Accounts Receivable to Sales = {ratio*100:.2f}%")  # Display only ratio if 0% change
        if critical_flags:
            output.append(f"Critical Zone: Accounts Receivable to Sales above 30%\n{'\n'.join(critical_flags)}")

    # Join the output list into a single string
    return '\n'.join(output) if output else None  # Return formatted output or None if no caution or red flags

################################################################################################## RF5 ##################################################################################################

def analyze_gross_profit_margin(data, caution_threshold=-0.10, red_flag_threshold=-0.20, critical_threshold=-0.30):
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
        output.append("Decreasing Gross Profit Margins")
        output.append("— Suggests worsening efficiency or rising costs of goods sold, which can erode profitability.")
        output.append("— It may indicate market pressures or competitive challenges affecting pricing power, requiring a strategic review to address cost management.")

    # Caution zone output
    if caution_years:
        caution_flags = []
        for year, change in zip(caution_years, caution_changes):
            caution_flags.append(f"FY {year}: Gross Profit Margin ↓ {abs(change) * 100:.2f}%")
        output.append(f"Caution Zone: Gross Profit Margin decreased between 10%-20%\n{'\n'.join(caution_flags)}")

    # Red flag zone output
    if red_flag_years:
        red_flags = []
        for year, change in zip(red_flag_years, red_flag_changes):
            red_flags.append(f"FY {year}: Gross Profit Margin ↓ {abs(change) * 100:.2f}%")
        output.append(f"Red Flag: Gross Profit Margin decreased above 20%\n{'\n'.join(red_flags)}")

    # Critical zone output
    if critical_years:
        critical_flags = []
        for year, change in zip(critical_years, critical_changes):
            critical_flags.append(f"FY {year}: Gross Profit Margin ↓ {abs(change) * 100:.2f}%")
        output.append(f"Critical Zone: Gross Profit Margin decreased above 30%\n{'\n'.join(critical_flags)}")

    # Join the output list into a single string
    return '\n'.join(output) if output else None  # Return formatted output or None if no caution or red flags

################################################################################################## RF6 ##################################################################################################

def analyze_inventory_turnover(data, caution_threshold=-0.05, red_flag_threshold=-0.10, critical_threshold=-0.20):
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
        output.append("Increasing Inventory Levels Relative to Sales")
        output.append("— Indicates potential overstocking or declining demand for products, which can lead to obsolescence.")
        output.append("— It can tie up capital that could be used for growth or other investments, posing risks to cash flow and profitability.")

    # Caution zone output
    if caution_years:
        caution_flags = []
        for year, change in zip(caution_years, caution_changes):
            caution_flags.append(f"FY {year}: Inventory Turnover ↓ {abs(change) * 100:.2f}%")
        output.append(f"Caution Zone: Inventory Turnover decreased between 5%-10%\n{'\n'.join(caution_flags)}")

    # Red flag zone output
    if red_flag_years:
        red_flags = []
        for year, change in zip(red_flag_years, red_flag_changes):
            red_flags.append(f"FY {year}: Inventory Turnover ↓ {abs(change) * 100:.2f}%")
        output.append(f"Red Flag: Inventory Turnover decreased above 10%\n{'\n'.join(red_flags)}")

    # Critical zone output
    if critical_years:
        critical_flags = []
        for year, change in zip(critical_years, critical_changes):
            critical_flags.append(f"FY {year}: Inventory Turnover ↓ {abs(change) * 100:.2f}%")
        output.append(f"Critical Zone: Inventory Turnover decreased above 20%\n{'\n'.join(critical_flags)}")

    # Join the output list into a single string
    return '\n'.join(output) if output else None  # Return formatted output or None if no issues

################################################################################################## RF7 ##################################################################################################

def analyze_goodwill_increase(data, caution_threshold=0.10, red_flag_threshold=0.20):

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
            caution_flags.append(f"FY {year}: Goodwill ↑ {change * 100:.2f}%")
        output.append(f"Caution Zone: Goodwill increased between 10%-20%\n{'\n'.join(caution_flags)}")

    # Red flag zone output
    if red_flag_years:
        red_flags = []
        for year, change in zip(red_flag_years, red_flag_changes):
            red_flags.append(f"FY {year}: Goodwill ↑ {change * 100:.2f}%")
        output.append(f"Red Flag: Goodwill increased above 20%\n{'\n'.join(red_flags)}")

    # If there are caution or red flags, add the warning text
    if output:
        warning_text = (
            "Large Increases in Goodwill or Intangible Assets\n"
            "— Risk of overpaying for acquisitions, leading to future impairment charges if expected synergies or performance do not materialize\n"
            "— This can negatively impact future earnings and may suggest aggressive growth strategies without adequate due diligence\n"
        )
        
        return f"{warning_text}{''.join(output)}"
    return None  # Return None if no red flag

################################################################################################## RF8 ##################################################################################################

def analyze_interest_coverage(data, caution_threshold=2.5, red_flag_threshold=1.5, critical_threshold=1.0):
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
        output.append("Declining Interest Coverage Ratio")
        output.append("— Signals growing difficulties in meeting interest obligations, raising default risk.")
        output.append("— A declining ratio can impact credit ratings and future borrowing costs, potentially limiting financial flexibility.")

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
                    caution_flags.append(f"FY {year}: Interest Coverage = {caution_values[i]:.2f} ({direction} {abs(change):.2f}%)")
                else:
                    caution_flags.append(f"FY {year}: Interest Coverage = {caution_values[i]:.2f}")
            else:
                caution_flags.append(f"FY {year}: Interest Coverage = {caution_values[i]:.2f}")
        
        output.append(f"Caution Zone: Interest Coverage between {red_flag_threshold}-{caution_threshold}\n{'\n'.join(caution_flags)}")

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
                    red_flags.append(f"FY {year}: Interest Coverage = {red_flag_values[i]:.2f} ({direction} {abs(change):.2f}%)")
                else:
                    red_flags.append(f"FY {year}: Interest Coverage = {red_flag_values[i]:.2f}")
            else:
                red_flags.append(f"FY {year}: Interest Coverage = {red_flag_values[i]:.2f}")
        
        output.append(f"Red Flag: Interest Coverage between {critical_threshold}-{red_flag_threshold}\n{'\n'.join(red_flags)}")

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
                    critical_flags.append(f"FY {year}: Interest Coverage = {critical_values[i]:.2f} ({direction} {abs(change):.2f}%)")
                else:
                    critical_flags.append(f"FY {year}: Interest Coverage = {critical_values[i]:.2f}")
            else:
                critical_flags.append(f"FY {year}: Interest Coverage = {critical_values[i]:.2f}")
        
        output.append(f"Critical Zone: Interest Coverage below {critical_threshold}\n{'\n'.join(critical_flags)}")

    # Join the output list into a single string
    return '\n'.join(output) if output else None  # Return formatted output or None if no caution or red flags

################################################################################################## RF9 ##################################################################################################

def analyze_increasing_dso(data, bad_dso_threshold=60):
    # Calculate DSO
    data['DSO'] = (data['netReceivables'] / data['Revenue']) * 365

    # Check if DSO is already bad
    bad_dso = data['DSO'] > bad_dso_threshold

    # Calculate year-over-year percentage change in DSO
    dso_pct_change = data['DSO'].pct_change().fillna(0) * 100

    # Filter for years where DSO is bad
    caution_zone = dso_pct_change[(dso_pct_change > 5) & (dso_pct_change <= 10) & bad_dso]
    red_flag_zone = dso_pct_change[(dso_pct_change > 10) & bad_dso]

    # Prepare output
    output = []

    # Caution Zone
    if not caution_zone.empty:
        output.append("Caution Zone: DSO increased between 5%-10%")
        for idx in caution_zone.index:
            year = data['calendarYear'].iloc[idx]
            change = caution_zone[idx]
            dso_value = data['DSO'].iloc[idx]
            output.append(f"FY {year}: DSO = {dso_value:.2f} (↑ {change:.2f}%)")

    # Red Flag Zone
    if not red_flag_zone.empty:
        output.append("Red Flag: DSO increased above 10%")
        for idx in red_flag_zone.index:
            year = data['calendarYear'].iloc[idx]
            change = red_flag_zone[idx]
            dso_value = data['DSO'].iloc[idx]
            output.append(f"FY {year}: DSO = {dso_value:.2f} (↑ {change:.2f}%)")

    # Check for output presence
    if output:
        return (
            "Increasing Days Sales Outstanding\n"
            "— Delayed cash inflows, affecting liquidity\n"
            "— An increasing DSO suggests the company is taking longer to collect payments, which may be due to customer financial strain or ineffective collection processes, potentially leading to cash shortages\n" +
            "\n".join(output)
        )
    else:
        return None  # Return None if no red flag

################################################################################################## RF10 ##################################################################################################

def analyze_negative_free_cash_flow(data):

    # Check for negative Free Cash Flow
    negative_fcf = data[data['freeCashFlow'] < 0]

    # Prepare output
    output = []

    if not negative_fcf.empty:
        for year, fcf in zip(negative_fcf['calendarYear'], negative_fcf['freeCashFlow']):
            output.append(f"FY {year}: Free Cash Flow = {fcf:.0f}")

    # Check for output presence
    if output:
        return (
            "Negative Free Cash Flow\n"
            "— Insufficient internal funds to support operations and growth, potentially requiring external financing\n"
            "— Persistent negative free cash flow can indicate unsustainable business models or overinvestment without adequate returns, increasing financial risk\n" +
            "\n".join(output).replace('-', '-$')
        )
    else:
        return None  # Return None if no red flag

################################################################################################## RF11 ##################################################################################################

def analyze_high_dividend_payout_poor_cash_flow(data):
    output = []
    
    # Calculate Dividend Payout Ratio
    data['payout_ratio'] = data['dividendsPaid'] / data['Net Income']

    # Calculate the percentage change in payout ratio
    payout_ratio_pct_change = data['payout_ratio'].pct_change().fillna(0)

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
                f"FY {int(row['calendarYear'])}: Payout Ratio = {row['payout_ratio']:.2f} ({change_symbol} {abs(pct_change):.2f}%), "
                f"Operating Cash Flow = {int(row['operatingCashFlow'])}, Dividends Paid = {int(row['dividendsPaid'])}"
            )

    # Check for output presence
    if output:
        return (
            "High Dividend Payout with Poor Cash Flow\n"
            "— Unsustainable dividend policy, possibly leading to increased debt or depletion of cash reserves.\n"
            "— This situation may indicate management's attempt to maintain investor confidence at the expense of long-term financial stability.\n" +
            "\n".join(output)
        )
    else:
        return None  # Return None if no red flag

################################################################################################## RF12 ##################################################################################################

def analyze_frequent_equity_issuances(data):

    # Calculate year-over-year change in shares outstanding
    data['shares_change'] = data['weightedAverageShsOut'].pct_change()

    # Filter for significant increases in shares outstanding (e.g., more than 5% increase)
    equity_issuances = data[data['shares_change'] > 0.05]

    # Prepare output
    output = []
    
    if not equity_issuances.empty:
        for year, change, shares in zip(equity_issuances['calendarYear'], equity_issuances['shares_change'], equity_issuances['weightedAverageShsOut']):
            output.append(f"FY {year}: Shares Outstanding ↑ {change:.2%}")

    # Check if any red flags are found
    if output:
        return (
            "Frequent Equity Issuances\n"
            "— Dilution of existing shareholders' equity and potential signal of cash flow problems.\n"
            "— Reliance on issuing new shares may indicate that the company cannot generate sufficient internal funds.\n"
            "— This may undermine investor confidence and negatively affect earnings per share (EPS).\n" +
            "\n".join(output)
        )
    else:
        return None  # Return None if no red flags are found
    
################################################################################################## RF13 ##################################################################################################

def analyze_short_term_debt(data, caution_threshold=0.10, red_flag_threshold=0.15):
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
        "Unusual Increase in Short-Term Debt\n"
        "— Potential liquidity crunch, as reliance on short-term financing may indicate cash flow issues.\n"
        "— Short-term debt often carries higher rollover risk and may reflect difficulties in securing long-term financing, raising concerns about financial stability.\n"
    )
    
    # Caution zone output
    if caution_years:
        caution_flags = []
        for year, change in zip(caution_years, caution_changes):
            caution_flags.append(f"FY {year}: Short-Term Debt ↑ {change * 100:.2f}%")
        output.append(f"Caution Zone: Short-Term Debt increased between 10%-15%\n{'\n'.join(caution_flags)}")

    # Red flag zone output
    if red_flag_years:
        red_flags = []
        for year, change in zip(red_flag_years, red_flag_changes):
            red_flags.append(f"FY {year}: Short-Term Debt ↑ {change * 100:.2f}%")
        output.append(f"Red Flag: Short-Term Debt increased above 15%\n{'\n'.join(red_flags)}")

    # Combine warning text with output
    if output:
        return f"{warning_text}{'\n'.join(output)}"
    
    return None  # Return None if no red flag is found

################################################################################################## Dataframe ##################################################################################################

# Sample dataset to trigger all functions (replace with actual data):
data = pd.DataFrame({
    'calendarYear': [2020, 2021, 2022, 2023, 2024],
    
    # Balance Sheet
    'totalCurrentAssets': [500, 550, 580, np.nan, 600],  # Current assets showing an overall increase
    'cashAndCashEquivalents': [100, 150, 120, 130, np.nan],  # Increasing cash levels
    'netReceivables': [200, 220, 230, 240, 250],  # Increasing receivables
    'inventory': [150, 160, 170, 180, 190],  # Gradual increases in inventory levels
    'goodwill': [100, 120, np.nan, 140, 160],  # Goodwill values showing potential acquisition activity
    'intangibleAssets': [50, 60, 65, np.nan, 70],  # Increasing intangible assets reflecting investments in intellectual property
    'totalAssets': [1000, 1100, 1200, 1250, 1300],  # Steady increase in total assets
    'totalCurrentLiabilities': [300, 320, 340, 360, 380],  # Current liabilities increasing slightly
    'accountPayables': [150, 160, 170, np.nan, 180],  # Increasing accounts payable
    'shortTermDebt': [50, 55, 60, 65, 70],  # Short-term debt levels increasing gradually
    'totalDebt': [500, 600, 900, 1200, 1500],  # Total debt increasing, which may require monitoring
    'deferredRevenue': [30, 35, 40, 45, np.nan],  # Increasing deferred revenue reflecting future sales commitments
    'totalStockholdersEquity': [1000, 1100, 950, 800, 700], # Decreasing equity indicating weak retained earnings

    # Income Statement
    'Revenue': [1000, 1100, 1200, 1150, 1050],  # 2023 and 2024 show declining revenue, indicating potential sales challenges
    'Cost of Revenue': [600, 650, 700, 680, 720],  # Cost of revenue increasing, suggesting higher input costs
    'Gross Profit': [400, 450, 500, 470, 330],  # Fluctuations in gross profit
    'Operating Expenses': [200, 220, 250, 240, 260],  # Operating expenses increasing
    'EBIT': [200, 230, 250, 230, 70],  # Earnings Before Interest and Taxes showing variability
    'Interest Expense': [50, 55, 60, 65, 70],  # Increasing interest expense due to higher debt levels
    'Net Income': [300, 500, 600, 500, 800],  # Increasing net income
    'weightedAverageShsOut': [5000000, 5250000, 6000000, 7000000, 7000000],  # Shares outstanding increasing slightly

    # Cash Flow Statement
    'operatingCashFlow': [150, 280, 200, 350, 300],  # Cash flow from operations increasing
    'capitalExpenditure': [70, 80, 90, 85, 100],  # Increasing capital expenditures indicating investment in growth
    'freeCashFlow': [180, 190, 210, -205, np.nan],  # Free cash flow increasing
    'dividendsPaid': [200, 300, 250, 400, 450]  # Increasing dividends
})

# Run the analysis
results = analyze_red_flags(data)
print(results)
