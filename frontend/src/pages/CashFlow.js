import React, { useEffect, useState } from 'react';
import axios from 'axios';
import FilterComponent from './FilterComponent';  // Import the reusable component

function CashFlow({ ticker }) {
    const [cashFlowData, setCashFlowData] = useState(null);

    // Define the groups and their metrics for Cash Flow Statement
    const cashFlowGroups = [
        {
            group: "Operating Activities",
            metrics: [
                { label: "Net Income", value: "netIncome" },
                { label: "Depreciation and Amortization", value: "depreciationAndAmortization" },
                { label: "Change in Working Capital", value: "changeInWorkingCapital" },
                { label: "Net Cash Provided by Operating Activities", value: "netCashProvidedByOperatingActivities" }
            ]
        },
        {
            group: "Investing Activities",
            metrics: [
                { label: "Investments in Property, Plant, and Equipment", value: "investmentsInPropertyPlantAndEquipment" },
                { label: "Acquisitions (Net)", value: "acquisitionsNet" },
                { label: "Purchases of Investments", value: "purchasesOfInvestments" },
                { label: "Sales/Maturities of Investments", value: "salesMaturitiesOfInvestments" },
                { label: "Net Cash Used for Investing Activities", value: "netCashUsedForInvestingActivites" }
            ]
        },
        {
            group: "Financing Activities",
            metrics: [
                { label: "Debt Repayment", value: "debtRepayment" },
                { label: "Common Stock Issued", value: "commonStockIssued" },
                { label: "Common Stock Repurchased", value: "commonStockRepurchased" },
                { label: "Dividends Paid", value: "dividendsPaid" },
                { label: "Net Cash Provided by/Used for Financing Activities", value: "netCashUsedProvidedByFinancingActivities" }
            ]
        },
        {
            group: "Free Cash Flow",
            metrics: [
                { label: "Operating Cash Flow", value: "operatingCashFlow" },
                { label: "Capital Expenditure", value: "capitalExpenditure" },
                { label: "Free Cash Flow", value: "freeCashFlow" }
            ]
        },
        {
            group: "Cash at Period End",
            metrics: [
                { label: "Net Change in Cash", value: "netChangeInCash" },
                { label: "Cash at End of Period", value: "cashAtEndOfPeriod" },
                { label: "Cash at Beginning of Period", value: "cashAtBeginningOfPeriod" }
            ]
        }
    ];

    useEffect(() => {
        const fetchCashFlow = async () => {
            try {
                const response = await axios.get(`http://127.0.0.1:5000/cashFlowDB/${ticker}`);
                setCashFlowData(response.data.cashFlow);
            } catch (error) {
                console.error('Error fetching cash flow statement:', error);
            }
        };
        fetchCashFlow();
    }, [ticker]);

    if (!cashFlowData) {
        return <p>Loading cash flow data...</p>;
    }

    return (
        <div>
            <h2>Cash Flow Statement</h2>
            {/* Pass data and groups to FilterComponent */}
            <FilterComponent data={cashFlowData} groups={cashFlowGroups} />
        </div>
    );
}

export default CashFlow;
