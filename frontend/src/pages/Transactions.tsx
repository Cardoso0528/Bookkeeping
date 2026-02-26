import { useEffect, useState } from 'react';
import {
  Plus,
  Search,
  Filter,
  Download,
  Edit,
  Trash2,
  Calendar,
} from 'lucide-react';
import { type Transaction, TransactionType, type Account, type Category } from '../types';
import { transactionApi, accountApi, categoryApi } from '../services/api';
import { format } from 'date-fns';

export default function Transactions() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterOpen, setFilterOpen] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);

  // Filters
  const [selectedAccount, setSelectedAccount] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      // Mock data for demo
      const mockTransactions: Transaction[] = [
        {
          id: '1',
          tenantId: '1',
          accountId: '1',
          transactionDate: '2026-02-10',
          amount: 1250.00,
          transactionType: TransactionType.CREDIT,
          description: 'Client Payment - Project Alpha',
          merchantName: 'ABC Corp',
          isTaxDeductible: false,
          categoryId: '1',
          source: 'MANUAL',
        },
        {
          id: '2',
          tenantId: '1',
          accountId: '1',
          transactionDate: '2026-02-09',
          amount: 85.50,
          transactionType: TransactionType.DEBIT,
          description: 'Office Supplies',
          merchantName: 'Office Depot',
          isTaxDeductible: true,
          categoryId: '2',
          source: 'BANK_IMPORT',
        },
        {
          id: '3',
          tenantId: '1',
          accountId: '2',
          transactionDate: '2026-02-08',
          amount: 45.00,
          transactionType: TransactionType.DEBIT,
          description: 'Software Subscription',
          merchantName: 'Adobe',
          isTaxDeductible: true,
          source: 'MANUAL',
        },
      ];

      const mockAccounts: Account[] = [
        { id: '1', tenantId: '1', accountName: 'Business Checking', accountType: 'CHECKING', balance: 15000, currency: 'USD', isActive: true },
        { id: '2', tenantId: '1', accountName: 'Savings', accountType: 'SAVINGS', balance: 25000, currency: 'USD', isActive: true },
      ];

      const mockCategories: Category[] = [
        { id: '1', tenantId: '1', categoryName: 'Revenue', isSystemDefault: true, isTaxDeductible: false },
        { id: '2', tenantId: '1', categoryName: 'Office Expenses', isSystemDefault: true, isTaxDeductible: true },
        { id: '3', tenantId: '1', categoryName: 'Software', isSystemDefault: false, isTaxDeductible: true },
      ];

      setTransactions(mockTransactions);
      setAccounts(mockAccounts);
      setCategories(mockCategories);
    } catch (error) {
      console.error('Failed to load transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredTransactions = transactions.filter((transaction) => {
    const matchesSearch =
      !searchQuery ||
      transaction.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      transaction.merchantName?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesAccount = !selectedAccount || transaction.accountId === selectedAccount;
    const matchesCategory = !selectedCategory || transaction.categoryId === selectedCategory;
    const matchesType = !selectedType || transaction.transactionType === selectedType;
    
    return matchesSearch && matchesAccount && matchesCategory && matchesType;
  });

  const getCategoryName = (categoryId?: string) => {
    return categories.find((c) => c.id === categoryId)?.categoryName || 'Uncategorized';
  };

  const getAccountName = (accountId: string) => {
    return accounts.find((a) => a.id === accountId)?.accountName || 'Unknown';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Transactions</h1>
          <p className="text-gray-500 mt-1">Manage your financial transactions</p>
        </div>
        <div className="flex gap-3">
          <button className="btn-secondary flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="btn-primary flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add Transaction
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="card">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search transactions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input pl-10"
            />
          </div>

          {/* Filter Toggle */}
          <button
            onClick={() => setFilterOpen(!filterOpen)}
            className="btn-secondary flex items-center gap-2"
          >
            <Filter className="w-4 h-4" />
            Filters
          </button>
        </div>

        {/* Expanded Filters */}
        {filterOpen && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-4 pt-4 border-t border-gray-200">
            <div>
              <label className="label">Account</label>
              <select
                value={selectedAccount}
                onChange={(e) => setSelectedAccount(e.target.value)}
                className="input"
              >
                <option value="">All Accounts</option>
                {accounts.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.accountName}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="label">Category</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="input"
              >
                <option value="">All Categories</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.categoryName}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="label">Type</label>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="input"
              >
                <option value="">All Types</option>
                <option value="CREDIT">Income</option>
                <option value="DEBIT">Expense</option>
              </select>
            </div>

            <div>
              <label className="label">Date Range</label>
              <div className="flex gap-2">
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="input"
                  placeholder="Start"
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Transactions Table */}
      <div className="card overflow-hidden p-0">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-500">Loading transactions...</div>
          </div>
        ) : filteredTransactions.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64">
            <p className="text-gray-500">No transactions found</p>
            <button
              onClick={() => setShowAddModal(true)}
              className="btn-primary mt-4"
            >
              Add your first transaction
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Account
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredTransactions.map((transaction) => (
                  <tr key={transaction.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {format(new Date(transaction.transactionDate), 'MMM d, yyyy')}
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {transaction.description}
                        </p>
                        {transaction.merchantName && (
                          <p className="text-sm text-gray-500">{transaction.merchantName}</p>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {getAccountName(transaction.accountId)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                          transaction.categoryId
                            ? 'bg-primary-100 text-primary-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {getCategoryName(transaction.categoryId)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                          transaction.transactionType === 'CREDIT'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {transaction.transactionType === 'CREDIT' ? 'Income' : 'Expense'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium">
                      <span
                        className={
                          transaction.transactionType === 'CREDIT'
                            ? 'text-green-600'
                            : 'text-red-600'
                        }
                      >
                        {transaction.transactionType === 'CREDIT' ? '+' : '-'}$
                        {transaction.amount.toFixed(2)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                      <div className="flex justify-end gap-2">
                        <button className="p-1 text-gray-400 hover:text-primary-600">
                          <Edit className="w-4 h-4" />
                        </button>
                        <button className="p-1 text-gray-400 hover:text-red-600">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card bg-green-50 border-green-200">
          <p className="text-sm text-green-600 font-medium">Total Income</p>
          <p className="text-2xl font-bold text-green-700 mt-1">
            $
            {filteredTransactions
              .filter((t) => t.transactionType === 'CREDIT')
              .reduce((sum, t) => sum + t.amount, 0)
              .toFixed(2)}
          </p>
        </div>
        <div className="card bg-red-50 border-red-200">
          <p className="text-sm text-red-600 font-medium">Total Expenses</p>
          <p className="text-2xl font-bold text-red-700 mt-1">
            $
            {filteredTransactions
              .filter((t) => t.transactionType === 'DEBIT')
              .reduce((sum, t) => sum + t.amount, 0)
              .toFixed(2)}
          </p>
        </div>
        <div className="card bg-primary-50 border-primary-200">
          <p className="text-sm text-primary-600 font-medium">Net</p>
          <p className="text-2xl font-bold text-primary-700 mt-1">
            $
            {(
              filteredTransactions
                .filter((t) => t.transactionType === 'CREDIT')
                .reduce((sum, t) => sum + t.amount, 0) -
              filteredTransactions
                .filter((t) => t.transactionType === 'DEBIT')
                .reduce((sum, t) => sum + t.amount, 0)
            ).toFixed(2)}
          </p>
        </div>
      </div>
    </div>
  );
}
