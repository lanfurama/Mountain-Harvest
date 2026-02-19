'use client'

import { useState } from 'react'
import ProductsAdmin from '@/components/admin/ProductsAdmin'
import ArticlesAdmin from '@/components/admin/ArticlesAdmin'
import HeaderAdmin from '@/components/admin/HeaderAdmin'
import FooterAdmin from '@/components/admin/FooterAdmin'

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState<'products' | 'articles' | 'header' | 'footer'>('products')

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-50">
      <div className="bg-white shadow-lg border-b-2 border-green-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-green-600 to-emerald-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">M</span>
              </div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                Mountain Harvest CMS
              </h1>
            </div>
          </div>
          <div className="flex space-x-2 border-t border-gray-200">
            <button
              onClick={() => setActiveTab('products')}
              className={`px-6 py-3 text-sm font-semibold transition-all ${
                activeTab === 'products'
                  ? 'border-b-3 border-green-600 text-green-600 bg-green-50'
                  : 'text-gray-600 hover:text-green-600 hover:bg-green-50/50'
              }`}
            >
              📦 Sản phẩm
            </button>
            <button
              onClick={() => setActiveTab('articles')}
              className={`px-6 py-3 text-sm font-semibold transition-all ${
                activeTab === 'articles'
                  ? 'border-b-3 border-green-600 text-green-600 bg-green-50'
                  : 'text-gray-600 hover:text-green-600 hover:bg-green-50/50'
              }`}
            >
              📝 Bài viết
            </button>
            <button
              onClick={() => setActiveTab('header')}
              className={`px-6 py-3 text-sm font-semibold transition-all ${
                activeTab === 'header'
                  ? 'border-b-3 border-green-600 text-green-600 bg-green-50'
                  : 'text-gray-600 hover:text-green-600 hover:bg-green-50/50'
              }`}
            >
              🎨 Header
            </button>
            <button
              onClick={() => setActiveTab('footer')}
              className={`px-6 py-3 text-sm font-semibold transition-all ${
                activeTab === 'footer'
                  ? 'border-b-3 border-green-600 text-green-600 bg-green-50'
                  : 'text-gray-600 hover:text-green-600 hover:bg-green-50/50'
              }`}
            >
              🔗 Footer
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'products' && <ProductsAdmin />}
        {activeTab === 'articles' && <ArticlesAdmin />}
        {activeTab === 'header' && <HeaderAdmin />}
        {activeTab === 'footer' && <FooterAdmin />}
      </div>
    </div>
  )
}
