'use client'

import { useTranslation } from '@/contexts/LanguageContext'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faArrowRight } from '@fortawesome/free-solid-svg-icons'

export default function HeroBanner() {
  const { t } = useTranslation()

  return (
    <header className="relative h-[400px] md:h-[500px] flex items-center">
      <div className="absolute inset-0 z-0">
        <img
          src="https://images.unsplash.com/photo-1542838132-92c53300491e?ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80"
          alt="Market"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-black/70 to-transparent"></div>
      </div>
      <div className="relative z-10 max-w-7xl mx-auto px-4 w-full">
        <div className="max-w-xl text-white">
          <span className="bg-brand-orange text-white text-xs font-bold px-2 py-1 rounded uppercase mb-2 inline-block">
            {t.hero.promo}
          </span>
          <h1
            className="text-4xl md:text-5xl font-bold mb-4 leading-tight"
            dangerouslySetInnerHTML={{ __html: t.hero.title }}
          />
          <p className="text-gray-200 mb-6 text-lg">{t.hero.subtitle}</p>
          <a
            href="#shop"
            className="bg-brand-green hover:bg-brand-light text-white px-8 py-3 rounded-full font-bold transition shadow-lg inline-flex items-center"
          >
            <span>{t.hero.button}</span>
            <FontAwesomeIcon icon={faArrowRight} className="ml-2" />
          </a>
        </div>
      </div>
    </header>
  )
}
