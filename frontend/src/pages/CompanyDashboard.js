import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import BalanceSheet from './BalanceSheet';
import IncomeStatement from './IncomeStatement';
import CashFlow from './CashFlow';
import RedFlagsPopup from '../components/RedFlagsPopup';
import PositiveIndicatorsPopup from '../components/PositiveIndicatorsPopup';

function CompanyDashboard() {
    const { ticker } = useParams();
    const [companyData, setCompanyData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('balanceSheet');
    const [isRedFlagsOpen, setIsRedFlagsOpen] = useState(false);
    const [isPositivesOpen, setIsPositivesOpen] = useState(false);
    const [isExpanded, setIsExpanded] = useState(false); // For toggling full description

    useEffect(() => {
        const fetchCompanyData = async () => {
            try {
                const response = await axios.get(`http://127.0.0.1:5000/companyDB/${ticker}`);
                setCompanyData(response.data.company);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching company data:', error);
                setError('Failed to load company information.');
                setLoading(false);
            }
        };

        if (ticker) {
            fetchCompanyData();
        }
    }, [ticker]);

    const handleRedFlags = () => {
        setIsRedFlagsOpen(true);
    };

    const handlePositives = () => {
        setIsPositivesOpen(true);
    };

    const toggleDescription = () => {
        setIsExpanded(!isExpanded);
    };

    if (loading) {
        return <p style={styles.loading}>Loading...</p>;
    }

    if (error) {
        return <p style={styles.error}>{error}</p>;
    }

    return (
        <div style={styles.container}>
            <h1 style={styles.heading}>{companyData.companyName}</h1>
            <div style={styles.infoWrapper}>
                <div style={styles.descriptionContainer}>
                    {/* Description with Read More */}
                    <p
                        style={{
                            ...styles.description,
                            WebkitLineClamp: isExpanded ? 'unset' : 3, // Show 3 lines when collapsed
                        }}
                    >
                        {companyData.description}
                    </p>
                    {/* Show "Read More" or "Show Less" based on the expanded state */}
                    <span onClick={toggleDescription} style={styles.readMore}>
                        {isExpanded ? 'Show Less' : '... Read More'}
                    </span>
                </div>

                <div style={styles.buttonContainer}>
                    <button onClick={handleRedFlags} style={styles.redButton}>
                        Show Red Flags
                    </button>
                    <button onClick={handlePositives} style={styles.greenButton}>
                        Positives
                    </button>
                </div>
            </div>

            <div style={styles.tabsContainer}>
                <button onClick={() => setActiveTab('balanceSheet')} style={activeTab === 'balanceSheet' ? styles.activeTab : styles.tab}>Balance Sheet</button>
                <button onClick={() => setActiveTab('incomeStatement')} style={activeTab === 'incomeStatement' ? styles.activeTab : styles.tab}>Income Statement</button>
                <button onClick={() => setActiveTab('cashFlow')} style={activeTab === 'cashFlow' ? styles.activeTab : styles.tab}>Statement of Cash Flows</button>
            </div>

            <div style={styles.tabContent}>
                {activeTab === 'balanceSheet' && <BalanceSheet ticker={ticker} />}
                {activeTab === 'incomeStatement' && <IncomeStatement ticker={ticker} />}
                {activeTab === 'cashFlow' && <CashFlow ticker={ticker} />}
            </div>

            {/* Red Flags Popup */}
            <RedFlagsPopup isOpen={isRedFlagsOpen} onClose={() => setIsRedFlagsOpen(false)} />

            {/* Positive Indicators Popup */}
            <PositiveIndicatorsPopup isOpen={isPositivesOpen} onClose={() => setIsPositivesOpen(false)} />
        </div>
    );
}

const styles = {
    container: {
        margin: '0 auto',
        padding: '40px 20px',
        backgroundColor: '#111',
        color: '#fff',
        minHeight: '100vh',
        width: '100%',
        maxWidth: '100vw',
        boxSizing: 'border-box',
    },
    heading: {
        fontSize: '2.5rem',
        color: '#f5f5f5',
        marginBottom: '20px',
        textAlign: 'left',
    },
    infoWrapper: {
        display: 'flex',
        justifyContent: 'space-between',
        gap: '20px',
        marginBottom: '40px',
        alignItems: 'flex-start',
        flexWrap: 'wrap',
    },
    descriptionContainer: {
        maxWidth: '75%',
        position: 'relative',
    },
    description: {
        fontSize: '1.2rem',
        color: '#ccc',
        lineHeight: '1.5',
        display: '-webkit-box',
        WebkitBoxOrient: 'vertical',
        overflow: 'hidden',
        WebkitLineClamp: 3, // Limit to 3 lines when collapsed
    },
    readMore: {
        color: '#ff6b6b',
        cursor: 'pointer',
        fontWeight: 'bold',
    },
    buttonContainer: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-end',
        gap: '20px',
        marginTop: '20px'
        
    },
    redButton: {
        backgroundColor: '#dc3545',
        color: '#fff',
        padding: '12px 24px',
        width: '150px',
        cursor: 'pointer',
        border: 'none',
        borderRadius: '6px',
        
    },
    greenButton: {
        backgroundColor: '#28a745',
        color: '#fff',
        padding: '12px 24px',
        width: '150px',
        cursor: 'pointer',
        border: 'none',
        borderRadius: '6px',
      
        
    },
    tabsContainer: {
        display: 'flex',
        justifyContent: 'center',
        borderBottom: '1px solid #444',
        marginBottom: '20px',
        flexWrap: 'wrap',
    },
    tab: {
        backgroundColor: '#222',
        color: '#fff',
        padding: '12px 30px',
        margin: '10px',
        cursor: 'pointer',
        border: 'none',
        borderRadius: '6px 6px 0 0',
        flex: '1',
        minWidth: '150px',
    },
    activeTab: {
        backgroundColor: '#ff6b6b',
        color: '#fff',
        padding: '12px 30px',
        margin: '10px',
        cursor: 'pointer',
        border: 'none',
        borderRadius: '6px 6px 0 0',
        boxShadow: '0 4px 8px rgba(255, 107, 107, 0.4)',
        flex: '1',
        minWidth: '150px',
    },
    tabContent: {
        marginTop: '20px',
        padding: '20px',
        backgroundColor: '#222',
        borderRadius: '8px',
        color: '#fff',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
    },
    loading: {
        fontSize: '1.5rem',
        color: '#fff',
    },
    error: {
        fontSize: '1.5rem',
        color: '#ff6b6b',
    },
};

export default CompanyDashboard;
