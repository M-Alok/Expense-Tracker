import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { IndianRupee } from 'lucide-react';
import toast from 'react-hot-toast';

const API_BASE = import.meta.env.VITE_API_URL;

export default function Login({ setToken, setUser }) {
  const [loginData, setLoginData] = useState({ username: '', password: '' });
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    const loadingToast = toast.loading('Logging in...');
    try {
      const formBody = new URLSearchParams();
      formBody.append('username', loginData.username);
      formBody.append('password', loginData.password);

      const response = await fetch(`${API_BASE}/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formBody
      });

      if (response.ok) {
        const data = await response.json();
        setToken(data.access_token);
        setUser({ username: loginData.username });
        localStorage.setItem('token', data.access_token);
        setLoginData({ username: '', password: '' });
        toast.success('Login successful!', { id: loadingToast });
        navigate('/');
      } else {
        toast.error('Invalid username or password', { id: loadingToast });
      }
    } catch (error) {
      console.error('Login error:', error);
      toast.error('Login failed. Please try again.', { id: loadingToast });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <IndianRupee className="w-16 h-16 text-blue-600 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-gray-800">Expense Tracker</h1>
          <p className="text-gray-600 mt-2">Manage your finances effortlessly</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Username</label>
            <input
              type="text"
              value={loginData.username}
              onChange={(e) => setLoginData({...loginData, username: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
            <input
              type="password"
              value={loginData.password}
              onChange={(e) => setLoginData({...loginData, password: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>
          <button type="submit" className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition font-semibold">
            Login
          </button>
          <div className="text-center">
            <Link to="/register" className="text-blue-600 hover:underline">
              Create new account
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}