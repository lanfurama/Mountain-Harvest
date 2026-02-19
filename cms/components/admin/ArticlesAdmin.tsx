'use client'

import { useState, useEffect } from 'react'

interface Article {
  id?: number
  title: string
  image?: string | null
  summary: string
  content: string
  is_published: boolean
}

export default function ArticlesAdmin() {
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState<Article | null>(null)
  const [formData, setFormData] = useState<Article>({
    title: '',
    image: null,
    summary: '',
    content: '',
    is_published: true,
  })

  useEffect(() => {
    fetchArticles()
  }, [])

  const fetchArticles = async () => {
    try {
      const res = await fetch('/api/articles')
      const data = await res.json()
      setArticles(data)
    } catch (error) {
      console.error('Error fetching articles:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editing) {
        await fetch(`/api/articles/${editing.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData),
        })
      } else {
        await fetch('/api/articles', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData),
        })
      }
      fetchArticles()
      setEditing(null)
      setFormData({
        title: '',
        image: null,
        summary: '',
        content: '',
        is_published: true,
      })
    } catch (error) {
      console.error('Error saving article:', error)
    }
  }

  const handleEdit = (article: Article) => {
    setEditing(article)
    setFormData(article)
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Bạn có chắc muốn xóa bài viết này?')) return
    try {
      await fetch(`/api/articles/${id}`, { method: 'DELETE' })
      fetchArticles()
    } catch (error) {
      console.error('Error deleting article:', error)
    }
  }

  if (loading) return <div>Loading...</div>

  return (
    <div className="space-y-6">
      <div className="bg-white shadow-xl rounded-xl border-2 border-green-100 p-6">
        <h2 className="text-2xl font-bold mb-6 text-gray-800 flex items-center gap-2">
          {editing ? '✏️ Sửa bài viết' : '➕ Thêm bài viết mới'}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Tiêu đề</label>
            <input
              type="text"
              required
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">URL hình ảnh</label>
            <input
              type="url"
              value={formData.image || ''}
              onChange={(e) => setFormData({ ...formData, image: e.target.value || null })}
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Tóm tắt</label>
            <textarea
              required
              value={formData.summary}
              onChange={(e) => setFormData({ ...formData, summary: e.target.value })}
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
              rows={3}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Nội dung</label>
            <textarea
              required
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition"
              rows={10}
            />
          </div>
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={formData.is_published}
              onChange={(e) => setFormData({ ...formData, is_published: e.target.checked })}
              className="mr-2"
            />
            <label className="text-sm font-medium">Đã xuất bản</label>
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl hover:from-green-700 hover:to-emerald-700 transition-all"
            >
              {editing ? 'Cập nhật' : 'Thêm mới'}
            </button>
            {editing && (
              <button
                type="button"
                onClick={() => {
                  setEditing(null)
                  setFormData({
                    title: '',
                    image: null,
                    summary: '',
                    content: '',
                    is_published: true,
                  })
                }}
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
              >
                Hủy
              </button>
            )}
          </div>
        </form>
      </div>

      <div className="bg-white shadow-xl rounded-xl border-2 border-green-100 overflow-hidden">
        <div className="px-6 py-4 bg-gradient-to-r from-green-600 to-emerald-600">
          <h2 className="text-xl font-bold text-white">📝 Danh sách bài viết ({articles.length})</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tiêu đề</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Xuất bản</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {articles.map((article) => (
                <tr key={article.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{article.id}</td>
                  <td className="px-6 py-4 text-sm font-medium">{article.title}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{article.is_published ? '✓' : ''}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => handleEdit(article)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      Sửa
                    </button>
                    <button
                      onClick={() => handleDelete(article.id!)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Xóa
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
