'use client'

import { useCart } from '@/contexts/CartContext'
import { useTranslation } from '@/contexts/LanguageContext'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faShoppingBasket } from '@fortawesome/free-solid-svg-icons'
import MiniCart from './MiniCart'

export default function CartIcon() {
  const { getItemCount } = useCart()
  const { t } = useTranslation()
  const count = getItemCount()

  return (
    <div className="relative group cursor-pointer hover:text-brand-green">
      <div className="flex flex-col items-center">
        <div className="relative">
          <FontAwesomeIcon icon={faShoppingBasket} className="text-xl" />
          {count > 0 && (
            <span className={`absolute -top-2 -right-2 bg-brand-orange text-white text-[10px] font-bold rounded-full h-4 w-4 flex items-center justify-center animate-bounce ${count === 0 ? 'hidden' : ''}`}>
              {count}
            </span>
          )}
        </div>
        <span className="text-[10px] mt-1 hidden md:block">{t.nav.cart}</span>
      </div>

      {/* Mini Cart Preview (Hover) */}
      <div className="absolute right-0 top-full pt-2 hidden group-hover:block z-50">
        <MiniCart />
      </div>
    </div>
  )
}
