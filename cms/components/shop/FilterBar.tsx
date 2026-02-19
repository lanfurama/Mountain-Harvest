'use client'

import { useState } from 'react'
import { useTranslation } from '@/contexts/LanguageContext'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faFilter, faChevronDown, faTimes } from '@fortawesome/free-solid-svg-icons'

export default function FilterBar() {
  const { t } = useTranslation()
  const [selectedFilters, setSelectedFilters] = useState<string[]>([])

  const removeFilter = (filter: string) => {
    setSelectedFilters((prev) => prev.filter((f) => f !== filter))
  }

  return (
    <section className="mb-12">
      <div className="sticky top-24 z-30">
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-4 md:p-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            {/* Title */}
            <div className="flex items-center gap-2 text-brand-green font-bold text-lg">
              <FontAwesomeIcon icon={faFilter} />
              <span>{t.filter.title}</span>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap gap-3 flex-1 md:justify-end">
              {/* Category Filter */}
              <div className="relative">
                <select className="appearance-none bg-gray-50 border border-gray-200 text-gray-700 py-2 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-brand-green text-sm font-medium">
                  <option>Danh mục: Tất cả</option>
                  <option>Rau củ quả</option>
                  <option>Hạt & Ngũ cốc</option>
                  <option>Gia dụng</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                  <FontAwesomeIcon icon={faChevronDown} className="text-xs" />
                </div>
              </div>

              {/* Price Filter */}
              <div className="relative">
                <select className="appearance-none bg-gray-50 border border-gray-200 text-gray-700 py-2 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-brand-green text-sm font-medium">
                  <option>Mức giá: Tất cả</option>
                  <option>Dưới 50.000đ</option>
                  <option>50.000đ - 200.000đ</option>
                  <option>Trên 200.000đ</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                  <FontAwesomeIcon icon={faChevronDown} className="text-xs" />
                </div>
              </div>

              {/* Origin Filter */}
              <div className="relative">
                <select className="appearance-none bg-gray-50 border border-gray-200 text-gray-700 py-2 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-brand-green text-sm font-medium">
                  <option>Tiêu chuẩn: Tất cả</option>
                  <option>Organic</option>
                  <option>VietGAP</option>
                  <option>Handmade</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                  <FontAwesomeIcon icon={faChevronDown} className="text-xs" />
                </div>
              </div>

              {/* Sort */}
              <div className="relative">
                <select className="appearance-none bg-gray-50 border border-gray-200 text-gray-700 py-2 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-brand-green text-sm font-medium">
                  <option>Sắp xếp: Mặc định</option>
                  <option>Giá: Thấp đến cao</option>
                  <option>Giá: Cao đến thấp</option>
                  <option>Đánh giá cao nhất</option>
                  <option>Mới nhất</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                  <FontAwesomeIcon icon={faChevronDown} className="text-xs" />
                </div>
              </div>
            </div>
          </div>

          {/* Active Filters */}
          {selectedFilters.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-gray-100">
              {selectedFilters.map((filter) => (
                <span
                  key={filter}
                  className="bg-brand-green/10 text-brand-green px-3 py-1 rounded-full text-xs font-medium flex items-center gap-2"
                >
                  {filter}
                  <button
                    onClick={() => removeFilter(filter)}
                    className="hover:text-brand-darkGreen"
                  >
                    <FontAwesomeIcon icon={faTimes} />
                  </button>
                </span>
              ))}
              <span className="text-gray-400 px-2 py-1 cursor-pointer hover:text-red-500">
                Xoá tất cả
              </span>
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
