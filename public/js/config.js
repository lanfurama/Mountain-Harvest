/**
 * Mountain Harvest - Configuration & Constants
 * Centralized configuration for the application
 */

const Config = {
  // Pagination
  PRODUCTS_PER_PAGE: 8,
  NEWS_PER_PAGE: 6,

  // API
  API_TIMEOUT: 10000,
  API_RETRIES: 3,

  // UI
  TOAST_DURATION: 3000,
  DEBOUNCE_DELAY: 300,
  THROTTLE_DELAY: 100,

  // Images
  FALLBACK_IMAGE_URL: 'https://placehold.co/600x400/e5e7eb/9ca3af?text=No+Image',

  // Scroll
  SCROLL_OFFSET: 100,
  STICKY_NAVBAR_THRESHOLD: 50,

  // Storage keys
  STORAGE_KEYS: {
    CART: 'cart',
    LANGUAGE: 'language',
    THEME: 'theme'
  },

  // Selectors (commonly used)
  SELECTORS: {
    NAVBAR: '#navbar',
    CART_COUNT: '#cart-count',
    MOBILE_MENU: '#mobile-menu',
    MOBILE_MENU_BTN: '#mobile-menu-btn',
    TOAST_CONTAINER: '#toast-container'
  },

  // Category icons mapping
  CATEGORY_ICONS: [
    'fa-carrot',
    'fa-wheat-awn',
    'fa-coffee',
    'fa-house-chimney',
    'fa-spray-can-sparkles'
  ],

  // Category colors
  CATEGORY_COLORS: {
    icon: ['text-green-600', 'text-amber-600', 'text-orange-600', 'text-blue-600', 'text-purple-600'],
    bg: ['bg-green-50', 'bg-amber-50', 'bg-orange-50', 'bg-blue-50', 'bg-purple-50']
  }
};

// Export for use in other modules
if (typeof window !== 'undefined') {
  window.Config = Config;
}
