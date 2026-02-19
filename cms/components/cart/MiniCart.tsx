'use client'

import { useCart } from '@/contexts/CartContext'
import { useTranslation } from '@/contexts/LanguageContext'
import { formatCurrency } from '@/lib/utils'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faTimes } from '@fortawesome/free-solid-svg-icons'

export default function MiniCart() {
  const { cart, removeFromCart, getTotal } = useCart()
  const { t } = useTranslation()

  return (
    <div className="w-72 bg-white rounded-lg shadow-xl border border-gray-100 p-4">
      <h4 className="text-sm font-bold text-gray-700 mb-3 border-b pb-2">
        {t.cart.title}
      </h4>
      <div className="space-y-3 mb-4 max-h-48 overflow-y-auto custom-scrollbar">
        {cart.length === 0 ? (
          <div className="text-center text-gray-500 py-4 text-sm">{t.cart.empty}</div>
        ) : (
          cart.map((item) => (
            <div key={item.id} className="flex gap-2 group relative">
              <img
                src={item.image || '/placeholder.png'}
                alt={item.name}
                className="w-12 h-12 object-cover rounded"
              />
              <div className="flex-1">
                <div className="text-xs font-bold truncate">{item.name}</div>
                <div className="text-xs text-gray-500">
                  {item.quantity} x {formatCurrency(item.price)}
                </div>
              </div>
              <button
                onClick={() => removeFromCart(item.id)}
                className="text-gray-400 hover:text-red-500 absolute right-0 top-1"
              >
                <FontAwesomeIcon icon={faTimes} />
              </button>
            </div>
          ))
        )}
      </div>
      <div className="flex justify-between text-sm font-bold mb-3 text-brand-green">
        <span>{t.cart.total}</span>
        <span>{formatCurrency(getTotal())}</span>
      </div>
      <button className="w-full bg-brand-brown text-white py-2 rounded text-sm hover:bg-gray-800 transition">
        {t.cart.checkout}
      </button>
    </div>
  )
}
