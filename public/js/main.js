/**
 * Mountain Harvest - Main Application Logic (SSR-first)
 */

// Global fallback image for broken images
const FALLBACK_IMAGE_URL = 'https://placehold.co/600x400/e5e7eb/9ca3af?text=No+Image';

function handleImageError(img) {
  if (!img || img.dataset.fallbackApplied === 'true') return;
  img.dataset.fallbackApplied = 'true';
  img.src = FALLBACK_IMAGE_URL;
  img.alt = (img.alt || '') + ' (Hình ảnh tạm thời - ảnh gốc bị lỗi)';
  img.classList.add('bg-gray-100', 'object-contain');
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
  if (!navbar) return;
  if (window.scrollY > 50) {
    navbar.classList.add('shadow-lg');
  } else {
    navbar.classList.remove('shadow-lg');
  }
});

async function loadSiteConfig() {
  try {
    const res = await fetch('/api/site');
    const data = res.ok ? await res.json() : null;
    if (!data) return;

    // Topbar
    const topbar = data.topbar || {};
    const elFreeShip = document.getElementById('topbar-free-shipping');
    if (elFreeShip && topbar.freeShipping) elFreeShip.innerHTML = '<i class="fas fa-truck mr-2"></i>' + escapeHtml(topbar.freeShipping);
    const elHotline = document.getElementById('topbar-hotline');
    if (elHotline && topbar.hotline) {
      elHotline.textContent = 'Hotline: ' + topbar.hotline;
      elHotline.href = 'tel:' + topbar.hotline.replace(/\s/g, '');
    }
    const elSupport = document.getElementById('topbar-support');
    if (elSupport && topbar.support) elSupport.textContent = topbar.support;

    // Hero
    const hero = data.hero || {};
    const heroImg = document.getElementById('hero-image');
    if (heroImg && hero.image) { heroImg.src = hero.image; heroImg.alt = hero.title || 'Hero'; }
    const heroPromo = document.getElementById('hero-promo');
    if (heroPromo && hero.promo) heroPromo.textContent = hero.promo;
    const heroTitle = document.getElementById('hero-title');
    if (heroTitle && hero.title) heroTitle.innerHTML = hero.title.replace(/\n/g, '<br>');
    const heroSub = document.getElementById('hero-subtitle');
    if (heroSub && hero.subtitle) heroSub.textContent = hero.subtitle;
    const heroBtn = document.getElementById('hero-button');
    if (heroBtn && hero.buttonText) heroBtn.textContent = hero.buttonText;

    // Brand (header + footer)
    const brand = data.brand || data.header || {};
    const brandName = brand.name || brand.siteName;
    const siteName = document.getElementById('site-name');
    if (siteName && brandName) siteName.textContent = brandName;
    const siteTagline = document.getElementById('site-tagline');
    if (siteTagline && brand.tagline) siteTagline.textContent = brand.tagline;
    const siteNameFooter = document.getElementById('site-name-footer');
    if (siteNameFooter && brandName) siteNameFooter.textContent = brandName;
    if (brand.icon) {
      const iconClass = brand.icon.startsWith('fa-') ? 'fas ' + brand.icon : brand.icon;
      const icons = document.querySelectorAll('#site-icon, #site-icon-footer');
      icons.forEach(el => {
        const isFooter = el.id === 'site-icon-footer';
        el.className = iconClass + ' text-brand-green ' + (isFooter ? 'text-2xl' : 'text-3xl') + ' mr-2';
      });
    }

    // Nav categories
    const categories = data.categories || [];
    const navCat = document.getElementById('nav-categories');
    if (navCat && categories.length > 0) {
      const icons = ['fa-carrot', 'fa-wheat-awn', 'fa-coffee', 'fa-house-chimney', 'fa-spray-can-sparkles'];
      navCat.innerHTML = categories.map((c, i) =>
        `<a href="/?category=${encodeURIComponent(c)}" class="hover:text-brand-green transition flex items-center"><i class="fas ${icons[i] || 'fa-tag'} mr-1"></i><span>${escapeHtml(c)}</span></a>`
      ).join('');
    }

    // Category filter dropdown (task 3)
    const filterCat = document.getElementById('filter-category');
    if (filterCat && categories.length > 0) {
      const urlParams = new URLSearchParams(window.location.search);
      const urlCategory = urlParams.get('category') || filterCat.value;
      filterCat.innerHTML = '<option value="">Danh mục: Tất cả</option>' +
        categories.map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join('');
      filterCat.value = urlCategory && categories.includes(urlCategory) ? urlCategory : '';
    }

    // Brochures
    const brochures = data.brochures || [];
    const brochureList = document.getElementById('brochure-list');
    if (brochureList && brochures.length > 0) {
      const defaultImg = 'https://images.unsplash.com/photo-1542838132-92c53300491e?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80';
      const colors = ['text-brand-green', 'text-brand-brown'];
      brochureList.innerHTML = brochures.map((b, i) => {
        const img = b.image || defaultImg;
        const btnClass = i === 0 ? 'bg-white text-brand-green hover:bg-brand-green hover:text-white' : 'bg-white text-brand-brown hover:bg-brand-brown hover:text-white';
        return `<div class="relative rounded-2xl overflow-hidden h-80 group cursor-pointer">
          <img src="${escapeHtml(img)}" alt="${escapeHtml(b.title || '')}" class="absolute inset-0 w-full h-full object-cover transition duration-500 group-hover:scale-105" onerror="handleImageError(this)">
          <div class="absolute inset-0 bg-black/40 hover:bg-black/30 transition"></div>
          <div class="absolute inset-0 flex flex-col justify-center items-center text-center p-8">
            <h3 class="text-3xl font-bold text-white mb-2 font-serif">${escapeHtml(b.title || '')}</h3>
            <p class="text-gray-200 mb-6 max-w-sm">${escapeHtml(b.desc || '')}</p>
            <a href="#shop" class="${btnClass} px-6 py-2 rounded-full font-bold transition">${escapeHtml(b.buttonText || 'Shop Now')}</a>
          </div>
        </div>`;
      }).join('');
    }

    // Footer
    const footer = data.footer || {};
    const footerAddr = document.getElementById('footer-address');
    if (footerAddr && footer.address) footerAddr.textContent = footer.address;
    const footerPhone = document.getElementById('footer-phone');
    if (footerPhone && footer.phone) {
      footerPhone.textContent = footer.phone;
      footerPhone.href = 'tel:' + footer.phone.replace(/\s/g, '');
    }
    const footerEmail = document.getElementById('footer-email');
    if (footerEmail && footer.email) {
      footerEmail.textContent = footer.email;
      footerEmail.href = 'mailto:' + footer.email;
    }
    const footerDesc = document.getElementById('footer-desc');
    if (footerDesc && footer.description) footerDesc.textContent = footer.description;
    if (footer.social && Array.isArray(footer.social)) {
      const socialEl = document.getElementById('footer-social');
      if (socialEl) {
        socialEl.innerHTML = footer.social.map(s => {
          const icon = (s.icon || 'fa-link').startsWith('fa-') ? s.icon : 'fa-' + s.icon;
          return `<a href="${escapeHtml(s.url || '#')}" target="_blank" rel="noopener" class="text-white hover:text-brand-light transition"><i class="fab ${escapeHtml(icon)}"></i></a>`;
        }).join('');
      }
    }
  } catch (e) {
    console.warn('Site config load failed', e);
  }
}

async function loadFooterPages() {
  try {
    const res = await fetch('/api/pages');
    const data = res.ok ? await res.json() : null;
    const items = (data && data.items) || [];
    const footerPages = document.getElementById('footer-pages');
    if (!footerPages) return;
    if (items.length > 0) {
      footerPages.innerHTML = items.map(p =>
        `<li><a href="/p/${escapeHtml(p.slug)}" class="hover:text-white hover:underline">${escapeHtml(p.title || p.slug)}</a></li>`
      ).join('');
    }
  } catch (e) {
    console.warn('Footer pages load failed', e);
  }
}

function escapeHtml(s) {
  if (s == null) return '';
  const div = document.createElement('div');
  div.textContent = s;
  return div.innerHTML;
}

function initNewsletterForm() {
  const form = document.getElementById('newsletter-form');
  const msgEl = document.getElementById('newsletter-message');
  if (!form || !msgEl) return;
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('newsletter-email');
    const email = (input && input.value || '').trim();
    if (!email) return;
    msgEl.classList.add('hidden');
    try {
      const res = await fetch('/api/newsletter/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      const data = await res.json().catch(() => ({}));
      msgEl.classList.remove('hidden');
      if (data.ok) {
        msgEl.textContent = data.message || 'Đăng ký thành công!';
        msgEl.className = 'mt-3 text-sm text-green-600';
        if (input) input.value = '';
      } else {
        msgEl.textContent = data.error || 'Có lỗi xảy ra. Vui lòng thử lại.';
        msgEl.className = 'mt-3 text-sm text-red-600';
      }
    } catch (err) {
      msgEl.classList.remove('hidden');
      msgEl.textContent = 'Kết nối thất bại. Vui lòng thử lại.';
      msgEl.className = 'mt-3 text-sm text-red-600';
    }
  });
}

// Initialize - all critical content is already server-side rendered
document.addEventListener('DOMContentLoaded', () => {
  if (typeof applyLanguage === 'function') applyLanguage();
  if (typeof updateLanguageButtons === 'function') updateLanguageButtons();
  if (typeof renderCart === 'function') renderCart();
  loadSiteConfig();
  loadFooterPages();
  initNewsletterForm();
  initCheckoutSection();
});

function initCheckoutSection() {
  function renderCheckout() {
    const summary = document.getElementById('checkout-cart-summary');
    const totalEl = document.getElementById('checkout-total');
    if (!summary || !totalEl) return;
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    if (cart.length === 0) {
      summary.innerHTML = '<p class="text-gray-500 text-center py-4">Giỏ hàng trống. <a href="/#shop" class="text-brand-green hover:underline">Mua sắm ngay</a></p>';
      totalEl.textContent = '0đ';
      return;
    }
    const total = cart.reduce((s, i) => s + (i.price || 0) * (i.quantity || 1), 0);
    summary.innerHTML = cart.map(i =>
      `<div class="flex justify-between items-center py-2 border-b border-gray-100">
        <span class="font-medium">${escapeHtml(i.name || 'Sản phẩm')} x ${i.quantity || 1}</span>
        <span>${typeof formatCurrency === 'function' ? formatCurrency((i.price || 0) * (i.quantity || 1)) : (i.price * i.quantity).toLocaleString('vi-VN') + 'đ'}</span>
      </div>`
    ).join('');
    totalEl.textContent = typeof formatCurrency === 'function' ? formatCurrency(total) : total.toLocaleString('vi-VN') + 'đ';
  }
  if (window.location.hash === '#checkout') renderCheckout();
  window.addEventListener('hashchange', () => { if (window.location.hash === '#checkout') renderCheckout(); });
  document.addEventListener('cartUpdated', renderCheckout);
}
