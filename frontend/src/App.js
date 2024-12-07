// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SearchPage from './pages/SearchPage';
import CompanyDashboard from './pages/CompanyDashboard';
import RedFlagsPage from './pages/RedFlagsPage';
import PositiveIndicatorsPage from './pages/PositiveIndicatorsPage';
import ErrorPage from './pages/ErrorPage';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<SearchPage />} />
                <Route path="/company/:ticker" element={<CompanyDashboard />} />
                <Route path="/redflags/:ticker" element={<RedFlagsPage />} />
                <Route path="/positiveindicators/:ticker" element={<PositiveIndicatorsPage />} />
                <Route path="/error" element={<ErrorPage />} />
            </Routes>
        </Router>
    );
}

export default App;
