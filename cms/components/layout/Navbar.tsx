'use client'

import { useState, useEffect } from 'react'
import { useTranslation } from '@/contexts/LanguageContext'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faMountain,
  faSearch,
  faBars,
  faCarrot,
  faWheatAwn,
  faCoffee,
  faHouseChimney,
  faSprayCanSparkles,
} from '@fortawesome/free-solid-svg-icons'
import { far } from '@fortawesome/free-regular-svg-icons'
import CartIcon from '@/components/cart/CartIcon'

export default function Navbar() {
  const { t } = useTranslation()
  const [isScrolled, setIsScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <>
      <nav
        className={`bg-white shadow-md sticky top-0 w-full z-50 transition-all duration-300 ${
          isScrolled ? 'shadow-lg' : ''
        }`}
        id="navbar"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20 gap-4">
            {/* Logo */}
            <div
              className="flex-shrink-0 flex items-center cursor-pointer min-w-fit"
              onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            >
              <FontAwesomeIcon
                icon={faMountain}
                className="text-brand-green text-3xl mr-2"
              />
              <div className="hidden sm:block">
                <h1 className="text-xl md:text-2xl font-bold text-brand-green tracking-wide font-serif">
                  Mountain Harvest
                </h1>
                <span className="text-[10px] text-brand-brown tracking-widest uppercase block text-center">
                  Nature's Best
                </span>
              </div>
            </div>

            {/* Search Box */}
            <div className="hidden md:flex flex-1 max-w-2xl mx-4 relative group">
              <div className="relative w-full">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none z-10">
                  <FontAwesomeIcon
                    icon={faSearch}
                    className="text-gray-400 group-focus-within:text-brand-green transition"
                  />
                </div>
                <input
                  type="text"
                  className="block w-full pl-10 pr-32 py-2.5 border border-gray-300 rounded-full leading-5 bg-gray-50 placeholder-gray-500 focus:outline-none focus:bg-white focus:border-brand-green focus:ring-1 focus:ring-brand-green sm:text-sm transition shadow-sm"
                  placeholder={t.search.placeholder}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                <div className="absolute inset-y-0 right-0 flex items-center">
                  <select className="h-full py-0 pl-2 pr-8 border-transparent bg-transparent text-gray-500 sm:text-sm rounded-r-md focus:ring-0 cursor-pointer hover:text-brand-green font-medium appearance-none">
                    <option>{t.search.all}</option>
                    <option>{t.search.agricultural}</option>
                    <option>{t.search.essentials}</option>
                  </select>
                  <button className="absolute right-1 top-1 bottom-1 bg-brand-green hover:bg-brand-darkGreen text-white px-4 rounded-full transition text-sm font-bold shadow-md hover:shadow-lg">
                    {t.search.button}
                  </button>
                </div>
              </div>
            </div>

            {/* Right Actions */}
            <div className="flex items-center space-x-6 text-gray-600">
              {/* User Account */}
              <div className="hidden md:flex flex-col items-center cursor-pointer hover:text-brand-green transition">
                <FontAwesomeIcon icon={far.faUser} className="text-xl mb-0.5" />
                <span className="text-[10px]">{t.nav.account}</span>
              </div>

              {/* Cart */}
              <CartIcon />

              {/* Mobile Menu Button */}
              <button
                id="mobile-menu-btn"
                className="md:hidden text-2xl text-gray-600 hover:text-brand-green transition"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                <FontAwesomeIcon icon={faBars} />
              </button>
            </div>
          </div>
        </div>

        {/* Category Bar */}
        <div className="hidden md:flex justify-center space-x-8 py-3 border-t border-gray-100 text-sm font-medium">
          <a href="#fresh-food" className="hover:text-brand-green transition flex items-center group">
            <FontAwesomeIcon icon={faCarrot} className="mr-1 group-hover:scale-110 transition" />
            <span>{t.nav.fresh}</span>
          </a>
          <a href="#dry-food" className="hover:text-brand-green transition flex items-center group">
            <FontAwesomeIcon icon={faWheatAwn} className="mr-1 group-hover:scale-110 transition" />
            <span>{t.nav.dry}</span>
          </a>
          <a href="#beverage" className="hover:text-brand-green transition flex items-center group">
            <FontAwesomeIcon icon={faCoffee} className="mr-1 group-hover:scale-110 transition" />
            <span>{t.nav.beverage}</span>
          </a>
          <div className="w-px h-4 bg-gray-300 my-auto"></div>
          <a href="#home-line" className="hover:text-brand-brown transition flex items-center group">
            <FontAwesomeIcon icon={faHouseChimney} className="mr-1 group-hover:scale-110 transition" />
            Home Line
          </a>
          <a href="#dhp" className="hover:text-brand-brown transition flex items-center group">
            <FontAwesomeIcon icon={faSprayCanSparkles} className="mr-1 group-hover:scale-110 transition" />
            <span>{t.nav.cosmetics}</span>
          </a>
        </div>
      </nav>

      {/* Mobile Menu Panel */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-t p-4">
          <input
            type="text"
            className="w-full border p-2 rounded mb-4"
            placeholder={t.search.placeholder}
          />
          <div className="space-y-2">
            <a href="#" className="block font-bold text-brand-green">
              {t.search.agricultural}
            </a>
            <div className="pl-4 space-y-1 text-sm text-gray-600">
              <a href="#" className="block">
                {t.nav.fresh}
              </a>
              <a href="#" className="block">
                {t.nav.dry}
              </a>
            </div>
            <a href="#" className="block font-bold text-brand-brown mt-2">
              {t.search.essentials}
            </a>
          </div>
        </div>
      )}
    </>
  )
}
