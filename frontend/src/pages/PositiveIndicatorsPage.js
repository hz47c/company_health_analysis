// src/pages/PositiveIndicatorsPage.js
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

function PositiveIndicatorsPage() {
    const { ticker } = useParams();
    
    const [positiveIndicators, setPositiveIndicators] = useState(''); 
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPositives = async () => {
            try {
                const response = await axios.get(`http://127.0.0.1:5000/positiveindicators/${ticker}`);
                
                setPositiveIndicators(response.data.positive_indicators);
  
                  

                setLoading(false);
            } catch (error) {
                console.error('Error fetching positive indicators:', error);
                alert('Failed to load positive indicators.');
            }
        };
        fetchPositives();
    }, [ticker]);

    if (loading) {
        return <p>Loading positive indicators...</p>;
    }

    return (
        <div style={styles.container}>
            <h1>Positive Indicators for {ticker.toUpperCase()}</h1>
            <pre style={styles.data}>{positiveIndicators}</pre>
        </div>
    );
}

const styles = {
    container: {
        margin: '20px',
        textAlign: 'center',
    },
    data: {
        backgroundColor: '#d4edda',
        color: '#155724',
        padding: '20px',
        borderRadius: '8px',
        whiteSpace: 'pre-wrap',
        textAlign: 'left',
    },
};

export default PositiveIndicatorsPage;
