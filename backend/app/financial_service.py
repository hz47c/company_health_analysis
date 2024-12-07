# app/financial_service.py

import requests
import os
from .db import db
from .models import Company, BalanceSheet, IncomeStatement, CashFlow
from dotenv import load_dotenv

load_dotenv()

class FinancialService:
    def __init__(self):
        self.api_key = os.getenv('FMP_API_KEY')
        self.base_url = 'https://financialmodelingprep.com/api/v3'

    def fetch_balance_sheet(self, ticker):
        return self._get_data(f"/balance-sheet-statement/{ticker}")

    def fetch_company_name(self, ticker):
        response = self._get_data(f"/profile/{ticker}")
        return response[0] if response else {}

    def fetch_income_statement(self, ticker):
        return self._get_data(f"/income-statement/{ticker}")

    def fetch_cash_flow(self, ticker):
        return self._get_data(f"/cash-flow-statement/{ticker}")

    def fetch_all_data(self, ticker):
        # Check if data for this ticker already exists
        existing_company = Company.query.filter_by(ticker=ticker).first()

        if existing_company:
            # Data exists in the database, retrieve it
            balance_sheets = BalanceSheet.query.filter_by(ticker=ticker).all()
            income_statements = IncomeStatement.query.filter_by(ticker=ticker).all()
            cash_flows = CashFlow.query.filter_by(ticker=ticker).all()

            return {
                "companyName": {"companyName": existing_company.name},
                "balanceSheet": [{"totalAssets": bs.total_assets, "totalLiabilities": bs.total_liabilities} for bs in balance_sheets],
                "incomeStatement": [{"revenue": is_.revenue, "netIncome": is_.net_income} for is_ in income_statements],
                "cashFlow": [{"operatingCashFlow": cf.operating_cash_flow} for cf in cash_flows]
            }

        else:
            # Data does not exist, fetch from API and store in database
            balance_sheet_data = self.fetch_balance_sheet(ticker)
            company_data = self.fetch_company_name(ticker)
            income_statement_data = self.fetch_income_statement(ticker)
            cash_flow_data = self.fetch_cash_flow(ticker)

            # Save to database
            self._save_to_db(ticker, company_data, balance_sheet_data, income_statement_data, cash_flow_data)

            return {
                "balanceSheet": balance_sheet_data,
                "companyName": company_data,
                "incomeStatement": income_statement_data,
                "cashFlow": cash_flow_data
            }

    def _get_data(self, endpoint):
        url = f"{self.base_url}{endpoint}?apikey={self.api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return {}

    def _save_to_db(self, ticker, company_data, balance_sheet_data, income_statement_data, cash_flow_data):
        
        # Store company data
        company = Company(
            ticker=ticker,
            name=company_data.get('companyName'),
            address=company_data.get('address'),
            beta=company_data.get('beta'),
            ceo=company_data.get('ceo'),
            changes=company_data.get('changes'),
            cik=company_data.get('cik'),
            city=company_data.get('city'),
            country=company_data.get('country'),
            currency=company_data.get('currency'),
            cusip=company_data.get('cusip'),
            dcf=company_data.get('dcf'),
            dcf_diff=company_data.get('dcfDiff'),
            default_image=company_data.get('defaultImage'),
            description=company_data.get('description'),
            exchange=company_data.get('exchange'),
            exchange_short_name=company_data.get('exchangeShortName'),
            full_time_employees=company_data.get('fullTimeEmployees'),
            image=company_data.get('image'),
            industry=company_data.get('industry'),
            ipo_date=company_data.get('ipoDate'),
            is_actively_trading=company_data.get('isActivelyTrading'),
            is_adr=company_data.get('isAdr'),
            is_etf=company_data.get('isEtf'),
            is_fund=company_data.get('isFund'),
            isin=company_data.get('isin'),
            last_div=company_data.get('lastDiv'),
            market_cap=company_data.get('mktCap'),
            phone=company_data.get('phone'),
            price=company_data.get('price'),
            price_range=company_data.get('range'),
            sector=company_data.get('sector'),
            state=company_data.get('state'),
            vol_avg=company_data.get('volAvg'),
            website=company_data.get('website'),
            zip_code=company_data.get('zip')
        )
        db.session.add(company)
        
        for data in balance_sheet_data:
            balance_sheet = BalanceSheet(
                ticker=ticker,
                accepted_date=data.get('acceptedDate'),
                account_payables=data.get('accountPayables'),
                accumulated_other_comprehensive_income_loss=data.get('accumulatedOtherComprehensiveIncomeLoss'),
                calendar_year=data.get('calendarYear'),
                capital_lease_obligations=data.get('capitalLeaseObligations'),
                cash_and_cash_equivalents=data.get('cashAndCashEquivalents'),
                cash_and_short_term_investments=data.get('cashAndShortTermInvestments'),
                cik=data.get('cik'),
                common_stock=data.get('commonStock'),
                date=data.get('date'),
                deferred_revenue=data.get('deferredRevenue'),
                deferred_revenue_non_current=data.get('deferredRevenueNonCurrent'),
                deferred_tax_liabilities_non_current=data.get('deferredTaxLiabilitiesNonCurrent'),
                filling_date=data.get('fillingDate'),
                final_link=data.get('finalLink'),
                goodwill=data.get('goodwill'),
                goodwill_and_intangible_assets=data.get('goodwillAndIntangibleAssets'),
                intangible_assets=data.get('intangibleAssets'),
                inventory=data.get('inventory'),
                link=data.get('link'),
                long_term_debt=data.get('longTermDebt'),
                long_term_investments=data.get('longTermInvestments'),
                minority_interest=data.get('minorityInterest'),
                net_debt=data.get('netDebt'),
                net_receivables=data.get('netReceivables'),
                other_assets=data.get('otherAssets'),
                other_current_assets=data.get('otherCurrentAssets'),
                other_current_liabilities=data.get('otherCurrentLiabilities'),
                other_liabilities=data.get('otherLiabilities'),
                other_non_current_assets=data.get('otherNonCurrentAssets'),
                other_non_current_liabilities=data.get('otherNonCurrentLiabilities'),
                othertotal_stockholders_equity=data.get('othertotalStockholdersEquity'),
                period=data.get('period'),
                preferred_stock=data.get('preferredStock'),
                property_plant_equipment_net=data.get('propertyPlantEquipmentNet'),
                reported_currency=data.get('reportedCurrency'),
                retained_earnings=data.get('retainedEarnings'),
                short_term_debt=data.get('shortTermDebt'),
                short_term_investments=data.get('shortTermInvestments'),
                tax_assets=data.get('taxAssets'),
                tax_payables=data.get('taxPayables'),
                total_assets=data.get('totalAssets'),
                total_current_assets=data.get('totalCurrentAssets'),
                total_current_liabilities=data.get('totalCurrentLiabilities'),
                total_debt=data.get('totalDebt'),
                total_equity=data.get('totalEquity'),
                total_investments=data.get('totalInvestments'),
                total_liabilities=data.get('totalLiabilities'),
                total_liabilities_and_stockholders_equity=data.get('totalLiabilitiesAndStockholdersEquity'),
                total_liabilities_and_total_equity=data.get('totalLiabilitiesAndTotalEquity'),
                total_non_current_assets=data.get('totalNonCurrentAssets'),
                total_non_current_liabilities=data.get('totalNonCurrentLiabilities'),
                total_stockholders_equity=data.get('totalStockholdersEquity')
            )
            db.session.add(balance_sheet)

        # Store income statement data
        for data in income_statement_data:
            income_statement = IncomeStatement(
                ticker=ticker,
                accepted_date=data.get('acceptedDate'),
                calendar_year=data.get('calendarYear'),
                cik=data.get('cik'),
                cost_and_expenses=data.get('costAndExpenses'),
                cost_of_revenue=data.get('costOfRevenue'),
                date=data.get('date'),
                depreciation_and_amortization=data.get('depreciationAndAmortization'),
                ebitda=data.get('ebitda'),
                ebitda_ratio=data.get('ebitdaratio'),
                eps=data.get('eps'),
                eps_diluted=data.get('epsdiluted'),
                filling_date=data.get('fillingDate'),
                final_link=data.get('finalLink'),
                general_and_administrative_expenses=data.get('generalAndAdministrativeExpenses'),
                gross_profit=data.get('grossProfit'),
                gross_profit_ratio=data.get('grossProfitRatio'),
                income_before_tax=data.get('incomeBeforeTax'),
                income_before_tax_ratio=data.get('incomeBeforeTaxRatio'),
                income_tax_expense=data.get('incomeTaxExpense'),
                interest_expense=data.get('interestExpense'),
                interest_income=data.get('interestIncome'),
                link=data.get('link'),
                net_income=data.get('netIncome'),
                net_income_ratio=data.get('netIncomeRatio'),
                operating_expenses=data.get('operatingExpenses'),
                operating_income=data.get('operatingIncome'),
                operating_income_ratio=data.get('operatingIncomeRatio'),
                other_expenses=data.get('otherExpenses'),
                period=data.get('period'),
                reported_currency=data.get('reportedCurrency'),
                research_and_development_expenses=data.get('researchAndDevelopmentExpenses'),
                revenue=data.get('revenue'),
                selling_and_marketing_expenses=data.get('sellingAndMarketingExpenses'),
                selling_general_and_administrative_expenses=data.get('sellingGeneralAndAdministrativeExpenses'),
                total_other_income_expenses_net=data.get('totalOtherIncomeExpensesNet'),
                weighted_average_shs_out=data.get('weightedAverageShsOut'),
                weighted_average_shs_out_dil=data.get('weightedAverageShsOutDil')
            )
            db.session.add(income_statement)
        
        

        # Store cash flow data
        
        for data in cash_flow_data:
            cash_flow = CashFlow(
                ticker=ticker,
                accepted_date=data.get('acceptedDate'),
                accounts_payables=data.get('accountsPayables'),
                accounts_receivables=data.get('accountsReceivables'),
                acquisitions_net=data.get('acquisitionsNet'),
                calendar_year=data.get('calendarYear'),
                capital_expenditure=data.get('capitalExpenditure'),
                cash_at_beginning_of_period=data.get('cashAtBeginningOfPeriod'),
                cash_at_end_of_period=data.get('cashAtEndOfPeriod'),
                change_in_working_capital=data.get('changeInWorkingCapital'),
                cik=data.get('cik'),
                common_stock_issued=data.get('commonStockIssued'),
                common_stock_repurchased=data.get('commonStockRepurchased'),
                date=data.get('date'),
                debt_repayment=data.get('debtRepayment'),
                deferred_income_tax=data.get('deferredIncomeTax'),
                depreciation_and_amortization=data.get('depreciationAndAmortization'),
                dividends_paid=data.get('dividendsPaid'),
                effect_of_forex_changes_on_cash=data.get('effectOfForexChangesOnCash'),
                filling_date=data.get('fillingDate'),
                final_link=data.get('finalLink'),
                free_cash_flow=data.get('freeCashFlow'),
                inventory=data.get('inventory'),
                investments_in_property_plant_and_equipment=data.get('investmentsInPropertyPlantAndEquipment'),
                link=data.get('link'),
                net_cash_provided_by_operating_activities=data.get('netCashProvidedByOperatingActivities'),
                net_cash_used_for_investing_activities=data.get('netCashUsedForInvestingActivites'),
                net_cash_used_provided_by_financing_activities=data.get('netCashUsedProvidedByFinancingActivities'),
                net_change_in_cash=data.get('netChangeInCash'),
                net_income=data.get('netIncome'),
                operating_cash_flow=data.get('operatingCashFlow'),
                other_financing_activities=data.get('otherFinancingActivites'),
                other_investing_activities=data.get('otherInvestingActivites'),
                other_non_cash_items=data.get('otherNonCashItems'),
                other_working_capital=data.get('otherWorkingCapital'),
                period=data.get('period'),
                purchases_of_investments=data.get('purchasesOfInvestments'),
                reported_currency=data.get('reportedCurrency'),
                sales_maturities_of_investments=data.get('salesMaturitiesOfInvestments'),
                stock_based_compensation=data.get('stockBasedCompensation')
            )
            db.session.add(cash_flow)
        # Commit all changes to the database
        db.session.commit()
    #@staticmethod
    def get_company_data(ticker):
       company = Company.query.filter_by(ticker=ticker).first()
       
       if not company:
        return None
       return {
        "ticker": company.ticker,
        "companyName": company.name,
        "address": company.address,
        "country": company.country,
        "currency": company.currency,
        "description":company.description
    }
    
# @staticmethod
    def get_cash_flow_data(ticker):
        cash_flow = CashFlow.query.filter_by(ticker=ticker).all()
        if not cash_flow:
            return None
        return [
            {
                "date": record.date,
                # Calendar Year
                "calendarYear": record.calendar_year,

                # Operating Activities (Group 1)
              "netIncome": record.net_income,
              "depreciationAndAmortization": record.depreciation_and_amortization,
             "deferredIncomeTax": record.deferred_income_tax,
             "stockBasedCompensation": record.stock_based_compensation,
             "changeInWorkingCapital": record.change_in_working_capital,
             "accountsReceivables": record.accounts_receivables,
             "inventory": record.inventory,
             "accountsPayables": record.accounts_payables,
             "otherWorkingCapital": record.other_working_capital,
             "otherNonCashItems": record.other_non_cash_items,
             "netCashProvidedByOperatingActivities": record.net_cash_provided_by_operating_activities,

              # Investing Activities (Group 2)
             "investmentsInPropertyPlantAndEquipment": record.investments_in_property_plant_and_equipment,
             "acquisitionsNet": record.acquisitions_net,
             "purchasesOfInvestments": record.purchases_of_investments,
             "salesMaturitiesOfInvestments": record.sales_maturities_of_investments,
             "otherInvestingActivities": record.other_investing_activities,
             "netCashUsedForInvestingActivities": record.net_cash_used_for_investing_activities,

             # Financing Activities (Group 3)
             "debtRepayment": record.debt_repayment,
             "commonStockIssued": record.common_stock_issued,
             "commonStockRepurchased": record.common_stock_repurchased,
             "dividendsPaid": record.dividends_paid,
             "otherFinancingActivities": record.other_financing_activities,
             "netCashUsedProvidedByFinancingActivities": record.net_cash_used_provided_by_financing_activities,

             #  Free Cash Flow (Group 4)
             "operatingCashFlow": record.operating_cash_flow,
             "capitalExpenditure": record.capital_expenditure,
             "freeCashFlow": record.free_cash_flow,

              # Cash Balance & Changes (Group 5)
             "netChangeInCash": record.net_change_in_cash,
             "cashAtEndOfPeriod": record.cash_at_end_of_period,
             "cashAtBeginningOfPeriod": record.cash_at_beginning_of_period,
            } for record in cash_flow
        ]


   # @staticmethod
    def get_income_statement_data(ticker):
        income_statement = IncomeStatement.query.filter_by(ticker=ticker).all()
        if not income_statement:
            return None
        return [
            {
                # Date
             "date": record.date,

              # Calendar Year
             "calendarYear": record.calendar_year,

              # Revenue & Gross Profit (Group 1)
              "revenue": record.revenue,
             "costOfRevenue": record.cost_of_revenue,
             "grossProfit": record.gross_profit,
             "grossProfitRatio": record.gross_profit_ratio,

              # Operating Expenses (Group 2)
              "researchAndDevelopmentExpenses": record.research_and_development_expenses,
              "sellingGeneralAndAdministrativeExpenses": record.selling_general_and_administrative_expenses,
             "operatingExpenses": record.operating_expenses,
             "costAndExpenses": record.cost_and_expenses,
             "depreciationAndAmortization": record.depreciation_and_amortization,

             # Operating & Non-Operating Income (Group 3)
             "operatingIncome": record.operating_income,
             "operatingIncomeRatio": record.operating_income_ratio,
             "interestIncome": record.interest_income,
             "interestExpense": record.interest_expense,
             "totalOtherIncomeExpensesNet": record.total_other_income_expenses_net,
             "ebitda": record.ebitda,
             "ebitdaratio": record.ebitda_ratio,

             # Net Income (Group 4)
             "incomeBeforeTax": record.income_before_tax,
             "incomeBeforeTaxRatio": record.income_before_tax_ratio,
             "incomeTaxExpense": record.income_tax_expense,
             "netIncome": record.net_income,
             "netIncomeRatio": record.net_income_ratio,

             # Per Share Data (Group 5)
             "eps": record.eps,
             "epsDiluted": record.eps_diluted,
             "weightedAverageShsOut": record.weighted_average_shs_out,
             "weightedAverageShsOutDil": record.weighted_average_shs_out_dil
            } for record in income_statement
        ]

   # @staticmethod
    def get_balance_sheet_data1(ticker):
        balance_sheet = BalanceSheet.query.filter_by(ticker=ticker).all()
        print(balance_sheet)
        if not balance_sheet:
            return None
        return [
            {
                "date": record.date,
                "totalAssets": record.total_assets,
                "totalLiabilities": record.total_liabilities,
                "totalStockholdersEquity": record.total_stockholders_equity
            } for record in balance_sheet
        ]
    

    # @staticmethod
    def get_balance_sheet_data(ticker):
        balance_sheet = BalanceSheet.query.filter_by(ticker=ticker).all()
        if not balance_sheet:
          return None

        return [
           {
            # Date
             "date": record.date,
            
            # Calendar Year
             "calendarYear": record.calendar_year,
            
            # Assets
             "cashAndCashEquivalents": record.cash_and_cash_equivalents,
             "shortTermInvestments": record.short_term_investments,
             "cashAndShortTermInvestments": record.cash_and_short_term_investments,
             "netReceivables": record.net_receivables,
             "inventory": record.inventory,
              "otherCurrentAssets": record.other_current_assets,
             "totalCurrentAssets": record.total_current_assets,
             "propertyPlantEquipmentNet": record.property_plant_equipment_net,
             "goodwill": record.goodwill,
             "intangibleAssets": record.intangible_assets,
             "goodwillAndIntangibleAssets": record.goodwill_and_intangible_assets,
             "longTermInvestments": record.long_term_investments,
             "otherNonCurrentAssets": record.other_non_current_assets,
             "totalNonCurrentAssets": record.total_non_current_assets,
             "totalAssets": record.total_assets,
            
            # Liabilities
             "accountPayables": record.account_payables,
             "shortTermDebt": record.short_term_debt,
             "deferredRevenue": record.deferred_revenue,
             "otherCurrentLiabilities": record.other_current_liabilities,
             "totalCurrentLiabilities": record.total_current_liabilities,
             "longTermDebt": record.long_term_debt,
             "deferredRevenueNonCurrent": record.deferred_revenue_non_current,
             "deferredTaxLiabilitiesNonCurrent": record.deferred_tax_liabilities_non_current,
             "otherNonCurrentLiabilities": record.other_non_current_liabilities,
             "totalNonCurrentLiabilities": record.total_non_current_liabilities,
             "totalLiabilities": record.total_liabilities,

            # Equity
             "commonStock": record.common_stock,
             "retainedEarnings": record.retained_earnings,
             "accumulatedOtherComprehensiveIncomeLoss": record.accumulated_other_comprehensive_income_loss,
             "totalStockholdersEquity": record.total_stockholders_equity,
             "totalEquity": record.total_equity,
            } for record in balance_sheet
        ]
