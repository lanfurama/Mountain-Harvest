/**
 * Mountain Harvest - Main Application Logic
 */

async function loadData() {
  await Promise.all([loadProducts(1), loadNews(1)]);
}

async function loadSiteHeader() {
  try {
    const res = await fetch('/api/site');
    if (!res.ok) return;
    const data = await res.json();
    const brand = data.brand || data.header || {};
    const name = brand.siteName || '';
    const tagline = brand.tagline || '';
    const iconClass = (brand.icon || 'fas fa-mountain').trim();
    const nameEl = document.getElementById('site-name');
    const taglineEl = document.getElementById('site-tagline');
    const iconEl = document.getElementById('site-icon');
    const nameFooterEl = document.getElementById('site-name-footer');
    const iconFooterEl = document.getElementById('site-icon-footer');
    if (nameEl && name) nameEl.textContent = name;
    if (taglineEl && tagline) taglineEl.textContent = tagline;
    if (iconEl) iconEl.className = iconClass + ' text-brand-green text-3xl mr-2';
    if (nameFooterEl && name) nameFooterEl.textContent = name;
    if (iconFooterEl) iconFooterEl.className = iconClass + ' text-2xl mr-2';
  } catch (e) { /* ignore */ }
}

function showToast(message) {
  let toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.className = 'fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none';
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  toast.className = 'bg-gray-900 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-3 transform translate-y-10 opacity-0 transition-all duration-300';
  toast.innerHTML = `<i class="fas fa-check-circle text-brand-light"></i> <span>${message}</span>`;

  toastContainer.appendChild(toast);

  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-10', 'opacity-0');
  });

  setTimeout(() => {
    toast.classList.add('translate-y-10', 'opacity-0');
    setTimeout(() => {
      toast.remove();
    }, 300);
  }, 3000);
}

// Sticky Navbar Effect
window.addEventListener('scroll', function () {
  const navbar = document.getElementById('navbar');
  if (window.scrollY > 50) {
    navbar.classList.add('shadow-lg');
    navbar.classList.add('py-0');
  } else {
    navbar.classList.remove('shadow-lg');
    navbar.classList.remove('py-0');
  }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  applyLanguage();
  updateLanguageButtons();
  loadSiteHeader();
  
  // Check if news detail page is being displayed (server-rendered)
  const newsDetailEl = document.getElementById('news-detail');
  const mainShopContent = document.getElementById('main-shop-content');
  const isServerRendered = newsDetailEl && (
    newsDetailEl.getAttribute('data-server-rendered') === 'true' ||
    (!newsDetailEl.classList.contains('hidden') &&
     newsDetailEl.querySelector('#news-detail-title') &&
     newsDetailEl.querySelector('#news-detail-title').textContent.trim() !== '')
  );
  
  const isNewsDetailPage = isServerRendered || 
    (mainShopContent && window.getComputedStyle(mainShopContent).display === 'none') ||
    window.location.pathname.match(/^\/news\/(\d+)$/);
  
  // Only check for client-side loading if NOT server-rendered
  if (!isServerRendered && typeof checkNewsParam === 'function') {
    checkNewsParam();
  }
  
  // Only load homepage data if not on news detail page
  if (!isNewsDetailPage) {
    loadData();
    renderCart();
    ['filter-category', 'filter-price', 'filter-standard', 'filter-sort'].forEach(function (id) {
      const el = document.getElementById(id);
      if (el) el.addEventListener('change', function () { loadProducts(1); });
    });
    const clearBtn = document.getElementById('clear-filters');
    if (clearBtn) clearBtn.addEventListener('click', function (e) { e.preventDefault(); clearAllFilters(); });

    const modal = document.getElementById('product-modal');
    if (modal) modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal();
    });
  } else {
    renderCart();
  }
});
