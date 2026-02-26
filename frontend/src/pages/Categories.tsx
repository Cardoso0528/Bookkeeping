import { useEffect, useState } from 'react';
import { Plus, Edit, Trash2, FolderTree, Shield } from 'lucide-react';
import type { Category } from '../types';
import { categoryApi } from '../services/api';

export default function Categories() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      setLoading(true);
      // Mock data for demo
      const mockCategories: Category[] = [
        {
          id: '1',
          tenantId: '1',
          categoryName: 'Revenue',
          isSystemDefault: true,
          isTaxDeductible: false,
          description: 'Income from sales and services',
        },
        {
          id: '2',
          tenantId: '1',
          categoryName: 'Office Expenses',
          isSystemDefault: true,
          isTaxDeductible: true,
          description: 'General office supplies and equipment',
        },
        {
          id: '3',
          tenantId: '1',
          categoryName: 'Software & Subscriptions',
          isSystemDefault: false,
          isTaxDeductible: true,
          description: 'Software licenses and online subscriptions',
        },
        {
          id: '4',
          tenantId: '1',
          categoryName: 'Marketing',
          isSystemDefault: true,
          isTaxDeductible: true,
          description: 'Advertising and marketing expenses',
        },
        {
          id: '5',
          tenantId: '1',
          categoryName: 'Travel',
          isSystemDefault: true,
          isTaxDeductible: true,
          description: 'Business travel and accommodation',
        },
        {
          id: '6',
          tenantId: '1',
          categoryName: 'Meals & Entertainment',
          isSystemDefault: true,
          isTaxDeductible: true,
          description: 'Business meals and entertainment',
        },
        {
          id: '7',
          tenantId: '1',
          categoryName: 'Professional Services',
          isSystemDefault: false,
          isTaxDeductible: true,
          description: 'Legal, accounting, and consulting fees',
        },
        {
          id: '8',
          tenantId: '1',
          categoryName: 'Utilities',
          isSystemDefault: true,
          isTaxDeductible: true,
          description: 'Electricity, internet, phone bills',
        },
      ];

      setCategories(mockCategories);
    } catch (error) {
      console.error('Failed to load categories:', error);
    } finally {
      setLoading(false);
    }
  };

  const taxDeductibleCategories = categories.filter((c) => c.isTaxDeductible);
  const customCategories = categories.filter((c) => !c.isSystemDefault);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Categories</h1>
          <p className="text-gray-500 mt-1">Organize your transactions with categories</p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Add Category
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-primary-100 rounded-lg">
              <FolderTree className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500 font-medium">Total Categories</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{categories.length}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <Shield className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500 font-medium">Tax Deductible</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {taxDeductibleCategories.length}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Edit className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500 font-medium">Custom Categories</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {customCategories.length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Categories List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading categories...</div>
        </div>
      ) : categories.length === 0 ? (
        <div className="card flex flex-col items-center justify-center h-64">
          <p className="text-gray-500 mb-4">No categories found</p>
          <button className="btn-primary">Add your first category</button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {categories.map((category) => (
            <div
              key={category.id}
              className="card hover:shadow-md transition-shadow group"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="text-base font-semibold text-gray-900 flex items-center gap-2">
                    {category.categoryName}
                    {category.isSystemDefault && (
                      <span className="inline-flex items-center px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">
                        System
                      </span>
                    )}
                  </h3>
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button className="p-1 text-gray-400 hover:text-primary-600">
                    <Edit className="w-4 h-4" />
                  </button>
                  {!category.isSystemDefault && (
                    <button className="p-1 text-gray-400 hover:text-red-600">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>

              {/* Description */}
              {category.description && (
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                  {category.description}
                </p>
              )}

              {/* Footer */}
              <div className="flex items-center justify-between pt-3 border-t border-gray-200">
                <div className="flex items-center gap-2">
                  {category.isTaxDeductible && (
                    <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                      Tax Deductible
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Info Card */}
      <div className="card bg-blue-50 border-blue-200">
        <div className="flex gap-4">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <FolderTree className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-gray-900 mb-1">
              About Categories
            </h3>
            <p className="text-sm text-gray-600">
              Categories help you organize your transactions and track spending patterns.
              System categories cannot be deleted, but you can create custom categories
              tailored to your business needs. Mark categories as tax-deductible to easily
              identify deductible expenses at tax time.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
