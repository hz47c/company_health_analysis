import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function SearchPage() {
    const [ticker, setTicker] = useState('');
    const [isPopupOpen, setIsPopupOpen] = useState(false); // State for popup visibility
    const navigate = useNavigate();

    const handleSearch = async (event) => {
        event.preventDefault();
        if (ticker.trim()) {
            try {
                // Fetch data from the financialData API
                const response = await axios.get(`https://company-health-analysis-backend.onrender.com/financialData/${ticker}`);
                console.log('API Response:', response.data);

                const { balanceSheet, cashFlow, companyName, incomeStatement } = response.data;
                const isDataMissing = 
                    !balanceSheet.length || 
                    !cashFlow.length || 
                    !companyName?.companyName || 
                    !incomeStatement.length;

                if (isDataMissing) {
                    console.log("Incomplete data found. Redirecting to error page");
                    navigate('/error');
                } else {
                    console.log("Data found. Navigating to company dashboard");
                    navigate(`/company/${ticker}`);
                }
            } catch (error) {
                console.error('Error fetching data:', error);
                navigate('/error');
            }
        }
    };

    const togglePopup = () => {
        setIsPopupOpen(!isPopupOpen); // Toggle popup visibility
    };

    return (
        <div style={styles.container}>
            <h1 style={styles.heading}>Explore Financial Insights</h1>
            <p style={styles.subtitle}>Empowering you with financial knowledge</p>
            <form onSubmit={handleSearch} style={styles.form}>
                <input
                    type="text"
                    placeholder="Enter U.S Stock Ticker..."
                    value={ticker}
                    onChange={(e) => setTicker(e.target.value)}
                    style={styles.input}
                />
                <button type="submit" style={styles.button}>Search</button>
            </form>

            <button onClick={togglePopup} style={styles.stockInfoButton}>Information Source</button>

            {isPopupOpen && (
                <div style={styles.popupOverlay} onClick={togglePopup}>
                    <div style={styles.popupContent} onClick={(e) => e.stopPropagation()}>
                        <h2>Company Financials Source</h2>
                        <p>All information is obtained from SEC website and Finanical Model prep website</p>
                        <button onClick={togglePopup} style={styles.closeButton}>Close</button>
                    </div>
                </div>
            )}
        </div>
    );
}

const styles = {
    container: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        backgroundColor: '#111',
        color: '#fff',
        fontFamily: 'Arial, sans-serif',
        padding: '0 20px',
    },
    heading: {
        fontSize: '2.5rem',
        color: '#f5f5f5',
        marginBottom: '20px',
    },
    subtitle: {
        fontSize: '1.2rem',
        color: '#999',
        marginBottom: '40px',
    },
    form: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: '100%',
    },
    input: {
        padding: '12px 15px',
        width: '300px',
        borderRadius: '6px',
        border: '1px solid #444',
        backgroundColor: '#222',
        color: '#fff',
        marginRight: '10px',
        fontSize: '1rem',
    },
    button: {
        padding: '12px 20px',
        border: 'none',
        borderRadius: '6px',
        backgroundColor: '#ff6b6b',
        color: '#fff',
        cursor: 'pointer',
        fontSize: '1rem',
    },
    stockInfoButton: {
        position: 'absolute', // Position the button absolutely within the container
        bottom: '20px', // 20px from the bottom of the container
        right: '20px', // 20px from the right of the container
        padding: '12px 20px',
        border: 'none',
        borderRadius: '6px',
        backgroundColor: '#4caf50',
        color: '#fff',
        cursor: 'pointer',
        fontSize: '1rem',
    },
    popupOverlay: {
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
    },
    popupContent: {
        backgroundColor: '#222',
        color: '#fff',
        padding: '20px',
        borderRadius: '10px',
        width: '400px',
        textAlign: 'center',
    },
    closeButton: {
        marginTop: '20px',
        padding: '10px 15px',
        border: 'none',
        borderRadius: '6px',
        backgroundColor: '#ff6b6b',
        color: '#fff',
        cursor: 'pointer',
        fontSize: '1rem',
    },
};

export default SearchPage;
