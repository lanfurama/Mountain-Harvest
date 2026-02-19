'use client'

import { useState, useEffect } from 'react'

interface HeaderSettings {
  logo?: string | null
  phone?: string
  email?: string
  menu_items?: any[]
  search_placeholder?: string
}

export default function HeaderAdmin() {
  const [loading, setLoading] = useState(true)
  const [formData, setFormData] = useState<HeaderSettings>({
    logo: null,
    phone: '',
    email: '',
    menu_items: [],
    search_placeholder: 'Tìm sản phẩm...',
  })

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      const res = await fetch('/api/header')
      const data = await res.json()
      setFormData(data)
    } catch (error) {
      console.error('Error fetching header settings:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await fetch('/api/header', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      })
      alert('Đã lưu thành công!')
    } catch (error) {
      console.error('Error saving header settings:', error)
      alert('Có lỗi xảy ra!')
    }
  }

  if (loading) return <div>Loading...</div>

  return (
      <div className="bg-white shadow-xl rounded-xl border-2 border-green-100 p-6">
        <h2 className="text-2xl font-bold mb-6 text-gray-800 flex items-center gap-2">🎨 Cấu hình Header</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">URL Logo</label>
          <input
            type="url"
            value={formData.logo || ''}
            onChange={(e) => setFormData({ ...formData, logo: e.target.value || null })}
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Số điện thoại</label>
            <input
              type="text"
              value={formData.phone || ''}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              value={formData.email || ''}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
            />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Placeholder tìm kiếm</label>
          <input
            type="text"
            value={formData.search_placeholder || ''}
            onChange={(e) => setFormData({ ...formData, search_placeholder: e.target.value })}
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Menu Items (JSON)</label>
          <textarea
            value={JSON.stringify(formData.menu_items || [], null, 2)}
            onChange={(e) => {
              try {
                setFormData({ ...formData, menu_items: JSON.parse(e.target.value) })
              } catch {}
            }}
            className="w-full border rounded px-3 py-2 font-mono text-sm"
            rows={6}
          />
        </div>
        <button type="submit" className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl hover:from-green-700 hover:to-emerald-700 transition-all">
          💾 Lưu cấu hình
        </button>
      </form>
    </div>
  )
}
