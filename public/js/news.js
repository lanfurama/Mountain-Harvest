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

function updateNewsSEO(news) {
  const title = news.title || 'Mountain Harvest';
  const description = news.content ? news.content.replace(/<[^>]*>/g, '').substring(0, 160) : 'Tin tức từ Mountain Harvest';
  const image = news.image || '';
  const siteUrl = window.location.origin;
  const currentUrl = window.location.href;

  // Update document title
  document.title = title + ' - Mountain Harvest';

  // Update or create meta tags
  function setMetaTag(property, content) {
    let meta = document.querySelector(`meta[property="${property}"]`) || document.querySelector(`meta[name="${property}"]`);
    if (!meta) {
      meta = document.createElement('meta');
      if (property.startsWith('og:')) {
        meta.setAttribute('property', property);
      } else {
        meta.setAttribute('name', property);
      }
      document.head.appendChild(meta);
    }
    meta.setAttribute('content', content);
  }

  // SEO Meta Tags
  setMetaTag('description', description);
  setMetaTag('og:title', title);
  setMetaTag('og:description', description);
  setMetaTag('og:image', image);
  setMetaTag('og:url', currentUrl);
  setMetaTag('og:type', 'article');
  setMetaTag('twitter:card', 'summary_large_image');
  setMetaTag('twitter:title', title);
  setMetaTag('twitter:description', description);
  setMetaTag('twitter:image', image);

  // Update canonical link
  let canonical = document.querySelector('link[rel="canonical"]');
  if (!canonical) {
    canonical = document.createElement('link');
    canonical.setAttribute('rel', 'canonical');
    document.head.appendChild(canonical);
  }
  canonical.setAttribute('href', currentUrl);
}

function resetNewsSEO() {
  const defaultTitle = 'Mountain Harvest - Tinh Hoa Nông Sản & Nhu Yếu Phẩm';
  const defaultDescription = 'Hệ thống phân phối nông sản và nhu yếu phẩm thiên nhiên hàng đầu.';
  
  document.title = defaultTitle;
  
  function setMetaTag(property, content) {
    let meta = document.querySelector(`meta[property="${property}"]`) || document.querySelector(`meta[name="${property}"]`);
    if (meta) {
      meta.setAttribute('content', content);
    }
  }

  setMetaTag('description', defaultDescription);
  setMetaTag('og:title', defaultTitle);
  setMetaTag('og:description', defaultDescription);
  setMetaTag('og:type', 'website');
}

async function loadNewsDetail(id) {
  const shopWrap = document.getElementById('main-shop-content');
  const detailEl = document.getElementById('news-detail');
  if (!detailEl || !shopWrap) return;
  try {
    const res = await fetch('/api/news/' + id);
    if (!res.ok) { showNewsList(); return; }
    const news = await res.json();
    if (news.error) { showNewsList(); return; }
    
    // Update SEO meta tags
    updateNewsSEO(news);
    
    document.getElementById('news-detail-image').src = news.image || '';
    document.getElementById('news-detail-image').alt = news.title || '';
    document.getElementById('news-detail-date').textContent = news.date ? news.date : '';
    const authorEl = document.getElementById('news-detail-author');
    if (authorEl) {
      authorEl.textContent = news.author ? 'Tác giả: ' + news.author : '';
    }
    document.getElementById('news-detail-title').textContent = news.title || '';
    var contentEl = document.getElementById('news-detail-content');
    if (contentEl) {
      contentEl.innerHTML = news.content || '';
    }
    shopWrap.classList.add('hidden');
    detailEl.classList.remove('hidden');
    const headerEl = document.querySelector('header.relative');
    if (headerEl) {
      headerEl.classList.add('hidden');
    }
  } catch (e) {
    console.warn('News detail failed', e);
    showNewsList();
  }
}

function showNewsList() {
  const shopWrap = document.getElementById('main-shop-content');
  const detailEl = document.getElementById('news-detail');
  if (shopWrap) shopWrap.classList.remove('hidden');
  if (detailEl) detailEl.classList.add('hidden');
  const headerEl = document.querySelector('header.relative');
  if (headerEl) {
    headerEl.classList.remove('hidden');
  }
  // Reset SEO to default
  resetNewsSEO();
}

function checkNewsParam() {
  // Check if content is already server-rendered (check data attribute or content)
  const newsDetailEl = document.getElementById('news-detail');
  const isServerRendered = newsDetailEl && (
    newsDetailEl.getAttribute('data-server-rendered') === 'true' ||
    (!newsDetailEl.classList.contains('hidden') &&
     newsDetailEl.querySelector('#news-detail-title') &&
     newsDetailEl.querySelector('#news-detail-title').textContent.trim() !== '')
  );
  
  // If already server-rendered, don't load again
  if (isServerRendered) {
    return;
  }
  
  // Check URL path /news/{id}
  const pathMatch = window.location.pathname.match(/^\/news\/(\d+)$/);
  if (pathMatch) {
    const id = parseInt(pathMatch[1], 10);
    if (!isNaN(id) && id > 0) {
      loadNewsDetail(id);
      return;
    }
  }
  
  // Check query parameter ?news=
  const urlParams = new URLSearchParams(window.location.search);
  const newsId = urlParams.get('news');
  if (newsId) {
    const id = parseInt(newsId, 10);
    if (!isNaN(id) && id > 0) {
      loadNewsDetail(id);
      // Update URL to clean path without query parameter (but keep history)
      if (window.history && window.history.replaceState) {
        window.history.replaceState({}, '', '/news/' + id);
      }
    }
  }
}

function renderNews() {
  const container = document.getElementById('news-list');
  if (!container) return;
  const list = Array.isArray(newsData) ? newsData : [];

  container.innerHTML = list.map(news => `
    <div class="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition">
        <div class="h-48 overflow-hidden">
            <img src="${news.image}" class="w-full h-full object-cover transform hover:scale-105 transition duration-500">
        </div>
        <div class="p-6">
            <span class="text-xs text-gray-400 mb-2 block"><i class="far fa-calendar-alt mr-1"></i> ${news.date}</span>
            <a href="/news/${news.id}" class="font-bold text-lg mb-2 hover:text-brand-green cursor-pointer block">${news.title}</a>
            <p class="text-gray-600 text-sm mb-4 line-clamp-3">${news.content ? news.content.replace(/<[^>]*>/g, '').substring(0, 150) + '...' : ''}</p>
        </div>
    </div>
`).join('');
}
