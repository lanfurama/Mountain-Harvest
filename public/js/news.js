/**
 * Mountain Harvest - News Management
 */

const NEWS_PER_PAGE = 6;
let newsData = [];
let newsPage = 1, newsTotal = 0, newsTotalPages = 0;
let newsLoading = false;

function showNewsLoading() {
  const container = document.getElementById('news-list');
  if (!container) return;
  container.innerHTML = Array(NEWS_PER_PAGE).fill(0).map(() => `
    <div class="skeleton-card">
      <div class="skeleton skeleton-image" style="height: 12rem;"></div>
      <div class="skeleton skeleton-text" style="width: 40%; margin-top: 1rem;"></div>
      <div class="skeleton skeleton-text" style="margin-top: 0.5rem;"></div>
      <div class="skeleton skeleton-text skeleton-text-sm" style="margin-top: 0.5rem;"></div>
    </div>
  `).join('');
}

async function loadNews(page) {
  page = page || 1;
  if (newsLoading) return;
  newsLoading = true;
  
  showNewsLoading();
  setNewsPaginationLoading(true);
  
  try {
    const res = await fetch('/api/news?page=' + page + '&limit=' + NEWS_PER_PAGE);
    const data = res.ok ? await res.json() : {};
    newsData = Array.isArray(data.items) ? data.items : [];
    newsTotal = typeof data.total === 'number' ? data.total : newsData.length;
    newsPage = typeof data.page === 'number' ? data.page : 1;
    const limit = typeof data.limit === 'number' ? data.limit : NEWS_PER_PAGE;
    newsTotalPages = typeof data.totalPages === 'number' ? data.totalPages : Math.max(1, Math.ceil(newsTotal / limit));
  } catch (e) {
    console.warn('News API failed', e);
    newsData = [];
    newsTotal = 0;
    newsPage = 1;
    newsTotalPages = 1;
  } finally {
    newsLoading = false;
    setNewsPaginationLoading(false);
  }
  
  renderNews();
  renderNewsPagination();
}

function setNewsPaginationLoading(loading) {
  const pagination = document.getElementById('news-pagination');
  if (!pagination) return;
  if (loading) {
    pagination.classList.add('pagination-loading');
  } else {
    pagination.classList.remove('pagination-loading');
  }
}

function renderNewsPagination() {
  const el = document.getElementById('news-pagination');
  if (!el) return;
  if (newsTotalPages <= 1) {
    el.innerHTML = '';
    return;
  }
  const prevDisabled = newsPage <= 1 || newsLoading ? ' opacity-50 pointer-events-none' : '';
  const nextDisabled = newsPage >= newsTotalPages || newsLoading ? ' opacity-50 pointer-events-none' : '';
  
  let html = '<a href="#" data-page="prev" class="inline-flex items-center justify-center w-9 h-9 border border-gray-300 rounded-lg hover:bg-gray-100 text-gray-700 transition' + prevDisabled + '"><i class="fas fa-chevron-left"></i></a>';
  for (let p = 1; p <= newsTotalPages; p++) {
    const active = p === newsPage ? ' bg-brand-green text-white border-brand-green' : ' border-gray-300 hover:bg-gray-100 text-gray-700';
    const disabled = newsLoading && p !== newsPage ? ' opacity-50 pointer-events-none' : '';
    html += '<a href="#" data-page="' + p + '" class="inline-flex items-center justify-center w-9 h-9 border rounded-lg transition' + active + disabled + '">' + p + '</a>';
  }
  html += '<a href="#" data-page="next" class="inline-flex items-center justify-center w-9 h-9 border border-gray-300 rounded-lg hover:bg-gray-100 text-gray-700 transition' + nextDisabled + '"><i class="fas fa-chevron-right"></i></a>';
  el.innerHTML = html;
  el.querySelectorAll('a[data-page]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      if (newsLoading) return;
      const v = a.getAttribute('data-page');
      if (v === 'prev') loadNews(newsPage - 1);
      else if (v === 'next') loadNews(newsPage + 1);
      else loadNews(parseInt(v, 10));
    });
  });
}

function dateToIso(dateStr) {
  if (!dateStr || typeof dateStr !== 'string') return '';
  const s = dateStr.trim();
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return s;
  const m = s.match(/^(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})$/);
  if (m) {
    const d = parseInt(m[1], 10), M = parseInt(m[2], 10), y = m[3];
    if (d <= 31 && M <= 12) return y + '-' + String(M).padStart(2, '0') + '-' + String(d).padStart(2, '0');
  }
  return '';
}


function renderNews() {
  const container = document.getElementById('news-list');
  if (!container) return;
  const list = Array.isArray(newsData) ? newsData : [];

  container.innerHTML = list.map(news => {
    const titleEscaped = (news.title || '').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    let contentPreview = '';
    if (news.content) {
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = news.content;
      contentPreview = tempDiv.textContent || tempDiv.innerText || '';
      contentPreview = contentPreview.replace(/&nbsp;/g, ' ').trim().replace(/\s+/g, ' ').substring(0, 150);
      if (contentPreview.length >= 150) contentPreview += '...';
      contentPreview = contentPreview.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }
    return `
    <article class="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition">
        <div class="h-48 overflow-hidden">
            <img src="${news.image || ''}" alt="${titleEscaped}" class="w-full h-full object-cover transform hover:scale-105 transition duration-500" onerror="handleImageError(this)">
        </div>
        <div class="p-6">
            <span class="text-xs text-gray-400 mb-2 block"><i class="far fa-calendar-alt mr-1"></i> ${news.date || ''}</span>
            <h3 class="font-bold text-lg mb-2"><a href="/news/${news.id}" class="hover:text-brand-green cursor-pointer block" style="text-decoration: none;">${titleEscaped}</a></h3>
            <p class="text-gray-600 text-sm mb-4 line-clamp-3">${contentPreview}</p>
        </div>
    </article>
    `;
  }).join('');
}
