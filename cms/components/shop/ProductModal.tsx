'use client'

import { useState } from 'react'
import { Product } from '@/lib/api'
import { useCart } from '@/contexts/CartContext'
import { useToast } from '@/components/ui/Toast'
import { useTranslation } from '@/contexts/LanguageContext'
import { formatCurrency } from '@/lib/utils'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faTimes,
  faStar,
  faStarHalfAlt,
  faHeart,
} from '@fortawesome/free-solid-svg-icons'
import { far } from '@fortawesome/free-regular-svg-icons'

type ProductModalProps = {
  product: Product | null
  isOpen: boolean
  onClose: () => void
}

export default function ProductModal({ product, isOpen, onClose }: ProductModalProps) {
  const { addToCart } = useCart()
  const { showToast } = useToast()
  const { t } = useTranslation()
  const [quantity, setQuantity] = useState(1)

  if (!isOpen || !product) return null

  const handleAddToCart = () => {
    for (let i = 0; i < quantity; i++) {
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
    }
    showToast(`${t.toast.addedToCart}: "${product.name}"`)
    onClose()
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
    <div
      className="fixed inset-0 z-[100]"
      onClick={onClose}
    >
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity"></div>
      <div className="absolute inset-0 flex items-center justify-center p-4">
        <div
          className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl p-6 md:p-8 relative"
          onClick={(e) => e.stopPropagation()}
        >
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-2xl z-10"
          >
            <FontAwesomeIcon icon={faTimes} />
          </button>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="h-64 md:h-full rounded-lg overflow-hidden">
              <img
                src={product.image || '/placeholder.png'}
                alt={product.name}
                className="w-full h-full object-cover"
              />
            </div>
            <div>
              <span className="text-sm text-brand-green font-bold bg-green-100 px-2 py-1 rounded-full">
                {product.category}
              </span>
              <h2 className="text-2xl font-bold text-gray-800 mt-2 mb-2 font-serif">
                {product.name}
              </h2>
              <div className="flex items-center mb-4">
                <div className="flex text-yellow-400 text-sm">{renderStars(product.rating)}</div>
                <span className="text-sm text-gray-500 ml-2">
                  ({product.reviews} đánh giá)
                </span>
              </div>

              <div className="text-3xl font-bold text-brand-green mb-4">
                {formatCurrency(product.price)}
                {product.unit && (
                  <span className="text-base font-normal text-gray-500">
                    {' '}
                    {product.unit}
                  </span>
                )}
              </div>

              <p className="text-gray-600 mb-6 leading-relaxed">{product.description}</p>

              <div className="flex gap-4">
                <div className="inline-flex items-center border border-gray-300 rounded-lg">
                  <button
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    className="px-3 py-2 hover:bg-gray-100 text-gray-600 font-bold"
                  >
                    -
                  </button>
                  <input
                    type="text"
                    value={quantity}
                    onChange={(e) => {
                      const val = parseInt(e.target.value) || 1
                      setQuantity(Math.max(1, val))
                    }}
                    className="w-12 text-center border-none focus:ring-0 text-sm font-bold"
                  />
                  <button
                    onClick={() => setQuantity(quantity + 1)}
                    className="px-3 py-2 hover:bg-gray-100 text-gray-600 font-bold"
                  >
                    +
                  </button>
                </div>
                <button
                  onClick={handleAddToCart}
                  className="flex-1 bg-brand-green text-white py-2 rounded-lg font-bold hover:bg-brand-darkGreen transition shadow-lg shadow-green-200"
                >
                  Thêm vào giỏ
                </button>
                <button className="p-3 border border-gray-300 rounded-lg text-gray-500 hover:text-red-500 hover:border-red-500 transition">
                  <FontAwesomeIcon icon={far.faHeart} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
