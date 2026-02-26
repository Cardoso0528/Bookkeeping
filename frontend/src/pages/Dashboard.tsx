import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  TrendingUp,
  TrendingDown,
  Wallet,
  AlertCircle,
  ArrowRight,
} from 'lucide-react';
import type { DashboardStats, Transaction } from '../types';
import { dashboardApi, transactionApi } from '../services/api';
import { format } from 'date-fns';

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      // For demo purposes, using mock data
      // Replace with actual API calls when backend is ready
      const mockStats: DashboardStats = {
        totalIncome: 45000,
        totalExpenses: 32500,
        netIncome: 12500,
        uncategorizedCount: 5,
        accountsCount: 3,
        categoriesCount: 12,
      };
      
      const mockTransactions: Transaction[] = [
        {
          id: '1',
          tenantId: '1',
          accountId: '1',
          transactionDate: new Date().toISOString(),
          amount: 1250.00,
          transactionType: 'CREDIT',
          description: 'Client Payment',
          merchantName: 'ABC Corp',
          isTaxDeductible: false,
        },
        {
          id: '2',
          tenantId: '1',
          accountId: '1',
          transactionDate: new Date(Date.now() - 86400000).toISOString(),
          amount: 85.50,
          transactionType: 'DEBIT',
          description: 'Office Supplies',
          merchantName: 'Office Depot',
          isTaxDeductible: true,
          categoryId: '1',
        },
      ];

      setStats(mockStats);
      setRecentTransactions(mockTransactions);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">Welcome back! Here's your financial overview.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Income */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Income</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                ${stats?.totalIncome.toLocaleString()}
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        {/* Total Expenses */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Expenses</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                ${stats?.totalExpenses.toLocaleString()}
              </p>
            </div>
            <div className="p-3 bg-red-100 rounded-lg">
              <TrendingDown className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>

        {/* Net Income */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Net Income</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                ${stats?.netIncome.toLocaleString()}
              </p>
            </div>
            <div className="p-3 bg-primary-100 rounded-lg">
              <Wallet className="w-6 h-6 text-primary-600" />
            </div>
          </div>
        </div>

        {/* Uncategorized */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Uncategorized</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {stats?.uncategorizedCount}
              </p>
            </div>
            <div className="p-3 bg-yellow-100 rounded-lg">
              <AlertCircle className="w-6 h-6 text-yellow-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Recent Transactions</h2>
          <Link
            to="/transactions"
            className="flex items-center text-sm text-primary-600 hover:text-primary-700"
          >
            View all
            <ArrowRight className="w-4 h-4 ml-1" />
          </Link>
        </div>

        <div className="space-y-3">
          {recentTransactions.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No transactions yet</p>
          ) : (
            recentTransactions.map((transaction) => (
              <div
                key={transaction.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex-1">
                  <p className="font-medium text-gray-900">
                    {transaction.description || 'No description'}
                  </p>
                  <p className="text-sm text-gray-500">
                    {transaction.merchantName} • {format(new Date(transaction.transactionDate), 'MMM d, yyyy')}
                  </p>
                </div>
                <div className="text-right">
                  <p
                    className={`font-semibold ${
                      transaction.transactionType === 'CREDIT'
                        ? 'text-green-600'
                        : 'text-red-600'
                    }`}
                  >
                    {transaction.transactionType === 'CREDIT' ? '+' : '-'}$
                    {transaction.amount.toFixed(2)}
                  </p>
                  {transaction.categoryId && (
                    <span className="inline-block px-2 py-1 text-xs bg-gray-200 text-gray-700 rounded mt-1">
                      Categorized
                    </span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
