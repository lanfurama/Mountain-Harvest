'use client'

import { useTranslation } from '@/contexts/LanguageContext'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCarrot } from '@fortawesome/free-solid-svg-icons'

export default function CategoryBrochures() {
  const { t } = useTranslation()

  return (
    <section className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
      <div className="relative rounded-2xl overflow-hidden h-80 group cursor-pointer">
        <img
          src="https://images.unsplash.com/photo-1542838132-92c53300491e?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80"
          alt="Nông Sản Tươi"
          className="absolute inset-0 w-full h-full object-cover transition duration-500 group-hover:scale-105"
        />
        <div className="absolute inset-0 bg-black/40 hover:bg-black/30 transition"></div>
        <div className="absolute inset-0 flex flex-col justify-center items-center text-center p-8">
          <h3 className="text-3xl font-bold text-white mb-2 font-serif">
            {t.category.fresh.title}
          </h3>
          <p className="text-gray-200 mb-6 max-w-sm">{t.category.fresh.desc}</p>
          <button className="bg-white text-brand-green px-6 py-2 rounded-full font-bold hover:bg-brand-green hover:text-white transition">
            {t.category.fresh.button}
          </button>
        </div>
      </div>

      <div className="relative rounded-2xl overflow-hidden h-80 group cursor-pointer">
        <img
          src="https://images.unsplash.com/photo-1556911220-e15b29be8c8f?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80"
          alt="Nhu Yếu Phẩm"
          className="absolute inset-0 w-full h-full object-cover transition duration-500 group-hover:scale-105"
        />
        <div className="absolute inset-0 bg-black/40 hover:bg-black/30 transition"></div>
        <div className="absolute inset-0 flex flex-col justify-center items-center text-center p-8">
          <h3 className="text-3xl font-bold text-white mb-2 font-serif">
            {t.category.essentials.title}
          </h3>
          <p className="text-gray-200 mb-6 max-w-sm">{t.category.essentials.desc}</p>
          <button className="bg-white text-brand-brown px-6 py-2 rounded-full font-bold hover:bg-brand-brown hover:text-white transition">
            {t.category.essentials.button}
          </button>
        </div>
      </div>
    </section>
  )
}
