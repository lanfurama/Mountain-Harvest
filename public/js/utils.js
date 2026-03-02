/**
 * Mountain Harvest - Utility Functions
 * Common utilities used across the application
 */

const Utils = {
  /**
   * Escape HTML to prevent XSS attacks
   * @param {string} text - Text to escape
   * @returns {string} Escaped HTML
   */
  escapeHtml(text) {
    if (text == null) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  },

  /**
   * Format currency in Vietnamese format
   * @param {number} amount - Amount to format
   * @returns {string} Formatted currency string
   */
  formatCurrency(amount) {
    if (typeof amount !== 'number') return '0đ';
    return amount.toLocaleString('vi-VN') + 'đ';
  },

  /**
   * Get element by ID safely
   * @param {string} id - Element ID
   * @returns {HTMLElement|null} Element or null
   */
  $(id) {
    return document.getElementById(id);
  },

  /**
   * Query selector all with error handling
   * @param {string} selector - CSS selector
   * @param {HTMLElement} context - Context element (default: document)
   * @returns {NodeList} NodeList of elements
   */
  $$(selector, context = document) {
    try {
      return context.querySelectorAll(selector);
    } catch (e) {
      console.warn('Invalid selector:', selector, e);
      return [];
    }
  },

  /**
   * Debounce function calls
   * @param {Function} func - Function to debounce
   * @param {number} wait - Wait time in ms
   * @returns {Function} Debounced function
   */
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  /**
   * Throttle function calls
   * @param {Function} func - Function to throttle
   * @param {number} limit - Time limit in ms
   * @returns {Function} Throttled function
   */
  throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  },

  /**
   * Parse URL parameters
   * @param {string} url - URL string (default: window.location.search)
   * @returns {Object} Parsed parameters
   */
  getUrlParams(url = window.location.search) {
    const params = new URLSearchParams(url);
    const result = {};
    for (const [key, value] of params.entries()) {
      result[key] = value;
    }
    return result;
  },

  /**
   * Build URL with parameters
   * @param {string} base - Base URL
   * @param {Object} params - Parameters object
   * @returns {string} URL with parameters
   */
  buildUrl(base, params = {}) {
    const url = new URL(base, window.location.origin);
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        url.searchParams.set(key, String(value));
      }
    });
    return url.pathname + url.search;
  },

  /**
   * Check if element is visible
   * @param {HTMLElement} element - Element to check
   * @returns {boolean} True if visible
   */
  isVisible(element) {
    if (!element) return false;
    return element.offsetParent !== null && !element.classList.contains('hidden');
  },

  /**
   * Smooth scroll to element
   * @param {string|HTMLElement} target - Target element or selector
   * @param {number} offset - Offset from top (default: 100)
   */
  scrollTo(target, offset = 100) {
    const element = typeof target === 'string' ? Utils.$(target) : target;
    if (!element) return;
    
    const elementPosition = element.offsetTop;
    const offsetPosition = elementPosition - offset;

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    });
  },

  /**
   * Show loading skeleton
   * @param {HTMLElement} container - Container element
   * @param {number} count - Number of skeleton items
   * @param {string} template - HTML template for skeleton
   */
  showSkeleton(container, count, template) {
    if (!container) return;
    container.innerHTML = Array(count).fill(0).map(() => template).join('');
  },

  /**
   * Safe JSON parse
   * @param {string} json - JSON string
   * @param {*} defaultValue - Default value if parse fails
   * @returns {*} Parsed object or default value
   */
  safeJsonParse(json, defaultValue = null) {
    try {
      return JSON.parse(json);
    } catch (e) {
      console.warn('JSON parse error:', e);
      return defaultValue;
    }
  },

  /**
   * Safe localStorage get
   * @param {string} key - Storage key
   * @param {*} defaultValue - Default value
   * @returns {*} Stored value or default
   */
  getStorage(key, defaultValue = null) {
    try {
      const item = localStorage.getItem(key);
      return item ? Utils.safeJsonParse(item, defaultValue) : defaultValue;
    } catch (e) {
      console.warn('localStorage get error:', e);
      return defaultValue;
    }
  },

  /**
   * Safe localStorage set
   * @param {string} key - Storage key
   * @param {*} value - Value to store
   * @returns {boolean} Success status
   */
  setStorage(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (e) {
      console.warn('localStorage set error:', e);
      return false;
    }
  }
};

// Export for use in other modules
if (typeof window !== 'undefined') {
  window.Utils = Utils;
}
