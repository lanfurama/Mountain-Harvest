'use client'

import { useTranslation } from '@/contexts/LanguageContext'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faTruck } from '@fortawesome/free-solid-svg-icons'

export default function TopBar() {
  const { t, language, setLanguage } = useTranslation()

  return (
    <div 
      className="text-white text-xs py-2 px-4 hidden md:block"
      style={{ backgroundColor: '#2F5233' }}
    >
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <span className="flex items-center text-white">
          <FontAwesomeIcon icon={faTruck} className="mr-2 text-white" />
          <span className="text-white">{t.topbar.freeShipping}</span>
        </span>
        <div className="flex items-center space-x-4">
          <a href="#" className="text-white hover:text-brand-light transition">
            {t.topbar.hotline}
          </a>
          <a href="#" className="text-white hover:text-brand-light transition">
            {t.topbar.support}
          </a>
          <div className="flex items-center gap-2 border-l border-white/30 pl-4">
            <button
              onClick={() => setLanguage('en')}
              className={`px-2 py-1 rounded hover:bg-white/20 transition font-medium text-white ${
                language === 'en' ? 'bg-white/20' : ''
              }`}
            >
              EN
            </button>
            <span className="text-white/50">|</span>
            <button
              onClick={() => setLanguage('vi')}
              className={`px-2 py-1 rounded hover:bg-white/20 transition font-medium text-white ${
                language === 'vi' ? 'bg-white/20' : ''
              }`}
            >
              VI
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
