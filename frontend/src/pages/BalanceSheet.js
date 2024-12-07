import React, { useEffect, useState } from 'react';
import axios from 'axios';
import FilterComponent from './FilterComponent';  // Import the reusable component

function BalanceSheet({ ticker }) {
    const [balanceSheetData, setBalanceSheetData] = useState(null);

    // Define the groups and their metrics for Balance Sheet
    const balanceSheetGroups = [
        {
            group: "Assets",
            metrics: [
                { label: "Cash and Cash Equivalents", value: "cashAndCashEquivalents" },
                { label: "Short-term Investments", value: "shortTermInvestments" },
                { label: "Cash and Short-term Investments", value: "cashAndShortTermInvestments" },
                { label: "Net Receivables", value: "netReceivables" },
                { label: "Inventory", value: "inventory" },
                { label: "Other Current Assets", value: "otherCurrentAssets" },
                { label: "Total Current Assets", value: "totalCurrentAssets" },
                { label: "Property, Plant, and Equipment Net", value: "propertyPlantEquipmentNet" },
                { label: "Goodwill", value: "goodwill" },
                { label: "Intangible Assets", value: "intangibleAssets" },
                { label: "Goodwill and Intangible Assets", value: "goodwillAndIntangibleAssets" },
                { label: "Long-term Investments", value: "longTermInvestments" },
                { label: "Other Non-current Assets", value: "otherNonCurrentAssets" },
                { label: "Total Non-current Assets", value: "totalNonCurrentAssets" },
                { label: "Total Assets", value: "totalAssets" }
            ]
        },
        {
            group: "Liabilities",
            metrics: [
                { label: "Account Payables", value: "accountPayables" },
                { label: "Short-term Debt", value: "shortTermDebt" },
                { label: "Deferred Revenue", value: "deferredRevenue" },
                { label: "Other Current Liabilities", value: "otherCurrentLiabilities" },
                { label: "Total Current Liabilities", value: "totalCurrentLiabilities" },
                { label: "Long-term Debt", value: "longTermDebt" },
                { label: "Deferred Revenue Non-current", value: "deferredRevenueNonCurrent" },
                { label: "Deferred Tax Liabilities Non-current", value: "deferredTaxLiabilitiesNonCurrent" },
                { label: "Other Non-current Liabilities", value: "otherNonCurrentLiabilities" },
                { label: "Total Non-current Liabilities", value: "totalNonCurrentLiabilities" },
                { label: "Total Liabilities", value: "totalLiabilities" }
            ]
        },
        {
            group: "Equity",
            metrics: [
                { label: "Common Stock", value: "commonStock" },
                { label: "Retained Earnings", value: "retainedEarnings" },
                { label: "Accumulated Other Comprehensive Income (Loss)", value: "accumulatedOtherComprehensiveIncomeLoss" },
                { label: "Total Stockholders' Equity", value: "totalStockholdersEquity" },
                { label: "Total Equity", value: "totalEquity" }
            ]
        }
    ];

    useEffect(() => {
        const fetchBalanceSheet = async () => {
            try {
                const response = await axios.get(`http://127.0.0.1:5000/balanceSheetDB/${ticker}`);
                setBalanceSheetData(response.data.balanceSheet);
            } catch (error) {
                console.error('Error fetching balance sheet:', error);
            }
        };
        fetchBalanceSheet();
    }, [ticker]);

    if (!balanceSheetData) {
        return <p>Loading balance sheet data...</p>;
    }

    return (
        <div>
            <h2>Balance Sheet</h2>
            {/* Pass data and groups to FilterComponent */}
            <FilterComponent data={balanceSheetData} groups={balanceSheetGroups} />
        </div>
    );
}

export default BalanceSheet;
