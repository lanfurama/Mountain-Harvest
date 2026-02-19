'use client'

import { useState, useEffect } from 'react'

interface FooterSettings {
  company_name?: string
  address?: string
  phone?: string
  email?: string
  social_links?: Record<string, string>
  footer_links?: any[]
  copyright_text?: string
}

export default function FooterAdmin() {
  const [loading, setLoading] = useState(true)
  const [formData, setFormData] = useState<FooterSettings>({
    company_name: 'Mountain Harvest',
    address: '',
    phone: '',
    email: '',
    social_links: {},
    footer_links: [],
    copyright_text: '© 2024 Mountain Harvest. Designed for E-commerce.',
  })

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      const res = await fetch('/api/footer')
      const data = await res.json()
      setFormData(data)
    } catch (error) {
      console.error('Error fetching footer settings:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await fetch('/api/footer', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      })
      alert('Đã lưu thành công!')
    } catch (error) {
      console.error('Error saving footer settings:', error)
      alert('Có lỗi xảy ra!')
    }
  }

  if (loading) return <div>Loading...</div>

  return (
      <div className="bg-white shadow-xl rounded-xl border-2 border-green-100 p-6">
        <h2 className="text-2xl font-bold mb-6 text-gray-800 flex items-center gap-2">🔗 Cấu hình Footer</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Tên công ty</label>
          <input
            type="text"
            value={formData.company_name || ''}
            onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Địa chỉ</label>
          <textarea
            value={formData.address || ''}
            onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
            rows={2}
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
          <label className="block text-sm font-medium mb-1">Social Links (JSON)</label>
          <textarea
            value={JSON.stringify(formData.social_links || {}, null, 2)}
            onChange={(e) => {
              try {
                setFormData({ ...formData, social_links: JSON.parse(e.target.value) })
              } catch {}
            }}
            className="w-full border rounded px-3 py-2 font-mono text-sm"
            rows={4}
            placeholder='{"facebook": "url", "tiktok": "url", "youtube": "url"}'
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Footer Links (JSON)</label>
          <textarea
            value={JSON.stringify(formData.footer_links || [], null, 2)}
            onChange={(e) => {
              try {
                setFormData({ ...formData, footer_links: JSON.parse(e.target.value) })
              } catch {}
            }}
            className="w-full border rounded px-3 py-2 font-mono text-sm"
            rows={6}
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Copyright Text</label>
          <input
            type="text"
            value={formData.copyright_text || ''}
            onChange={(e) => setFormData({ ...formData, copyright_text: e.target.value })}
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
          />
        </div>
        <button type="submit" className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl hover:from-green-700 hover:to-emerald-700 transition-all">
          💾 Lưu cấu hình
        </button>
      </form>
    </div>
  )
}
