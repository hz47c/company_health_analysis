import React, { useEffect, useState } from 'react';
import axios from 'axios';
import FilterComponent from './FilterComponent';  // Import the reusable component

function IncomeStatement({ ticker }) {
    const [incomeStatementData, setIncomeStatementData] = useState(null);

    // Define the groups and their metrics for Income Statement
    const incomeStatementGroups = [
        {
            group: "Revenue & Gross Profit",
            metrics: [
                { label: "Revenue", value: "revenue" },
                { label: "Cost of Revenue", value: "costOfRevenue" },
                { label: "Gross Profit", value: "grossProfit" },
                { label: "Gross Profit Ratio", value: "grossProfitRatio" }
            ]
        },
        {
            group: "Operating Expenses",
            metrics: [
                { label: "Research and Development Expenses", value: "researchAndDevelopmentExpenses" },
                { label: "Selling, General, and Administrative Expenses", value: "sellingGeneralAndAdministrativeExpenses" },
                { label: "Operating Expenses", value: "operatingExpenses" },
                { label: "Cost and Expenses", value: "costAndExpenses" },
                { label: "Depreciation and Amortization", value: "depreciationAndAmortization" }
            ]
        },
        {
            group: "Operating & Non-Operating Income",
            metrics: [
                { label: "Operating Income", value: "operatingIncome" },
                { label: "Operating Income Ratio", value: "operatingIncomeRatio" },
                { label: "Interest Income", value: "interestIncome" },
                { label: "Interest Expense", value: "interestExpense" },
                { label: "Total Other Income/Expenses Net", value: "totalOtherIncomeExpensesNet" },
                { label: "EBITDA", value: "ebitda" },
                { label: "EBITDA Ratio", value: "ebitdaratio" }
            ]
        },
        {
            group: "Net Income",
            metrics: [
                { label: "Income Before Tax", value: "incomeBeforeTax" },
                { label: "Income Before Tax Ratio", value: "incomeBeforeTaxRatio" },
                { label: "Income Tax Expense", value: "incomeTaxExpense" },
                { label: "Net Income", value: "netIncome" },
                { label: "Net Income Ratio", value: "netIncomeRatio" }
            ]
        },
        {
            group: "Per Share Data",
            metrics: [
                { label: "Earnings per Share (EPS)", value: "eps" },
                { label: "EPS Diluted", value: "epsdiluted" },
                { label: "Weighted Average Shares Outstanding", value: "weightedAverageShsOut" },
                { label: "Weighted Average Shares Outstanding (Diluted)", value: "weightedAverageShsOutDil" }
            ]
        }
    ];

    useEffect(() => {
        const fetchIncomeStatement = async () => {
            try {
                const response = await axios.get(`http://127.0.0.1:5000/incomeStatementDB/${ticker}`);
                setIncomeStatementData(response.data.incomeStatement);
            } catch (error) {
                console.error('Error fetching income statement:', error);
            }
        };
        fetchIncomeStatement();
    }, [ticker]);

    if (!incomeStatementData) {
        return <p>Loading income statement data...</p>;
    }

    return (
        <div>
            <h2>Income Statement</h2>
            {/* Pass data and groups to FilterComponent */}
            <FilterComponent 
            data={incomeStatementData} 
            groups={incomeStatementGroups} 
            selectedOptionStyle={{ color: 'white', backgroundColor: 'green' }} // Green for selected
            unselectedOptionStyle={{ color: 'white', backgroundColor: 'blue' }} // Blue for unselected
            
            />
        </div>
    );
}

export default IncomeStatement;
