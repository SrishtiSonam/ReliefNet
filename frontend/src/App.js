import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import SimulationPage from './pages/SimulationPage';
import AuditLogPage from './pages/AuditLogPage';
import Navbar from './components/Navbar';
import './App.css';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:4000/api';
const ML_API_BASE = process.env.REACT_APP_ML_API_BASE || 'http://localhost:8000';

function App() {
  const [user, setUser] = useState(null);
  const [sessionId, setSessionId] = useState(localStorage.getItem('sessionId'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    if (sessionId) {
      fetch(`${API_BASE}/session/current`, {
        headers: {
          'Authorization': `Bearer ${sessionId}`
        }
      })
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        throw new Error('Session expired');
      })
      .then(data => {
        setUser(data.user);
      })
      .catch(() => {
        localStorage.removeItem('sessionId');
        setSessionId(null);
      })
      .finally(() => {
        setLoading(false);
      });
    } else {
      setLoading(false);
    }
  }, [sessionId]);

  const login = async (username, password) => {
    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();
      
      if (data.success) {
        setUser(data.user);
        setSessionId(data.sessionId);
        localStorage.setItem('sessionId', data.sessionId);
        return { success: true };
      } else {
        return { success: false, message: data.message };
      }
    } catch (error) {
      return { success: false, message: 'Network error' };
    }
  };

  const logout = async () => {
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ sessionId })
      });
    } catch (error) {
      console.error('Logout error:', error);
    }

    setUser(null);
    setSessionId(null);
    localStorage.removeItem('sessionId');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  return (
    <Router>
      <div className="App min-h-screen bg-gray-50">
        {user && <Navbar user={user} onLogout={logout} />}
        
        <Routes>
          <Route 
            path="/login" 
            element={
              user ? <Navigate to="/" /> : <LoginPage onLogin={login} />
            } 
          />
          
          <Route 
            path="/" 
            element={
              user ? (
                <DashboardPage 
                  user={user} 
                  sessionId={sessionId} 
                  apiBase={API_BASE}
                  mlApiBase={ML_API_BASE}
                />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />
          
          <Route 
            path="/simulation" 
            element={
              user ? (
                <SimulationPage 
                  user={user} 
                  sessionId={sessionId} 
                  apiBase={API_BASE}
                  mlApiBase={ML_API_BASE}
                />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />
          
          <Route 
            path="/audit" 
            element={
              user ? (
                <AuditLogPage 
                  user={user} 
                  sessionId={sessionId} 
                  apiBase={API_BASE}
                />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;