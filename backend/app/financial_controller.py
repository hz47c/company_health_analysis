# app/financial_controller.py

from flask import Blueprint, jsonify
from .financial_service import FinancialService
from .analysis_service import AnalysisService
from .redflags_service import RedFlagsService
from .positive_indicators_service import PositiveIndicatorsService
financial_bp = Blueprint('financial', __name__)
financial_service = FinancialService()
analysis_service = AnalysisService()
redflags_service = RedFlagsService()
positive_indicators_service = PositiveIndicatorsService()

@financial_bp.route('/companyDB/<ticker>', methods=['GET'])
def get_company_db(ticker):
    company_data = FinancialService.get_company_data(ticker)
    if not company_data:
        return jsonify({"error": "Company not found"}), 404
    return jsonify({"company": company_data}), 200

@financial_bp.route('/cashFlowDB/<ticker>', methods=['GET'])
def get_cash_flow_db(ticker):
    cash_flow_data = FinancialService.get_cash_flow_data(ticker)
    if not cash_flow_data:
        return jsonify({"error": "Cash flow data not found"}), 404
    return jsonify({"cashFlow": cash_flow_data}), 200

@financial_bp.route('/incomeStatementDB/<ticker>', methods=['GET'])
def get_income_statement_db(ticker):
    income_statement_data = FinancialService.get_income_statement_data(ticker)
    if not income_statement_data:
        return jsonify({"error": "Income statement data not found"}), 404
    return jsonify({"incomeStatement": income_statement_data}), 200

@financial_bp.route('/balanceSheetDB/<ticker>', methods=['GET'])
def get_balance_sheet_db(ticker):
    balance_sheet_data = FinancialService.get_balance_sheet_data(ticker)
    if not balance_sheet_data:
        return jsonify({"error": "Balance sheet data not found"}), 404
    return jsonify({"balanceSheet": balance_sheet_data}), 200










@financial_bp.route('/redflags/<ticker>', methods=['GET'])
def get_redflags(ticker):
    redflags_data = redflags_service.analyze_red_flags(ticker)
    return jsonify({'redflags': redflags_data})

# New endpoint to return financial data as a DataFrame in JSON format
@financial_bp.route('/financialdataframe/<ticker>', methods=['GET'])
def get_financial_data_as_dataframe(ticker):
    # Call the method from AnalysisService to retrieve DataFrame
    df = analysis_service.get_financial_data_as_dataframe(ticker)
    print(df)
    # Convert DataFrame to JSON format
    json_data = df.to_json(orient='records')
    
    # Return JSON response
    return jsonify(json_data)



@financial_bp.route('/positiveindicators/<ticker>', methods=['GET'])
def get_positive_indicators(ticker):
    positive_data = positive_indicators_service.analyze_positive_indicators(ticker)
    return jsonify({'positive_indicators': positive_data})

@financial_bp.route('/balanceSheet/<ticker>', methods=['GET'])
def get_balance_sheet(ticker):
    return jsonify(financial_service.fetch_balance_sheet(ticker))

@financial_bp.route('/companyName/<ticker>', methods=['GET'])
def get_company_name(ticker):
    return jsonify(financial_service.fetch_company_name(ticker))

@financial_bp.route('/incomeStatement/<ticker>', methods=['GET'])
def get_income_statement(ticker):
    return jsonify(financial_service.fetch_income_statement(ticker))

@financial_bp.route('/cashFlow/<ticker>', methods=['GET'])
def get_cash_flow(ticker):
    return jsonify(financial_service.fetch_cash_flow(ticker))

@financial_bp.route('/financialData/<ticker>', methods=['GET'])
def get_all_financial_data(ticker):
    return jsonify(financial_service.fetch_all_data(ticker))
