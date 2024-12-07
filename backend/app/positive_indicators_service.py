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
            
            'Revenue': [],
            'Cost of Revenue': [],
            'Gross Profit': [],
            'Operating Expenses': [],
            'EBIT': [],
            'Interest Expense': [],
            'Net Income': [],
            'weightedAverageShsOut': [],
            
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

        # Create DataFrame from the dictionary
        df = pd.DataFrame(data)
        return df

    def analyze_positive_indicators(self, ticker):
        data = self.get_financial_data_as_dataframe(ticker)
        results = []

        # List of analysis functions to execute
        analysis_functions = [
            self.analyze_revenue_growth,
            self.analyze_increasing_cash_flow,
            self.analyze_improving_gross_margin,
            self.analyze_increasing_dividends,
            self.analyze_decreasing_debt,
            self.analyze_high_interest_coverage,
            self.analyze_strong_return_on_equity,
            self.analyze_improved_inventory_turnover,
        ]

        for function in analysis_functions:
            result = function(data)
            if result:
                results.append(result)

        return "\n\n".join(results) if results else "No positive indicators identified."

    # Individual positive indicator analysis functions

    def analyze_revenue_growth(self, data):
        revenue_growth = data['Revenue'].pct_change().fillna(0) > 0
        growth_years = data.loc[revenue_growth, 'calendarYear'].tolist()
        if growth_years:
            return f"Revenue Growth in years: {', '.join(map(str, growth_years))}"
        return None

    def analyze_increasing_cash_flow(self, data):
        cash_flow_growth = data['operatingCashFlow'].pct_change().fillna(0) > 0
        growth_years = data.loc[cash_flow_growth, 'calendarYear'].tolist()
        if growth_years:
            return f"Increasing Operating Cash Flow in years: {', '.join(map(str, growth_years))}"
        return None

    def analyze_improving_gross_margin(self, data):
        gross_margin = data['Gross Profit'] / data['Revenue']
        margin_increase = gross_margin.pct_change().fillna(0) > 0
        positive_years = data.loc[margin_increase, 'calendarYear'].tolist()
        if positive_years:
            return f"Improving Gross Margin in years: {', '.join(map(str, positive_years))}"
        return None

    def analyze_increasing_dividends(self, data):
        dividend_growth = data['dividendsPaid'].pct_change().fillna(0) > 0
        growth_years = data.loc[dividend_growth, 'calendarYear'].tolist()
        if growth_years:
            return f"Increasing Dividends Paid in years: {', '.join(map(str, growth_years))}"
        return None

    def analyze_decreasing_debt(self, data):
        debt_decrease = data['totalDebt'].pct_change().fillna(0) < 0
        positive_years = data.loc[debt_decrease, 'calendarYear'].tolist()
        if positive_years:
            return f"Decreasing Total Debt in years: {', '.join(map(str, positive_years))}"
        return None

    def analyze_high_interest_coverage(self, data, threshold=3.0):
        interest_coverage = data['EBIT'] / data['Interest Expense']
        positive_years = data.loc[interest_coverage > threshold, 'calendarYear'].tolist()
        if positive_years:
            return f"High Interest Coverage Ratio in years: {', '.join(map(str, positive_years))}"
        return None

    def analyze_strong_return_on_equity(self, data, threshold=0.15):
        return_on_equity = data['Net Income'] / data['totalStockholdersEquity']
        positive_years = data.loc[return_on_equity > threshold, 'calendarYear'].tolist()
        if positive_years:
            return f"Strong Return on Equity (ROE) in years: {', '.join(map(str, positive_years))}"
        return None

    def analyze_improved_inventory_turnover(self, data):
        inventory_turnover = data['Cost of Revenue'] / data['inventory']
        turnover_increase = inventory_turnover.pct_change().fillna(0) > 0
        positive_years = data.loc[turnover_increase, 'calendarYear'].tolist()
        if positive_years:
            return f"Improving Inventory Turnover in years: {', '.join(map(str, positive_years))}"
        return None
