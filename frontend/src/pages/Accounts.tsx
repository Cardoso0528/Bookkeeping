import { useEffect, useState } from 'react';
import { Plus, Edit, Trash2, TrendingUp, TrendingDown } from 'lucide-react';
import { type Account, AccountType } from '../types';
import { accountApi } from '../services/api';

export default function Accounts() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      setLoading(true);
      // Mock data for demo
      const mockAccounts: Account[] = [
        {
          id: '1',
          tenantId: '1',
          accountName: 'Business Checking',
          accountType: AccountType.CHECKING,
          balance: 15420.50,
          currency: 'USD',
          isActive: true,
          description: 'Primary business checking account',
        },
        {
          id: '2',
          tenantId: '1',
          accountName: 'Savings Account',
          accountType: AccountType.SAVINGS,
          balance: 25000.00,
          currency: 'USD',
          isActive: true,
          description: 'Emergency fund and reserves',
        },
        {
          id: '3',
          tenantId: '1',
          accountName: 'Business Credit Card',
          accountType: AccountType.CREDIT_CARD,
          balance: -2350.75,
          currency: 'USD',
          isActive: true,
          description: 'Main business credit card',
        },
      ];

      setAccounts(mockAccounts);
    } catch (error) {
      console.error('Failed to load accounts:', error);
    } finally {
      setLoading(false);
    }
  };

  const getAccountTypeLabel = (type: AccountType) => {
    const labels = {
      [AccountType.CHECKING]: 'Checking',
      [AccountType.SAVINGS]: 'Savings',
      [AccountType.CREDIT_CARD]: 'Credit Card',
    };
    return labels[type];
  };

  const getAccountTypeColor = (type: AccountType) => {
    const colors = {
      [AccountType.CHECKING]: 'bg-blue-100 text-blue-800',
      [AccountType.SAVINGS]: 'bg-green-100 text-green-800',
      [AccountType.CREDIT_CARD]: 'bg-purple-100 text-purple-800',
    };
    return colors[type];
  };

  const totalBalance = accounts.reduce((sum, account) => sum + account.balance, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Accounts</h1>
          <p className="text-gray-500 mt-1">Manage your financial accounts</p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Add Account
        </button>
      </div>

      {/* Total Balance Card */}
      <div className="card bg-gradient-to-br from-primary-500 to-primary-700 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-primary-100 text-sm font-medium">Total Balance</p>
            <p className="text-4xl font-bold mt-2">
              ${totalBalance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </p>
            <p className="text-primary-100 text-sm mt-2">
              Across {accounts.filter((a) => a.isActive).length} active accounts
            </p>
          </div>
          <div className="p-4 bg-white/10 rounded-lg">
            {totalBalance >= 0 ? (
              <TrendingUp className="w-12 h-12" />
            ) : (
              <TrendingDown className="w-12 h-12" />
            )}
          </div>
        </div>
      </div>

      {/* Accounts Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading accounts...</div>
        </div>
      ) : accounts.length === 0 ? (
        <div className="card flex flex-col items-center justify-center h-64">
          <p className="text-gray-500 mb-4">No accounts found</p>
          <button className="btn-primary">Add your first account</button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {accounts.map((account) => (
            <div key={account.id} className="card hover:shadow-md transition-shadow">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {account.accountName}
                  </h3>
                  <span
                    className={`inline-block px-2 py-1 text-xs font-medium rounded-full mt-2 ${getAccountTypeColor(
                      account.accountType
                    )}`}
                  >
                    {getAccountTypeLabel(account.accountType)}
                  </span>
                </div>
                <div className="flex gap-1">
                  <button className="p-1 text-gray-400 hover:text-primary-600">
                    <Edit className="w-4 h-4" />
                  </button>
                  <button className="p-1 text-gray-400 hover:text-red-600">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Balance */}
              <div className="mb-4">
                <p className="text-sm text-gray-500">Current Balance</p>
                <p
                  className={`text-2xl font-bold mt-1 ${
                    account.balance >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {account.balance >= 0 ? '+' : ''}$
                  {Math.abs(account.balance).toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </p>
                <p className="text-xs text-gray-500 mt-1">{account.currency}</p>
              </div>

              {/* Description */}
              {account.description && (
                <p className="text-sm text-gray-600 line-clamp-2">{account.description}</p>
              )}

              {/* Status */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">Status</span>
                  <span
                    className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${
                      account.isActive
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {account.isActive ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <p className="text-sm text-gray-500 font-medium">Checking Accounts</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            $
            {accounts
              .filter((a) => a.accountType === AccountType.CHECKING)
              .reduce((sum, a) => sum + a.balance, 0)
              .toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500 font-medium">Savings Accounts</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            $
            {accounts
              .filter((a) => a.accountType === AccountType.SAVINGS)
              .reduce((sum, a) => sum + a.balance, 0)
              .toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500 font-medium">Credit Cards</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            $
            {accounts
              .filter((a) => a.accountType === AccountType.CREDIT_CARD)
              .reduce((sum, a) => sum + a.balance, 0)
              .toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </p>
        </div>
      </div>
    </div>
  );
}
