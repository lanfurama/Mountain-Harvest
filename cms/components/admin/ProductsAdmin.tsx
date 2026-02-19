'use client'

import { useState, useEffect } from 'react'

interface Product {
  id?: number
  name: string
  category: string
  price: number
  original_price?: number | null
  image?: string | null
  rating: number
  reviews: number
  is_hot: boolean
  discount?: string | null
  tags?: string
  description: string
  unit?: string | null
}

export default function ProductsAdmin() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState<Product | null>(null)
  const [formData, setFormData] = useState<Product>({
    name: '',
    category: '',
    price: 0,
    original_price: null,
    image: null,
    rating: 0,
    reviews: 0,
    is_hot: false,
    discount: null,
    tags: '',
    description: '',
    unit: null,
  })

  useEffect(() => {
    fetchProducts()
  }, [])

  const fetchProducts = async () => {
    try {
      const res = await fetch('/api/products')
      const data = await res.json()
      setProducts(data)
    } catch (error) {
      console.error('Error fetching products:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editing) {
        await fetch(`/api/products/${editing.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData),
        })
      } else {
        await fetch('/api/products', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData),
        })
      }
      fetchProducts()
      setEditing(null)
      setFormData({
        name: '',
        category: '',
        price: 0,
        original_price: null,
        image: null,
        rating: 0,
        reviews: 0,
        is_hot: false,
        discount: null,
        tags: '',
        description: '',
        unit: null,
      })
    } catch (error) {
      console.error('Error saving product:', error)
    }
  }

  const handleEdit = (product: Product) => {
    setEditing(product)
    setFormData(product)
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Bạn có chắc muốn xóa sản phẩm này?')) return
    try {
      await fetch(`/api/products/${id}`, { method: 'DELETE' })
      fetchProducts()
    } catch (error) {
      console.error('Error deleting product:', error)
    }
  }

  if (loading) return <div className="text-center py-12 text-gray-500">Đang tải...</div>

  return (
    <div className="space-y-6">
      <div className="bg-white shadow-xl rounded-xl border-2 border-green-100 p-6">
        <h2 className="text-2xl font-bold mb-6 text-gray-800 flex items-center gap-2">
          {editing ? '✏️ Sửa sản phẩm' : '➕ Thêm sản phẩm mới'}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-2 text-gray-700">Tên sản phẩm</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2 text-gray-700">Danh mục</label>
              <input
                type="text"
                required
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2 text-gray-700">Giá</label>
              <input
                type="number"
                required
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: Number(e.target.value) })}
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2 text-gray-700">Giá gốc</label>
              <input
                type="number"
                value={formData.original_price || ''}
                onChange={(e) =>
                  setFormData({ ...formData, original_price: e.target.value ? Number(e.target.value) : null })
                }
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2 text-gray-700">URL hình ảnh</label>
              <input
                type="url"
                value={formData.image || ''}
                onChange={(e) => setFormData({ ...formData, image: e.target.value || null })}
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2 text-gray-700">Đơn vị</label>
              <input
                type="text"
                value={formData.unit || ''}
                onChange={(e) => setFormData({ ...formData, unit: e.target.value || null })}
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2 text-gray-700">Đánh giá</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="5"
                value={formData.rating}
                onChange={(e) => setFormData({ ...formData, rating: Number(e.target.value) })}
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2 text-gray-700">Số đánh giá</label>
              <input
                type="number"
                value={formData.reviews}
                onChange={(e) => setFormData({ ...formData, reviews: Number(e.target.value) })}
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2 text-gray-700">Giảm giá</label>
              <input
                type="text"
                value={formData.discount || ''}
                onChange={(e) => setFormData({ ...formData, discount: e.target.value || null })}
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
                placeholder="VD: -15%"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2 text-gray-700">Tags</label>
              <input
                type="text"
                value={formData.tags || ''}
                onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
                placeholder="Các tag cách nhau bởi dấu phẩy"
              />
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={formData.is_hot}
                onChange={(e) => setFormData({ ...formData, is_hot: e.target.checked })}
                className="mr-2"
              />
              <label className="text-sm font-medium">Sản phẩm hot</label>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Mô tả</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full border rounded px-3 py-2"
              rows={4}
            />
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl hover:from-green-700 hover:to-emerald-700 transition-all"
            >
              {editing ? '💾 Cập nhật' : '➕ Thêm mới'}
            </button>
            {editing && (
              <button
                type="button"
                onClick={() => {
                  setEditing(null)
                  setFormData({
                    name: '',
                    category: '',
                    price: 0,
                    original_price: null,
                    image: null,
                    rating: 0,
                    reviews: 0,
                    is_hot: false,
                    discount: null,
                    tags: '',
                    description: '',
                    unit: null,
                  })
                }}
                className="bg-gray-200 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-300 transition"
              >
                ❌ Hủy
              </button>
            )}
          </div>
        </form>
      </div>

      <div className="bg-white shadow-xl rounded-xl border-2 border-green-100 overflow-hidden">
        <div className="px-6 py-4 bg-gradient-to-r from-green-600 to-emerald-600">
          <h2 className="text-xl font-bold text-white">📦 Danh sách sản phẩm ({products.length})</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-green-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Tên</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Danh mục</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Giá</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Hot</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {products.map((product) => (
                <tr key={product.id} className="hover:bg-green-50/50 transition">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-600">{product.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">{product.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{product.category}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-green-600">{product.price.toLocaleString()}đ</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{product.is_hot ? <span className="bg-red-100 text-red-600 px-2 py-1 rounded-full text-xs font-semibold">🔥 Hot</span> : ''}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => handleEdit(product)}
                      className="bg-blue-500 text-white px-3 py-1.5 rounded-lg hover:bg-blue-600 mr-2 transition font-medium"
                    >
                      ✏️ Sửa
                    </button>
                    <button
                      onClick={() => handleDelete(product.id!)}
                      className="bg-red-500 text-white px-3 py-1.5 rounded-lg hover:bg-red-600 transition font-medium"
                    >
                      🗑️ Xóa
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
