'use client'

import { useEffect, useState } from 'react'
import { getFooterSettings, FooterSettings } from '@/lib/api'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faMountain,
  faMapMarkerAlt,
  faPhone,
  faEnvelope,
  faMoneyBillWave,
} from '@fortawesome/free-solid-svg-icons'
import {
  faFacebookF,
  faTiktok,
  faYoutube,
  faCcVisa,
  faCcMastercard,
} from '@fortawesome/free-brands-svg-icons'

export default function Footer() {
  const [settings, setSettings] = useState<FooterSettings | null>(null)

  useEffect(() => {
    getFooterSettings().then(setSettings).catch(console.error)
  }, [])

  const defaultSettings: FooterSettings = {
    company_name: 'Mountain Harvest',
    address: '123 Đường Mây Núi, Đà Lạt',
    phone: '1900 1234',
    email: 'cskh@mountainharvest.vn',
    social_links: {},
    footer_links: [],
    copyright_text: '© 2024 Mountain Harvest. Designed for E-commerce.',
  }

  const footerData = settings || defaultSettings

  return (
    <footer className="bg-brand-green text-white pt-16 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
          {/* Col 1 */}
          <div>
            <div className="flex items-center mb-4">
              <FontAwesomeIcon icon={faMountain} className="text-2xl mr-2" />
              <span className="text-2xl font-bold font-serif">
                {footerData.company_name}
              </span>
            </div>
            <p className="text-green-100 text-sm leading-relaxed mb-4">
              Hệ thống phân phối nông sản và nhu yếu phẩm thiên nhiên hàng đầu.
            </p>
            <div className="flex space-x-4">
              {footerData.social_links?.facebook && (
                <a
                  href={footerData.social_links.facebook}
                  className="text-white hover:text-brand-light transition"
                >
                  <FontAwesomeIcon icon={faFacebookF} />
                </a>
              )}
              {footerData.social_links?.tiktok && (
                <a
                  href={footerData.social_links.tiktok}
                  className="text-white hover:text-brand-light transition"
                >
                  <FontAwesomeIcon icon={faTiktok} />
                </a>
              )}
              {footerData.social_links?.youtube && (
                <a
                  href={footerData.social_links.youtube}
                  className="text-white hover:text-brand-light transition"
                >
                  <FontAwesomeIcon icon={faYoutube} />
                </a>
              )}
            </div>
          </div>

          {/* Col 2 */}
          <div>
            <h4 className="text-lg font-bold mb-4">Hỗ Trợ Khách Hàng</h4>
            <ul className="space-y-2 text-green-100 text-sm">
              <li>
                <a href="#" className="hover:text-white hover:underline">
                  Hướng dẫn mua hàng
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white hover:underline">
                  Chính sách giao hàng
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white hover:underline">
                  Đổi trả & Hoàn tiền
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white hover:underline">
                  Câu hỏi thường gặp
                </a>
              </li>
            </ul>
          </div>

          {/* Col 3: Contact */}
          <div>
            <h4 className="text-lg font-bold mb-4">Liên hệ</h4>
            <ul className="space-y-3 text-green-100 text-sm">
              {footerData.address && (
                <li className="flex items-start">
                  <FontAwesomeIcon icon={faMapMarkerAlt} className="mt-1 mr-2" />
                  {footerData.address}
                </li>
              )}
              {footerData.phone && (
                <li className="flex items-center">
                  <FontAwesomeIcon icon={faPhone} className="mr-2" />
                  {footerData.phone}
                </li>
              )}
              {footerData.email && (
                <li className="flex items-center">
                  <FontAwesomeIcon icon={faEnvelope} className="mr-2" />
                  {footerData.email}
                </li>
              )}
            </ul>
          </div>

          {/* Col 4: Payment */}
          <div>
            <h4 className="text-lg font-bold mb-4">Thanh Toán</h4>
            <div className="flex gap-2 text-2xl text-green-200">
              <FontAwesomeIcon icon={faCcVisa} />
              <FontAwesomeIcon icon={faCcMastercard} />
              <FontAwesomeIcon icon={faMoneyBillWave} />
            </div>
          </div>
        </div>

        <div className="border-t border-green-800 pt-8 text-center text-sm text-green-200">
          <p>{footerData.copyright_text}</p>
        </div>
      </div>
    </footer>
  )
}
