'use client'

import { useState } from 'react'
import { useTranslation } from '@/contexts/LanguageContext'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faLeaf, faLemon } from '@fortawesome/free-solid-svg-icons'

export default function Newsletter() {
  const { t } = useTranslation()
  const [email, setEmail] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle newsletter subscription
    console.log('Subscribe:', email)
    setEmail('')
  }

  return (
    <section className="bg-brand-light/20 rounded-3xl p-8 md:p-12 text-center mb-16 relative overflow-hidden">
      <FontAwesomeIcon
        icon={faLeaf}
        className="text-brand-light/20 text-9xl absolute -top-10 -left-10 transform -rotate-12"
      />
      <FontAwesomeIcon
        icon={faLemon}
        className="text-brand-light/20 text-9xl absolute -bottom-10 -right-10 transform rotate-12"
      />

      <div className="relative z-10 max-w-2xl mx-auto">
        <h2 className="text-3xl font-bold text-brand-green mb-4">{t.newsletter.title}</h2>
        <p className="text-gray-600 mb-8">{t.newsletter.subtitle}</p>
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
          <input
            type="email"
            placeholder={t.newsletter.placeholder}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="flex-1 py-3 px-5 rounded-full border border-gray-300 focus:outline-none focus:border-brand-green"
          />
          <button
            type="submit"
            className="bg-brand-green text-white py-3 px-8 rounded-full font-bold hover:bg-green-800 transition"
          >
            {t.newsletter.button}
          </button>
        </form>
      </div>
    </section>
  )
}
