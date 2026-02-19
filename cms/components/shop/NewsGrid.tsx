'use client'

import { Article } from '@/lib/api'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faArrowRight } from '@fortawesome/free-solid-svg-icons'
import { far } from '@fortawesome/free-regular-svg-icons'

type NewsGridProps = {
  articles: Article[]
}

export default function NewsGrid({ articles }: NewsGridProps) {
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('vi-VN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      })
    } catch {
      return dateString
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {articles.map((article) => (
        <div
          key={article.id}
          className="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition"
        >
          <div className="h-48 overflow-hidden">
            <img
              src={article.image || '/placeholder.png'}
              alt={article.title}
              className="w-full h-full object-cover transform hover:scale-105 transition duration-500"
            />
          </div>
          <div className="p-6">
            <span className="text-xs text-gray-400 mb-2 block">
              <FontAwesomeIcon icon={far.faCalendarAlt} className="mr-1" />
              {formatDate(article.date)}
            </span>
            <h3 className="font-bold text-lg mb-2 hover:text-brand-green cursor-pointer">
              {article.title}
            </h3>
            <p className="text-gray-600 text-sm mb-4 line-clamp-3">{article.summary}</p>
            <button className="text-brand-green font-bold text-sm hover:underline">
              Đọc tiếp <FontAwesomeIcon icon={faArrowRight} className="text-xs ml-1" />
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
