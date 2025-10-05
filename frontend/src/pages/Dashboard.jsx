import { useState, useEffect } from 'react';
import { IndianRupee, TrendingUp, TrendingDown, Plus, Download, LogOut, Edit2, Trash2 } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import toast from 'react-hot-toast';
import ConfirmDialog from '../components/ConfirmDialog';
import ExpenseForm from '../components/ExpenseForm';
import CategoryForm from '../components/CategoryForm';
import PdfOptions from '../components/PdfOptions';

const API_BASE = 'http://localhost:8000';

export default function Dashboard({ token, user, onLogout }) {
  const [expenses, setExpenses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [showExpenseForm, setShowExpenseForm] = useState(false);
  const [showCategoryForm, setShowCategoryForm] = useState(false);
  const [showPdfOptions, setShowPdfOptions] = useState(false);
  const [editingExpense, setEditingExpense] = useState(null);
  const [showLogoutDialog, setShowLogoutDialog] = useState(false);
  const [deleteExpenseId, setDeleteExpenseId] = useState(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  useEffect(() => {
    fetchData();
  }, [token]);

  useEffect(() => {
    if (!token) return;

    const payload = JSON.parse(atob(token.split('.')[1]));
    const expiresIn = payload.exp * 1000 - Date.now();

    if (expiresIn <= 0) {
      handleLogout();
    } else {
      const timer = setTimeout(() => handleLogout(), expiresIn);
      return () => clearTimeout(timer);
    }
  }, [token]);

  const fetchData = async () => {
    try {
      const [expensesRes, categoriesRes] = await Promise.all([
        fetch(`${API_BASE}/expenses`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_BASE}/categories`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      if (expensesRes.ok && categoriesRes.ok) {
        const expensesData = await expensesRes.json();
        const categoriesData = await categoriesRes.json();
        setExpenses(expensesData);
        setCategories(categoriesData);
      } else {
        toast.error('Failed to fetch data');
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Error loading data');
    }
  };

  const handleLogout = () => {
    onLogout();
    setShowLogoutDialog(false);
    toast.success('Logged out successfully');
  };

  const handleDeleteExpense = async (id) => {
    const loadingToast = toast.loading('Deleting transaction...');
    try {
      const response = await fetch(`${API_BASE}/expenses/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        setExpenses(prevExpenses => prevExpenses.filter(exp => exp.id !== id));
        toast.success('Transaction deleted!', { id: loadingToast });
      } else {
        toast.error('Failed to delete transaction', { id: loadingToast });
      }
    } catch (error) {
      console.error('Error deleting expense:', error);
      toast.error('Error deleting transaction', { id: loadingToast });
    } finally {
      setShowDeleteDialog(false);
      setDeleteExpenseId(null);
    }
  };

  const openDeleteDialog = (expenseId) => {
    setDeleteExpenseId(expenseId);
    setShowDeleteDialog(true);
  };

  const handleEditExpense = (expense) => {
    setEditingExpense(expense);
    setShowExpenseForm(true);
  };

  const downloadPDF = async (period) => {
    const loadingToast = toast.loading('Generating PDF...');
    try {
      const response = await fetch(`${API_BASE}/expenses/report/pdf?period=${period}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `expense_report_${period}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
        setShowPdfOptions(false);
        toast.success('PDF downloaded!', { id: loadingToast });
      } else {
        toast.error('Failed to generate PDF', { id: loadingToast });
      }
    } catch (error) {
      console.error('Error downloading PDF:', error);
      toast.error('Error downloading PDF', { id: loadingToast });
    }
  };

  const totalIncome = expenses.filter(e => e.type === 'income').reduce((sum, e) => sum + e.amount, 0);
  const totalExpense = expenses.filter(e => e.type === 'expense').reduce((sum, e) => sum + e.amount, 0);
  const balance = totalIncome - totalExpense;

  const categoryData = categories.map(cat => ({
    name: cat.name,
    value: expenses.filter(e => e.category_id === cat.id && e.type === 'expense').reduce((sum, e) => sum + e.amount, 0)
  })).filter(d => d.value > 0);

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto">
        <header className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <IndianRupee className="w-10 h-10 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-800">Expense Tracker</h1>
                <p className="text-gray-600">Welcome, {user?.username || 'User'}</p>
              </div>
            </div>
            <button onClick={() => setShowLogoutDialog(true)} className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition">
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Income</p>
                <p className="text-3xl font-bold text-green-600">₹{totalIncome.toFixed(2)}</p>
              </div>
              <TrendingUp className="w-12 h-12 text-green-600" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Expenses</p>
                <p className="text-3xl font-bold text-red-600">₹{totalExpense.toFixed(2)}</p>
              </div>
              <TrendingDown className="w-12 h-12 text-red-600" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Balance</p>
                <p className={`text-3xl font-bold ${balance >= 0 ? 'text-blue-600' : 'text-red-600'}`}>
                  ₹{balance.toFixed(2)}
                </p>
              </div>
              <IndianRupee className="w-12 h-12 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Category Breakdown</h2>
            {categoryData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `₹${value.toFixed(2)}`} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500 text-center py-12">No expense data available</p>
            )}
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Income vs Expenses</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={[
                { name: 'Income', amount: totalIncome },
                { name: 'Expenses', amount: totalExpense }
              ]}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => `₹${value.toFixed(2)}`} />
                <Bar dataKey="amount" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-gray-800">Recent Transactions</h2>
            <div className="flex gap-3 flex-wrap">
              <button
                onClick={() => setShowExpenseForm(true)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                <Plus className="w-4 h-4" />
                Add Transaction
              </button>
              <button
                onClick={() => setShowCategoryForm(true)}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
              >
                <Plus className="w-4 h-4" />
                Add Category
              </button>
              <button
                onClick={() => setShowPdfOptions(true)}
                className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
              >
                <Download className="w-4 h-4" />
                Download PDF
              </button>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Date</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Description</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Category</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Type</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Amount</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody>
                {expenses.slice(0, 10).map((expense) => (
                  <tr key={expense.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 text-gray-600">
                      {new Date(expense.date).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4 text-gray-800">{expense.description}</td>
                    <td className="py-3 px-4">
                      <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                        {expense.category.name}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-3 py-1 rounded-full text-sm ${
                        expense.type === 'income' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {expense.type}
                      </span>
                    </td>
                    <td className={`py-3 px-4 text-right font-semibold ${
                      expense.type === 'income' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      ₹{expense.amount.toFixed(2)}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleEditExpense(expense)}
                        className="text-blue-600 hover:text-blue-800 mr-3"
                      >
                        <Edit2 className="w-4 h-4 inline" />
                      </button>
                      <button
                        onClick={() => openDeleteDialog(expense.id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <Trash2 className="w-4 h-4 inline" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {expenses.length === 0 && (
              <p className="text-gray-500 text-center py-8">No transactions yet. Add your first transaction!</p>
            )}
          </div>
        </div>

        {/* Logout Confirmation Dialog */}
        <ConfirmDialog
          isOpen={showLogoutDialog}
          title="Logout Confirmation"
          message="Are you sure you want to log out?"
          onConfirm={handleLogout}
          onCancel={() => setShowLogoutDialog(false)}
        />

        {/* Delete Confirmation Dialog */}
        <ConfirmDialog
          isOpen={showDeleteDialog}
          title="Delete Confirmation"
          message="Do you really want to delete this transaction?"
          onConfirm={() => handleDeleteExpense(deleteExpenseId)}
          onCancel={() => {
            setShowDeleteDialog(false);
            setDeleteExpenseId(null);
          }}
        />

        {/* Expense Form Modal */}
        <ExpenseForm
          isOpen={showExpenseForm}
          editingExpense={editingExpense}
          categories={categories}
          token={token}
          onClose={() => {
            setShowExpenseForm(false);
            setEditingExpense(null);
          }}
          onSuccess={() => {
            setShowExpenseForm(false);
            setEditingExpense(null);
            fetchData();
          }}
        />

        {/* Category Form Modal */}
        <CategoryForm
          isOpen={showCategoryForm}
          token={token}
          onClose={() => setShowCategoryForm(false)}
          onSuccess={() => {
            setShowCategoryForm(false);
            fetchData();
          }}
        />

        {/* PDF Options Modal */}
        <PdfOptions
          isOpen={showPdfOptions}
          onClose={() => setShowPdfOptions(false)}
          onDownload={downloadPDF}
        />
      </div>
    </div>
  );
}