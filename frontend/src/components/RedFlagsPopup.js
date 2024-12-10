import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

function RedFlagsPopup({ isOpen, onClose }) {
    const { ticker } = useParams();
    const [redFlags, setRedFlags] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (isOpen) {
            const fetchRedFlags = async () => {
                try {
                    const response = await axios.get(`http://127.0.0.1:5000/redflags/${ticker}`);
                    setRedFlags(response.data.redflags);
                    setLoading(false);
                } catch (error) {
                    console.error('Error fetching red flags:', error);
                    alert('Failed to load red flags data.');
                }
            };
            fetchRedFlags();
        }
    }, [ticker, isOpen]);

    if (!isOpen) return null;

    return (
        <div style={styles.overlay}>
            <div style={styles.popup}>
                <button onClick={onClose} style={styles.closeButton}>X</button>
                <h1 style={styles.heading}>Red Flags for {ticker.toUpperCase()}</h1>
                {loading ? (
                    <p style={styles.loading}>Loading red flags...</p>
                ) : (
                    <pre style={styles.data}>{redFlags}</pre>
                )}
            </div>
        </div>
    );
}

const styles = {
    overlay: {
        position: 'fixed',
        top: 0,
        right: 0,
        bottom: 0,
        left: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.6)',
        display: 'flex',
        justifyContent: 'flex-end',
        zIndex: 1000,
    },
    popup: {
        width: '50%',
        maxWidth: '600px',
        height: '100%',
        backgroundColor: '#1e1e1e',  // Dark background
        color: '#f5f5f5',             // Light text color
        padding: '20px',
        boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
        overflowY: 'auto',
        position: 'relative',
    },
    closeButton: {
        position: 'absolute',
        top: '10px',
        right: '10px',
        backgroundColor: 'transparent',
        border: 'none',
        fontSize: '18px',
        color: '#ff6b6b', // Close button color
        cursor: 'pointer',
    },
    heading: {
        color: '#ff6b6b',
        marginBottom: '15px',
    },
    loading: {
        color: '#aaa',
    },
    data: {
        backgroundColor: '#2e2e2e', // Darker background for data
        color: '#f5f5f5',
        padding: '20px',
        borderRadius: '8px',
        whiteSpace: 'pre-wrap',
        textAlign: 'left',
    },
};

export default RedFlagsPopup;
