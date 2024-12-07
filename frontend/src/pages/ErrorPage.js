// src/pages/ErrorPage.js
import React from 'react';
import { useNavigate } from 'react-router-dom';

function ErrorPage() {
    const navigate = useNavigate();

    const handleBackToSearch = () => {
        navigate('/'); // Navigate back to the SearchPage
    };

    return (
        <div style={styles.container}>
            <h1 style={styles.heading}>Data Not Found</h1>
            <p style={styles.message}>
                We couldn't find any data for the ticker you entered. Please try again with a different stock ticker.
            </p>
            <button onClick={handleBackToSearch} style={styles.button}>Back to Search</button>
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
        color: '#ff6b6b',
        marginBottom: '20px',
    },
    message: {
        fontSize: '1.2rem',
        color: '#ccc',
        marginBottom: '40px',
        textAlign: 'center',
        maxWidth: '600px',
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

export default ErrorPage;
