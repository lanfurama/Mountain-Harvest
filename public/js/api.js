/**
 * Mountain Harvest - API Client
 * Centralized API calls with error handling and retry logic
 */

const ApiClient = {
  /**
   * Default configuration
   */
  config: {
    baseUrl: '',
    timeout: 10000,
    retries: 3,
    retryDelay: 1000
  },

  /**
   * Make API request with error handling
   * @param {string} url - API endpoint
   * @param {Object} options - Fetch options
   * @returns {Promise<Object>} Response data
   */
  async request(url, options = {}) {
    const {
      method = 'GET',
      body = null,
      headers = {},
      timeout = this.config.timeout,
      retries = this.config.retries
    } = options;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const requestOptions = {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      signal: controller.signal
    };

    if (body && method !== 'GET') {
      requestOptions.body = JSON.stringify(body);
    }

    let lastError;
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const response = await fetch(url, requestOptions);
        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json().catch(() => ({}));
        return { ok: true, data, status: response.status };
      } catch (error) {
        lastError = error;
        if (attempt < retries && !controller.signal.aborted) {
          await new Promise(resolve => setTimeout(resolve, this.config.retryDelay * (attempt + 1)));
          continue;
        }
      }
    }

    clearTimeout(timeoutId);
    return {
      ok: false,
      error: lastError?.message || 'Request failed',
      data: null
    };
  },

  /**
   * GET request
   * @param {string} endpoint - API endpoint
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} Response data
   */
  async get(endpoint, params = {}) {
    const url = Utils.buildUrl(endpoint, params);
    return this.request(url, { method: 'GET' });
  },

  /**
   * POST request
   * @param {string} endpoint - API endpoint
   * @param {Object} data - Request body
   * @returns {Promise<Object>} Response data
   */
  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: data
    });
  },

  /**
   * PUT request
   * @param {string} endpoint - API endpoint
   * @param {Object} data - Request body
   * @returns {Promise<Object>} Response data
   */
  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: data
    });
  },

  /**
   * DELETE request
   * @param {string} endpoint - API endpoint
   * @returns {Promise<Object>} Response data
   */
  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  },

  // Specific API endpoints
  products: {
    async list(params = {}) {
      return ApiClient.get('/api/products', params);
    },
    async get(id) {
      return ApiClient.get(`/api/products/${id}`);
    }
  },

  news: {
    async list(params = {}) {
      return ApiClient.get('/api/news', params);
    },
    async get(id) {
      return ApiClient.get(`/api/news/${id}`);
    },
    async getRelated(id, limit = 3) {
      return ApiClient.get(`/api/news/${id}/related`, { limit });
    }
  },

  site: {
    async getConfig() {
      return ApiClient.get('/api/site');
    }
  },

  pages: {
    async list() {
      return ApiClient.get('/api/pages');
    }
  },

  newsletter: {
    async subscribe(email) {
      return ApiClient.post('/api/newsletter/subscribe', { email });
    }
  }
};

// Export for use in other modules
if (typeof window !== 'undefined') {
  window.ApiClient = ApiClient;
}
