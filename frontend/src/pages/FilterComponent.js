import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
} from 'chart.js';
import { Box, FormControl, InputLabel, MenuItem, Select, Typography } from '@mui/material';

// Register chart components for ChartJS
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

const FilterComponent = ({ data, groups }) => {
    const [selectedGroup, setSelectedGroup] = useState(groups[0].group); // Default to first group
    const [selectedMetric, setSelectedMetric] = useState(groups[0].metrics[0].value); // Default to first metric
    const [chartData, setChartData] = useState(null);

    useEffect(() => {
        if (data && selectedMetric) {
            const sortedData = [...data].sort((a, b) => a.calendarYear - b.calendarYear);
            const years = sortedData.map(item => item.calendarYear);
            const values = sortedData.map(item => item[selectedMetric]);

            setChartData({
                labels: years,
                datasets: [
                    {
                        label: selectedMetric,
                        data: values,
                        borderColor: 'rgba(34, 202, 236, 1)',
                        backgroundColor: 'rgba(34, 202, 236, 0.3)',
                        borderWidth: 2,
                        fill: true,
                        pointBackgroundColor: '#22CAEC',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                    }
                ]
            });
        }
    }, [data, selectedMetric]);

    const handleGroupChange = (event) => {
        const group = groups.find(g => g.group === event.target.value);
        setSelectedGroup(group.group);
        setSelectedMetric(group.metrics[0].value);
    };

    const handleMetricChange = (event) => {
        setSelectedMetric(event.target.value);
    };

    const currentMetrics = groups.find(group => group.group === selectedGroup)?.metrics || [];

    return (
        <Box sx={{ p: 4, maxWidth: '900px', margin: '0 auto', backgroundColor: '#1c1c1c', borderRadius: '8px' }}>
            {/* Title */}
            <Typography variant="h5" align="center" gutterBottom sx={{ color: '#f0f0f0' }}>
                Select Financial Data
            </Typography>

            {/* Dropdown for Category */}
            <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel id="group-label" sx={{ color: '#b0bec5' }}>Category</InputLabel>
                <Select
                    labelId="group-label"
                    id="group-select"
                    value={selectedGroup}
                    label="Category"
                    onChange={handleGroupChange}
                    sx={{
                        backgroundColor: '#333',
                        color: '#f0f0f0', // Color for selected item when dropdown is closed
                        '& .MuiSvgIcon-root': { color: '#f0f0f0' } // Color for dropdown arrow
                    }}
                >
                    {groups.map(group => (
                        <MenuItem
                            key={group.group}
                            value={group.group}
                            sx={{
                                color: '#f0f0f0',
                                backgroundColor: selectedGroup === group.group ? '#555' : '#333', // Darker bg for selected item
                                '&.Mui-selected': {
                                    backgroundColor: '#444', // Set background color for selected item
                                    color: '#fff' // Set text color for selected item
                                },
                                '&.Mui-selected:hover': {
                                    backgroundColor: '#666' // Different hover color when selected
                                },
                                '&:hover': {
                                    backgroundColor: '#555' // Hover color for non-selected items
                                }
                            }}
                        >
                            {group.group}
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>

            {/* Dropdown for Metric */}
            <FormControl fullWidth sx={{ mb: 4 }}>
                <InputLabel id="metric-label" sx={{ color: '#b0bec5' }}>Metric</InputLabel>
                <Select
                    labelId="metric-label"
                    id="metric-select"
                    value={selectedMetric}
                    label="Metric"
                    onChange={handleMetricChange}
                    sx={{
                        backgroundColor: '#333',
                        color: '#f0f0f0', // Color for selected item when dropdown is closed
                        '& .MuiSvgIcon-root': { color: '#f0f0f0' } // Color for dropdown arrow
                    }}
                >
                    {currentMetrics.map(metric => (
                        <MenuItem
                            key={metric.value}
                            value={metric.value}
                            sx={{
                                color: '#f0f0f0',
                                backgroundColor: selectedMetric === metric.value ? '#555' : '#333', // Darker bg for selected item
                                '&.Mui-selected': {
                                    backgroundColor: '#444', // Set background color for selected item
                                    color: '#fff' // Set text color for selected item
                                },
                                '&.Mui-selected:hover': {
                                    backgroundColor: '#666' // Different hover color when selected
                                },
                                '&:hover': {
                                    backgroundColor: '#555' // Hover color for non-selected items
                                }
                            }}
                        >
                            {metric.label}
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>

            {/* Render Chart */}
            {chartData && (
                <Box sx={{ boxShadow: 3, p: 3, backgroundColor: '#2a2a2a', borderRadius: '8px' }}>
                    <Line
                        data={chartData}
                        options={{
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    grid: {
                                        color: '#444'
                                    },
                                    ticks: {
                                        color: '#d4d4d4'
                                    }
                                },
                                x: {
                                    grid: {
                                        color: '#444'
                                    },
                                    ticks: {
                                        color: '#d4d4d4'
                                    }
                                }
                            },
                            responsive: true,
                            plugins: {
                                legend: {
                                    display: true,
                                    position: 'top',
                                    labels: {
                                        color: '#d4d4d4'
                                    }
                                },
                                title: {
                                    display: true,
                                    text: `Trends of ${selectedMetric.replace(/([A-Z])/g, ' $1')}`,
                                    color: '#d4d4d4',
                                    font: {
                                        size: 18
                                    }
                                }
                            }
                        }}
                    />
                </Box>
            )}
        </Box>
    );
};

export default FilterComponent;
