export type Product = {
  id: number
  name: string
  category: string
  price: number
  original_price?: number | null
  image?: string | null
  rating: number
  reviews: number
  is_hot: boolean
  discount?: string | null
  tags?: string | null
  description: string
  unit?: string | null
}

export type Article = {
  id: number
  title: string
  image?: string | null
  summary: string
  content: string
  date: string
  is_published: boolean
}

export type HeaderSettings = {
  logo?: string | null
  phone?: string
  email?: string
  menu_items?: any[]
  search_placeholder?: string
}

export type FooterSettings = {
  company_name?: string
  address?: string
  phone?: string
  email?: string
  social_links?: Record<string, string>
  footer_links?: any[]
  copyright_text?: string
}

type ProductFilters = {
  category?: string
  is_hot?: boolean
  min_price?: number
  max_price?: number
  tags?: string
}

export async function getProducts(filters?: ProductFilters): Promise<Product[]> {
  const params = new URLSearchParams()
  if (filters?.category) params.append('category', filters.category)
  if (filters?.is_hot) params.append('is_hot', 'true')
  
  const url = `/api/products${params.toString() ? `?${params.toString()}` : ''}`
  const res = await fetch(url)
  if (!res.ok) throw new Error('Failed to fetch products')
  const data = await res.json()
  
  // Client-side filtering for price and tags
  let filtered = Array.isArray(data) ? data : []
  if (filters?.min_price) {
    filtered = filtered.filter((p: Product) => p.price >= filters.min_price!)
  }
  if (filters?.max_price) {
    filtered = filtered.filter((p: Product) => p.price <= filters.max_price!)
  }
  if (filters?.tags) {
    const tagList = filters.tags.split(',').map(t => t.trim())
    filtered = filtered.filter((p: Product) => {
      const productTags = p.tags?.split(',').map(t => t.trim()) || []
      return tagList.some(tag => productTags.includes(tag))
    })
  }
  
  return filtered
}

export async function getArticles(): Promise<Article[]> {
  const res = await fetch('/api/articles')
  if (!res.ok) throw new Error('Failed to fetch articles')
  const data = await res.json()
  return Array.isArray(data) ? data : []
}

export async function getHeaderSettings(): Promise<HeaderSettings> {
  const res = await fetch('/api/header')
  if (!res.ok) throw new Error('Failed to fetch header settings')
  return await res.json()
}

export async function getFooterSettings(): Promise<FooterSettings> {
  const res = await fetch('/api/footer')
  if (!res.ok) throw new Error('Failed to fetch footer settings')
  return await res.json()
}
