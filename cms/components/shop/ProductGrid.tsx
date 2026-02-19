'use client'

import { Product } from '@/lib/api'
import { useCart } from '@/contexts/CartContext'
import { useToast } from '@/components/ui/Toast'
import { useTranslation } from '@/contexts/LanguageContext'
import { formatCurrency } from '@/lib/utils'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faEye,
  faCartPlus,
  faStar,
  faStarHalfAlt,
} from '@fortawesome/free-solid-svg-icons'
import { far } from '@fortawesome/free-regular-svg-icons'

type ProductGridProps = {
  products: Product[]
  onProductClick: (product: Product) => void
}

export default function ProductGrid({ products, onProductClick }: ProductGridProps) {
  const { addToCart } = useCart()
  const { showToast } = useToast()
  const { t } = useTranslation()

  const handleAddToCart = (product: Product) => {
    addToCart({
      id: product.id,
      name: product.name,
      category: product.category,
      price: product.price,
      original_price: product.original_price,
      image: product.image,
      rating: product.rating,
      reviews: product.reviews,
      is_hot: product.is_hot,
      discount: product.discount,
      tags: product.tags,
      description: product.description,
      unit: product.unit,
    })
    showToast(`${t.toast.addedToCart}: "${product.name}"`)
  }

  const renderStars = (rating: number) => {
    return Array(5)
      .fill(0)
      .map((_, i) => {
        if (i < Math.floor(rating)) {
          return <FontAwesomeIcon key={i} icon={faStar} className="text-yellow-400" />
        } else if (i < rating) {
          return <FontAwesomeIcon key={i} icon={faStarHalfAlt} className="text-yellow-400" />
        } else {
          return <FontAwesomeIcon key={i} icon={far.faStar} className="text-yellow-400" />
        }
      })
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {products.map((product) => (
        <div
          key={product.id}
          className="bg-white rounded-xl shadow-sm hover:shadow-xl transition duration-300 group overflow-hidden border border-gray-100"
        >
          <div className="relative h-64 overflow-hidden">
            {product.discount && (
              <span className="absolute top-3 left-3 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded z-10">
                {product.discount}
              </span>
            )}
            {product.tags &&
              product.tags
                .split(',')
                .filter((tag) => tag.trim())
                .map((tag, idx) => {
                  const trimmedTag = tag.trim()
                  let colorClass = 'bg-blue-100 text-blue-600'
                  if (trimmedTag === 'Best Seller') colorClass = 'bg-brand-orange text-white'
                  if (trimmedTag === 'Organic') colorClass = 'bg-green-100 text-brand-green'
                  return (
                    <span
                      key={idx}
                      className={`absolute top-3 right-3 ${colorClass} text-xs font-bold px-2 py-1 rounded z-10 mr-1`}
                    >
                      {trimmedTag}
                    </span>
                  )
                })}

            <img
              src={product.image || '/placeholder.png'}
              alt={product.name}
              className="w-full h-full object-cover transform group-hover:scale-110 transition duration-500"
            />

            <div className="absolute bottom-0 left-0 right-0 bg-white/90 p-2 translate-y-full group-hover:translate-y-0 transition duration-300 flex justify-center gap-2 backdrop-blur-sm">
              <button
                onClick={() => onProductClick(product)}
                className="p-2 rounded-full bg-gray-100 hover:bg-brand-green hover:text-white transition"
                title="Xem nhanh"
              >
                <FontAwesomeIcon icon={faEye} />
              </button>
            </div>
          </div>
          <div className="p-4">
            <div className="text-xs text-gray-500 mb-1">{product.category}</div>
            <h3
              className="font-bold text-lg text-gray-800 hover:text-brand-green cursor-pointer truncate"
              onClick={() => onProductClick(product)}
            >
              {product.name}
            </h3>
            <div className="flex items-center my-2">
              <div className="flex text-yellow-400 text-xs">{renderStars(product.rating)}</div>
              <span className="text-xs text-gray-400 ml-2">({product.reviews} đánh giá)</span>
            </div>
            <div className="flex justify-between items-center mt-3">
              <div>
                <span className="text-lg font-bold text-brand-green">
                  {formatCurrency(product.price)}
                </span>
                {product.original_price && (
                  <span className="text-sm text-gray-400 line-through ml-2">
                    {formatCurrency(product.original_price)}
                  </span>
                )}
                {product.unit && (
                  <span className="text-xs text-gray-500">{product.unit}</span>
                )}
              </div>
              <button
                onClick={() => handleAddToCart(product)}
                className="bg-brand-green text-white p-2 rounded-lg hover:bg-brand-darkGreen transition shadow-lg shadow-green-200"
              >
                <FontAwesomeIcon icon={faCartPlus} />
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
