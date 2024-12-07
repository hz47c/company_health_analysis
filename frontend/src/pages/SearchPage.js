// src/pages/SearchPage.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function SearchPage() {
    const [ticker, setTicker] = useState('');
    const navigate = useNavigate();

    const handleSearch = async (event) => {
        event.preventDefault();
        if (ticker.trim()) {
            try {
                // Fetch data from the financialData API
                const response = await axios.get(`http://127.0.0.1:5000/financialData/${ticker}`);
                console.log('API Response:', response.data); // Debugging: check API response

                // Check if essential data is missing or empty
                const { balanceSheet, cashFlow, companyName, incomeStatement } = response.data;
                const isDataMissing = 
                    !balanceSheet.length ||  // Check if balanceSheet is empty
                    !cashFlow.length ||      // Check if cashFlow is empty
                    !companyName?.companyName ||  // Check if companyName is null or missing
                    !incomeStatement.length; // Check if incomeStatement is empty

                if (isDataMissing) {
                    console.log("Incomplete data found. Redirecting to error page");
                    navigate('/error'); // Redirect to error page if data is incomplete
                } else {
                    console.log("Data found. Navigating to company dashboard");
                    navigate(`/company/${ticker}`); // Redirect to dashboard if data is valid
                }
            } catch (error) {
                console.error('Error fetching data:', error);
                navigate('/error'); // Redirect to error page on API error
            }
        }
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
};

export default SearchPage;
