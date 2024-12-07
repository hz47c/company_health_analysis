import React from 'react';

const SlideInPopup = ({ title, data, onClose }) => {
    return (
        <div style={styles.overlay}>
            <div style={styles.popup}>
                <div style={styles.header}>
                    <h2>{title}</h2>
                    <button onClick={onClose} style={styles.closeButton}>X</button>
                </div>
                <div style={styles.content}>
                    {data.length > 0 ? (
                        data.map((item, index) => (
                            <div key={index} style={styles.item}>
                                <h3>{item.title || "Data"}</h3>
                                <p>{item.description || item}</p>
                            </div>
                        ))
                    ) : (
                        <p>No data available.</p>
                    )}
                </div>
            </div>
        </div>
    );
};

const styles = {
    overlay: {
        position: 'fixed',
        top: 0,
        right: 0,
        bottom: 0,
        width: '30%',
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        zIndex: 1000,
    },
    popup: {
        backgroundColor: '#fff',
        color: '#333',
        height: '100%',
        overflowY: 'auto',
        padding: '20px',
        boxSizing: 'border-box',
    },
    header: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px',
    },
    closeButton: {
        background: 'red',
        color: '#fff',
        border: 'none',
        padding: '5px 10px',
        cursor: 'pointer',
    },
    content: {
        maxHeight: '90%',
    },
    item: {
        backgroundColor: '#f0f0f0',
        padding: '15px',
        borderRadius: '5px',
        marginBottom: '15px',
    },
};

export default SlideInPopup;
