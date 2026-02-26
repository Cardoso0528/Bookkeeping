export enum TransactionType {
  DEBIT = 'DEBIT',
  CREDIT = 'CREDIT'
}

export enum AccountType {
  CHECKING = 'CHECKING',
  SAVINGS = 'SAVINGS',
  CREDIT_CARD = 'CREDIT_CARD'
}

export enum BusinessType {
  RESTAURANT = 'RESTAURANT',
  RETAIL = 'RETAIL',
  SERVICE = 'SERVICE',
  TECH = 'TECH',
  OTHER = 'OTHER'
}

export interface Transaction {
  id: string;
  tenantId: string;
  accountId: string;
  transactionDate: string;
  amount: number;
  transactionType: TransactionType;
  categoryId?: string;
  description?: string;
  merchantName?: string;
  isTaxDeductible: boolean;
  confidenceScore?: number;
  source?: string;
  notes?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface Account {
  id: string;
  tenantId: string;
  accountName: string;
  accountType: AccountType;
  balance: number;
  currency: string;
  isActive: boolean;
  description?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface Category {
  id: string;
  tenantId: string;
  categoryName: string;
  businessType?: BusinessType;
  parentCategoryId?: string;
  isSystemDefault: boolean;
  isTaxDeductible: boolean;
  description?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface Tenant {
  id: string;
  tenantName: string;
  businessType: BusinessType;
  createdAt?: string;
  updatedAt?: string;
}

export interface DashboardStats {
  totalIncome: number;
  totalExpenses: number;
  netIncome: number;
  uncategorizedCount: number;
  accountsCount: number;
  categoriesCount: number;
}

export interface TransactionFilters {
  startDate?: string;
  endDate?: string;
  accountId?: string;
  categoryId?: string;
  transactionType?: TransactionType;
  searchQuery?: string;
}
