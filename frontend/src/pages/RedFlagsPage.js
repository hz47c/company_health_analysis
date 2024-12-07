// src/pages/RedFlagsPage.js
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

function RedFlagsPage() {
    const { ticker } = useParams();
    const [redFlags, setRedFlags] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
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
    }, [ticker]);

    if (loading) {
        return <p>Loading red flags...</p>;
    }

    return (
        <div style={styles.container}>
            <h1>Red Flags for {ticker.toUpperCase()}</h1>
            <pre style={styles.data}>{redFlags}</pre>
        </div>
    );
}

const styles = {
    container: {
        margin: '20px',
        textAlign: 'center',
    },
    data: {
        backgroundColor: '#f8d7da',
        color: '#721c24',
        padding: '20px',
        borderRadius: '8px',
        whiteSpace: 'pre-wrap',
        textAlign: 'left',
    },
};

export default RedFlagsPage;
