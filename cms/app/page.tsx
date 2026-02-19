'use client'

import { useEffect, useState } from 'react'
import { Product, Article, getProducts, getArticles } from '@/lib/api'
import TopBar from '@/components/layout/TopBar'
import Navbar from '@/components/layout/Navbar'
import HeroBanner from '@/components/shop/HeroBanner'
import FilterBar from '@/components/shop/FilterBar'
import ProductGrid from '@/components/shop/ProductGrid'
import ProductModal from '@/components/shop/ProductModal'
import CategoryBrochures from '@/components/shop/CategoryBrochures'
import Newsletter from '@/components/shop/Newsletter'
import NewsGrid from '@/components/shop/NewsGrid'
import Footer from '@/components/layout/Footer'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faArrowRight } from '@fortawesome/free-solid-svg-icons'

export default function Home() {
  const [products, setProducts] = useState<Product[]>([])
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  useEffect(() => {
    const loadData = async () => {
      try {
        const [productsData, articlesData] = await Promise.all([
          getProducts(),
          getArticles(),
        ])
        setProducts(productsData)
        setArticles(articlesData)
      } catch (error) {
        console.error('Error loading data:', error)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  const handleProductClick = (product: Product) => {
    setSelectedProduct(product)
    setIsModalOpen(true)
  }

  return (
    <div className="min-h-screen">
      <TopBar />
      <Navbar />
      <HeroBanner />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12" id="shop">
        <FilterBar />

        {/* PRODUCT SHOWCASE GRID */}
        <section className="mb-16">
          <div className="flex justify-between items-end mb-8">
            <div>
              <h2 className="text-3xl font-bold text-gray-800" data-i18n="products.featured">
                Sản Phẩm Nổi Bật
              </h2>
              <p className="text-gray-500 mt-2" data-i18n="products.subtitle">
                Best selection from Mountain Harvest farm
              </p>
            </div>
            <a href="#" className="text-brand-green font-bold hover:underline">
              <span data-i18n="products.viewAll">View All</span>{' '}
              <FontAwesomeIcon icon={faArrowRight} className="text-xs" />
            </a>
          </div>

          {loading ? (
            <div className="text-center py-12 text-gray-500">Đang tải sản phẩm...</div>
          ) : products.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              Chưa có sản phẩm nào trong hệ thống.
            </div>
          ) : (
            <ProductGrid products={products} onProductClick={handleProductClick} />
          )}
        </section>

        {/* CATEGORY BROCHURE */}
        <CategoryBrochures />

        {/* Newsletter */}
        <Newsletter />

        {/* News Section */}
        <section className="mb-16">
          <div className="flex justify-between items-end mb-8">
            <div>
              <h2 className="text-3xl font-bold text-gray-800">Tin Tức & Cập Nhật</h2>
              <p className="text-gray-500 mt-2">Cập nhật mới nhất từ Mountain Harvest</p>
            </div>
          </div>

          {loading ? (
            <div className="text-center py-8 text-gray-500">Đang tải bài viết...</div>
          ) : articles.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Chưa có bài viết nào trong hệ thống.
            </div>
          ) : (
            <NewsGrid articles={articles.slice(0, 6)} />
          )}
        </section>
      </main>

      <Footer />

      <ProductModal
        product={selectedProduct}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedProduct(null)
        }}
      />
    </div>
  )
}
