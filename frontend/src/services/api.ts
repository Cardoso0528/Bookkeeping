import type {
  Transaction,
  Account,
  Category,
  DashboardStats,
  TransactionFilters
} from '../types';
import { tokenStorage } from './auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api';

async function apiCall<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const accessToken = tokenStorage.getAccessToken();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options?.headers as Record<string, string>),
  };

  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // Token expired — clear state and redirect to login
    tokenStorage.clear();
    window.location.href = '/login';
    throw new Error('Session expired. Please sign in again.');
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    throw new Error(errorBody?.message || `API Error: ${response.statusText}`);
  }

  return response.json();
}

// Transaction API
export const transactionApi = {
  getAll: (filters?: TransactionFilters) => {
    const params = new URLSearchParams();
    if (filters?.startDate) params.append('startDate', filters.startDate);
    if (filters?.endDate) params.append('endDate', filters.endDate);
    if (filters?.accountId) params.append('accountId', filters.accountId);
    if (filters?.categoryId) params.append('categoryId', filters.categoryId);
    if (filters?.transactionType) params.append('type', filters.transactionType);
    
    const query = params.toString();
    return apiCall<Transaction[]>(`/transactions${query ? `?${query}` : ''}`);
  },

  getById: (id: string) => 
    apiCall<Transaction>(`/transactions/${id}`),

  create: (transaction: Omit<Transaction, 'id' | 'createdAt' | 'updatedAt'>) =>
    apiCall<Transaction>('/transactions', {
      method: 'POST',
      body: JSON.stringify(transaction),
    }),

  update: (id: string, transaction: Partial<Transaction>) =>
    apiCall<Transaction>(`/transactions/${id}`, {
      method: 'PUT',
      body: JSON.stringify(transaction),
    }),

  delete: (id: string) =>
    apiCall<void>(`/transactions/${id}`, { method: 'DELETE' }),

  getUncategorized: () =>
    apiCall<Transaction[]>('/transactions/uncategorized'),
};

// Account API
export const accountApi = {
  getAll: () => apiCall<Account[]>('/accounts'),

  getById: (id: string) => apiCall<Account>(`/accounts/${id}`),

  create: (account: Omit<Account, 'id' | 'createdAt' | 'updatedAt'>) =>
    apiCall<Account>('/accounts', {
      method: 'POST',
      body: JSON.stringify(account),
    }),

  update: (id: string, account: Partial<Account>) =>
    apiCall<Account>(`/accounts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(account),
    }),

  delete: (id: string) =>
    apiCall<void>(`/accounts/${id}`, { method: 'DELETE' }),
};

// Category API
export const categoryApi = {
  getAll: () => apiCall<Category[]>('/categories'),

  getById: (id: string) => apiCall<Category>(`/categories/${id}`),

  create: (category: Omit<Category, 'id' | 'createdAt' | 'updatedAt'>) =>
    apiCall<Category>('/categories', {
      method: 'POST',
      body: JSON.stringify(category),
    }),

  update: (id: string, category: Partial<Category>) =>
    apiCall<Category>(`/categories/${id}`, {
      method: 'PUT',
      body: JSON.stringify(category),
    }),

  delete: (id: string) =>
    apiCall<void>(`/categories/${id}`, { method: 'DELETE' }),
};

// Dashboard API
export const dashboardApi = {
  getStats: (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams();
    if (startDate) params.append('startDate', startDate);
    if (endDate) params.append('endDate', endDate);
    
    const query = params.toString();
    return apiCall<DashboardStats>(`/dashboard/stats${query ? `?${query}` : ''}`);
  },
};
