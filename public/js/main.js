/**
 * Mountain Harvest - Main Application Logic (SSR-first)
 * Refactored for better maintainability and modularity
 */

// CRITICAL: handleImageError must be defined FIRST and globally
// Images in HTML may call this before other scripts load
(function() {
  'use strict';
  const FALLBACK_IMAGE_URL = 'https://placehold.co/600x400/e5e7eb/9ca3af?text=No+Image';
  
  function handleImageError(img) {
    if (!img || img.dataset.fallbackApplied === 'true') return;
    img.dataset.fallbackApplied = 'true';
    img.src = FALLBACK_IMAGE_URL;
    img.alt = (img.alt || '') + ' (Hình ảnh tạm thời - ảnh gốc bị lỗi)';
    img.classList.add('bg-gray-100', 'object-contain');
  }
  
  // Make globally available IMMEDIATELY - before any other code runs
  if (typeof window !== 'undefined') {
    window.handleImageError = handleImageError;
  }
  // Also make available globally (for older browsers or edge cases)
  if (typeof globalThis !== 'undefined') {
    globalThis.handleImageError = handleImageError;
  }
})();

// Check dependencies with warning (not error, to allow graceful degradation)
if (typeof Config === 'undefined' || typeof Utils === 'undefined' || typeof ApiClient === 'undefined') {
  console.warn('Some modules may not be loaded. Using fallbacks where possible.');
  
  // Create minimal fallbacks
  if (typeof Utils === 'undefined') {
    window.Utils = {
      $: function(id) { return document.getElementById(id); },
      $$: function(sel) { return document.querySelectorAll(sel); },
      escapeHtml: function(text) {
        if (text == null) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
      },
      formatCurrency: function(amount) {
        if (typeof amount !== 'number') return '0đ';
        return amount.toLocaleString('vi-VN') + 'đ';
      },
      getStorage: function(key, defaultValue) {
        try {
          const item = localStorage.getItem(key);
          return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
          return defaultValue;
        }
      },
      scrollTo: function(target, offset) {
        const element = typeof target === 'string' ? document.getElementById(target) : target;
        if (!element) return;
        const elementPosition = element.offsetTop;
        const offsetPosition = elementPosition - (offset || 100);
        window.scrollTo({ top: offsetPosition, behavior: 'smooth' });
      },
      throttle: function(func, limit) {
        let inThrottle;
        return function executedFunction(...args) {
          if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
          }
        };
      }
    };
  }
  
  if (typeof Config === 'undefined') {
    window.Config = {
      FALLBACK_IMAGE_URL: 'https://placehold.co/600x400/e5e7eb/9ca3af?text=No+Image',
      SELECTORS: {
        NAVBAR: '#navbar',
        MOBILE_MENU: '#mobile-menu',
        MOBILE_MENU_BTN: '#mobile-menu-btn'
      },
      STICKY_NAVBAR_THRESHOLD: 50,
      SCROLL_OFFSET: 100,
      THROTTLE_DELAY: 100,
      STORAGE_KEYS: {
        CART: 'cart'
      },
      CATEGORY_ICONS: ['fa-carrot', 'fa-wheat-awn', 'fa-coffee', 'fa-house-chimney', 'fa-spray-can-sparkles'],
      CATEGORY_COLORS: {
        icon: ['text-green-600', 'text-amber-600', 'text-orange-600', 'text-blue-600', 'text-purple-600'],
        bg: ['bg-green-50', 'bg-amber-50', 'bg-orange-50', 'bg-blue-50', 'bg-purple-50']
      }
    };
  }
  
  if (typeof ApiClient === 'undefined') {
    window.ApiClient = {
      site: {
        getConfig: async function() {
          try {
            const res = await fetch('/api/site');
            const data = res.ok ? await res.json() : null;
            return { ok: !!data, data, error: data ? null : 'Failed to fetch' };
          } catch (e) {
            return { ok: false, data: null, error: e.message };
          }
        }
      },
      pages: {
        list: async function() {
          try {
            const res = await fetch('/api/pages');
            const data = res.ok ? await res.json() : null;
            return { ok: !!data, data, error: data ? null : 'Failed to fetch' };
          } catch (e) {
            return { ok: false, data: null, error: e.message };
          }
        }
      },
      newsletter: {
        subscribe: async function(email) {
          try {
            const res = await fetch('/api/newsletter/subscribe', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ email })
            });
            const data = await res.json().catch(() => ({}));
            return { ok: res.ok && data.ok, data, error: data.error || null };
          } catch (e) {
            return { ok: false, data: null, error: e.message };
          }
        }
      }
    };
  }
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

// Sticky Navbar Effect (throttled for performance)
// Wrap in function to ensure Utils/Config are available
function initNavbarScroll() {
  if (typeof Utils === 'undefined' || typeof Config === 'undefined') {
    // Fallback without throttle
    window.addEventListener('scroll', function() {
      const navbar = document.getElementById('navbar');
      if (!navbar) return;
      if (window.scrollY > 50) {
        navbar.classList.add('shadow-lg');
      } else {
        navbar.classList.remove('shadow-lg');
      }
    });
    return;
  }
  
  const handleNavbarScroll = Utils.throttle(() => {
    const navbar = Utils.$(Config.SELECTORS.NAVBAR.slice(1));
    if (!navbar) return;
    if (window.scrollY > Config.STICKY_NAVBAR_THRESHOLD) {
      navbar.classList.add('shadow-lg');
    } else {
      navbar.classList.remove('shadow-lg');
    }
  }, Config.THROTTLE_DELAY);
  
  window.addEventListener('scroll', handleNavbarScroll);
}

initNavbarScroll();

async function loadSiteConfig() {
  try {
    const response = await ApiClient.site.getConfig();
    if (!response.ok || !response.data) {
      console.warn('Site config load failed:', response.error);
      return;
    }
    const data = response.data;

    // Topbar
    const topbar = data.topbar || {};
    const elFreeShip = Utils.$('topbar-free-shipping');
    if (elFreeShip && topbar.freeShipping) {
      elFreeShip.innerHTML = '<i class="fas fa-truck mr-2"></i>' + Utils.escapeHtml(topbar.freeShipping);
    }
    const elHotline = Utils.$('topbar-hotline');
    if (elHotline && topbar.hotline) {
      elHotline.textContent = 'Hotline: ' + topbar.hotline;
      elHotline.href = 'tel:' + topbar.hotline.replace(/\s/g, '');
    }
    const elSupport = Utils.$('topbar-support');
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
    const navCat = Utils.$('nav-categories');
    if (navCat) {
      let html = '';
      if (categories.length > 0) {
        html = categories.map((c, i) =>
          `<a href="/?category=${encodeURIComponent(c)}" class="hover:text-brand-green transition flex items-center group"><i class="fas ${Config.CATEGORY_ICONS[i] || 'fa-tag'} mr-1.5 group-hover:scale-110 transition-transform"></i><span>${Utils.escapeHtml(c)}</span></a>`
        ).join('');
      }
      // Add separator and News link
      html += '<div class="w-px h-4 bg-gray-300"></div>';
      html += '<a href="/#news-section" class="hover:text-brand-green transition flex items-center group" data-i18n="nav.news"><i class="fas fa-newspaper mr-1.5 group-hover:scale-110 transition-transform"></i><span>Tin tức</span></a>';
      navCat.innerHTML = html;
    }

    // Mobile menu content
    const mobileMenuContent = Utils.$('mobile-menu-content');
    if (mobileMenuContent) {
      let mobileHtml = '';
      if (categories.length > 0) {
        mobileHtml = categories.map((c, i) =>
          `<a href="/?category=${encodeURIComponent(c)}" class="flex items-center gap-3 py-3 px-3 text-gray-800 hover:text-brand-green hover:bg-brand-green/5 rounded-xl transition font-medium group">
            <div class="w-10 h-10 rounded-lg ${Config.CATEGORY_COLORS.bg[i] || 'bg-gray-100'} flex items-center justify-center group-hover:bg-brand-green transition">
              <i class="fas ${Config.CATEGORY_ICONS[i] || 'fa-tag'} ${Config.CATEGORY_COLORS.icon[i] || 'text-gray-600'} group-hover:text-white transition"></i>
            </div>
            <span class="flex-1">${Utils.escapeHtml(c)}</span>
            <i class="fas fa-chevron-right text-gray-400 group-hover:text-brand-green transition"></i>
          </a>`
        ).join('');
      } else {
        // Fallback if no categories loaded
        mobileHtml = '<p class="text-gray-500 text-sm py-2 px-3">Đang tải danh mục...</p>';
      }
      mobileMenuContent.innerHTML = mobileHtml;
    }
    
    // Ensure News link is always visible in mobile menu
    const mobileMenuNews = document.getElementById('mobile-menu-news');
    if (!mobileMenuNews) {
      // Create news link section if it doesn't exist
      const mobileMenu = document.getElementById('mobile-menu');
      if (mobileMenu) {
        const container = mobileMenu.querySelector('.p-5');
        if (container) {
          const newsSection = document.createElement('div');
          newsSection.id = 'mobile-menu-news';
          newsSection.className = 'border-t-2 border-gray-100 pt-4 mt-4';
          newsSection.innerHTML = `
            <a href="/#news-section" class="flex items-center gap-3 py-3 px-3 text-gray-800 hover:text-brand-green hover:bg-brand-green/5 rounded-xl transition font-semibold group">
              <div class="w-10 h-10 rounded-lg bg-brand-green/10 flex items-center justify-center group-hover:bg-brand-green transition">
                <i class="fas fa-newspaper text-brand-green group-hover:text-white transition"></i>
              </div>
              <span>Tin tức</span>
              <i class="fas fa-chevron-right text-gray-400 ml-auto group-hover:text-brand-green transition"></i>
            </a>
          `;
          container.appendChild(newsSection);
        }
      }
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

    // Header category dropdown
    const headerCat = document.getElementById('header-category');
    if (headerCat && categories.length > 0) {
      const urlParams = new URLSearchParams(window.location.search);
      const urlCategory = urlParams.get('category') || headerCat.value;
      headerCat.innerHTML = '<option value="">Tất cả danh mục</option>' +
        categories.map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join('');
      headerCat.value = urlCategory && categories.includes(urlCategory) ? urlCategory : '';
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
          <img src="${Utils.escapeHtml(img)}" alt="${Utils.escapeHtml(b.title || '')}" class="absolute inset-0 w-full h-full object-cover transition duration-500 group-hover:scale-105" onerror="handleImageError(this)">
          <div class="absolute inset-0 bg-black/40 hover:bg-black/30 transition"></div>
          <div class="absolute inset-0 flex flex-col justify-center items-center text-center p-8">
            <h3 class="text-3xl font-bold text-white mb-2 font-serif">${Utils.escapeHtml(b.title || '')}</h3>
            <p class="text-gray-200 mb-6 max-w-sm">${Utils.escapeHtml(b.desc || '')}</p>
            <a href="#shop" class="${btnClass} px-6 py-2 rounded-full font-bold transition">${Utils.escapeHtml(b.buttonText || 'Shop Now')}</a>
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
    const response = await ApiClient.pages.list();
    if (!response.ok) {
      console.warn('Footer pages load failed:', response.error);
      return;
    }
    const items = response.data?.items || [];
    const footerPages = Utils.$('footer-pages');
    if (!footerPages) return;
    if (items.length > 0) {
      footerPages.innerHTML = items.map(p =>
        `<li><a href="/p/${Utils.escapeHtml(p.slug)}" class="hover:text-white hover:underline">${Utils.escapeHtml(p.title || p.slug)}</a></li>`
      ).join('');
    }
  } catch (e) {
    console.warn('Footer pages load failed', e);
  }
}

// Use Utils.escapeHtml instead - keeping for backward compatibility
function escapeHtml(s) {
  return Utils.escapeHtml(s);
}

function initNewsletterForm() {
  const form = Utils.$('newsletter-form');
  const msgEl = Utils.$('newsletter-message');
  if (!form || !msgEl) return;
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = Utils.$('newsletter-email');
    const email = (input?.value || '').trim();
    if (!email || !email.includes('@')) return;
    
    msgEl.classList.add('hidden');
    const response = await ApiClient.newsletter.subscribe(email);
    
    msgEl.classList.remove('hidden');
    if (response.ok && response.data?.ok) {
      msgEl.textContent = response.data.message || 'Đăng ký thành công!';
      msgEl.className = 'mt-3 text-sm text-green-600';
      if (input) input.value = '';
    } else {
      msgEl.textContent = response.data?.error || response.error || 'Có lỗi xảy ra. Vui lòng thử lại.';
      msgEl.className = 'mt-3 text-sm text-red-600';
    }
  });
}

// Smooth scroll handler for anchor links
function initSmoothScroll() {
  Utils.$$('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (href === '#' || !href.startsWith('#')) return;
      
      const targetId = href.substring(1);
      const targetElement = Utils.$(targetId);
      
      if (targetElement) {
        e.preventDefault();
        Utils.scrollTo(targetElement, Config.SCROLL_OFFSET);
        
        // Update URL without triggering scroll
        if (history.pushState) {
          history.pushState(null, null, href);
        }
      }
    });
  });
}

// Ensure mobile menu news link is visible
function ensureMobileMenuNews() {
  const mobileMenuNews = Utils.$('mobile-menu-news');
  const mobileMenu = Utils.$(Config.SELECTORS.MOBILE_MENU.slice(1));
  
  if (!mobileMenuNews && mobileMenu) {
    const container = mobileMenu.querySelector('.p-5');
    if (container) {
      const newsSection = document.createElement('div');
      newsSection.id = 'mobile-menu-news';
      newsSection.className = 'border-t-2 border-gray-100 pt-4 mt-4';
      newsSection.innerHTML = `
        <a href="/#news-section" class="flex items-center gap-3 py-3 px-3 text-gray-800 hover:text-brand-green hover:bg-brand-green/5 rounded-xl transition font-semibold group">
          <div class="w-10 h-10 rounded-lg bg-brand-green/10 flex items-center justify-center group-hover:bg-brand-green transition">
            <i class="fas fa-newspaper text-brand-green group-hover:text-white transition"></i>
          </div>
          <span>Tin tức</span>
          <i class="fas fa-chevron-right text-gray-400 ml-auto group-hover:text-brand-green transition"></i>
        </a>
      `;
      container.appendChild(newsSection);
    }
  }
}

// Initialize - all critical content is already server-side rendered
function initApp() {
  if (typeof applyLanguage === 'function') applyLanguage();
  if (typeof updateLanguageButtons === 'function') updateLanguageButtons();
  if (typeof renderCart === 'function') renderCart();
  ensureMobileMenuNews();
  loadSiteConfig();
  loadFooterPages();
  initNewsletterForm();
  initCheckoutSection();
  initMobileMenu();
  initSmoothScroll();
  if (typeof loadNews === 'function' && !window.location.pathname.match(/^\/news\/\d+$/)) {
    loadNews(1);
  }
  window.addEventListener('popstate', function() {
    if (typeof loadNews === 'function' && !window.location.pathname.match(/^\/news\/\d+$/)) {
      loadNews(1);
    }
  });
  
  // Double check after a short delay
  setTimeout(ensureMobileMenuNews, 100);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  // DOM already loaded
  initApp();
}

function initMobileMenu() {
  // Use direct ID lookup as fallback if Config/Utils not available
  const menuBtn = (typeof Utils !== 'undefined' && typeof Config !== 'undefined') 
    ? Utils.$(Config.SELECTORS.MOBILE_MENU_BTN.slice(1))
    : document.getElementById('mobile-menu-btn');
  
  const mobileMenu = (typeof Utils !== 'undefined' && typeof Config !== 'undefined')
    ? Utils.$(Config.SELECTORS.MOBILE_MENU.slice(1))
    : document.getElementById('mobile-menu');
  
  if (!menuBtn || !mobileMenu) {
    console.warn('Mobile menu elements not found', { menuBtn, mobileMenu });
    return;
  }
  
  const toggleMenu = (show) => {
    if (show === undefined) {
      mobileMenu.classList.toggle('hidden');
    } else {
      if (show) {
        mobileMenu.classList.remove('hidden');
      } else {
        mobileMenu.classList.add('hidden');
      }
    }
    
    const icon = menuBtn.querySelector('i');
    if (icon) {
      icon.className = mobileMenu.classList.contains('hidden') ? 'fas fa-bars' : 'fas fa-times';
    }
  };
  
  // Ensure button is clickable
  menuBtn.style.cursor = 'pointer';
  menuBtn.setAttribute('type', 'button');
  menuBtn.setAttribute('aria-label', 'Toggle mobile menu');
  menuBtn.setAttribute('aria-expanded', 'false');
  
  menuBtn.addEventListener('click', function(e) {
    e.preventDefault();
    e.stopPropagation();
    const isHidden = mobileMenu.classList.contains('hidden');
    toggleMenu(isHidden);
    menuBtn.setAttribute('aria-expanded', String(!isHidden));
  });
  
  // Close menu when clicking outside
  document.addEventListener('click', function(e) {
    if (!mobileMenu.contains(e.target) && !menuBtn.contains(e.target)) {
      if (!mobileMenu.classList.contains('hidden')) {
        toggleMenu(false);
        menuBtn.setAttribute('aria-expanded', 'false');
      }
    }
  });
  
  // Close menu when clicking on a link inside
  mobileMenu.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      toggleMenu(false);
      menuBtn.setAttribute('aria-expanded', 'false');
    });
  });
  
  // Close menu on escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && !mobileMenu.classList.contains('hidden')) {
      toggleMenu(false);
      menuBtn.setAttribute('aria-expanded', 'false');
      menuBtn.focus();
    }
  });
}

function initCheckoutSection() {
  function renderCheckout() {
    const summary = Utils.$('checkout-cart-summary');
    const totalEl = Utils.$('checkout-total');
    if (!summary || !totalEl) return;
    
    const cart = Utils.getStorage(Config.STORAGE_KEYS.CART, []);
    if (cart.length === 0) {
      summary.innerHTML = '<p class="text-gray-500 text-center py-4">Giỏ hàng trống. <a href="/#shop" class="text-brand-green hover:underline">Mua sắm ngay</a></p>';
      totalEl.textContent = Utils.formatCurrency(0);
      return;
    }
    
    const total = cart.reduce((s, i) => s + (i.price || 0) * (i.quantity || 1), 0);
    summary.innerHTML = cart.map(i =>
      `<div class="flex justify-between items-center py-2 border-b border-gray-100">
        <span class="font-medium">${Utils.escapeHtml(i.name || 'Sản phẩm')} x ${i.quantity || 1}</span>
        <span>${Utils.formatCurrency((i.price || 0) * (i.quantity || 1))}</span>
      </div>`
    ).join('');
    totalEl.textContent = Utils.formatCurrency(total);
  }
  
  if (window.location.hash === '#checkout') renderCheckout();
  window.addEventListener('hashchange', () => { 
    if (window.location.hash === '#checkout') renderCheckout(); 
  });
  document.addEventListener('cartUpdated', renderCheckout);
}
