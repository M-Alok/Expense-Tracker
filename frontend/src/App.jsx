import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useState, useEffect } from 'react';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';

export default function App() {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      setToken(savedToken);
      // Decode token to get user info
      try {
        const payload = JSON.parse(atob(savedToken.split('.')[1]));
        setUser({ username: payload.sub });
      } catch (error) {
        console.error('Error decoding token:', error);
        handleLogout();
      }
    }
  }, []);

  const handleLogout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  };

  return (
    <>
      <Toaster position="top-center" />
      <Router>
        <Routes>
          <Route 
            path="/login" 
            element={
              token ? <Navigate to="/" /> : 
              <Login 
                setToken={setToken} 
                setUser={setUser} 
              />
            } 
          />
          <Route 
            path="/register" 
            element={
              token ? <Navigate to="/" /> : 
              <Register />
            } 
          />
          <Route 
            path="/" 
            element={
              token ? 
              <Dashboard 
                token={token} 
                user={user} 
                onLogout={handleLogout} 
              /> : 
              <Navigate to="/login" />
            } 
          />
        </Routes>
      </Router>
    </>
  );
}