# app/services/analysis_service.py

import pandas as pd
import numpy as np
from app.models import Company, BalanceSheet, IncomeStatement, CashFlow

class AnalysisService:
    def get_financial_data_as_dataframe(self, ticker):
        # Query the relevant data
        balance_sheets = BalanceSheet.query.filter_by(ticker=ticker).all()
        income_statements = IncomeStatement.query.filter_by(ticker=ticker).all()
        cash_flows = CashFlow.query.filter_by(ticker=ticker).all()

        # Initialize dictionary to store data
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

        # Fill in Balance Sheet Data
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

        # Fill in Income Statement Data
        for record in income_statements:
            data['Revenue'].append(record.revenue or np.nan)
            data['Cost of Revenue'].append(record.cost_of_revenue or np.nan)
            data['Gross Profit'].append(record.gross_profit or np.nan)
            data['Operating Expenses'].append(record.operating_expenses or np.nan)
            data['EBIT'].append(record.operating_income or np.nan)  # EBIT equivalent
            data['Interest Expense'].append(record.interest_expense or np.nan)
            data['Net Income'].append(record.net_income or np.nan)
            data['weightedAverageShsOut'].append(record.weighted_average_shs_out or np.nan)

        # Fill in Cash Flow Statement Data
        for record in cash_flows:
            data['operatingCashFlow'].append(record.operating_cash_flow or np.nan)
            data['capitalExpenditure'].append(record.capital_expenditure or np.nan)
            data['freeCashFlow'].append(record.free_cash_flow or np.nan)
            data['dividendsPaid'].append(record.dividends_paid or np.nan)

        # Create DataFrame from dictionary
        df = pd.DataFrame(data)
        return df
