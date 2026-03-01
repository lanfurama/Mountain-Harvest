/**
 * Admin Panel JavaScript
 * Modular structure for maintainability and extensibility
 */
(function() {
  'use strict';

  // ============================================================================
  // CONFIGURATION & CONSTANTS
  // ============================================================================
  var CONFIG = {
    RETRY_MAX: 15,
    RETRY_DELAY: 200,
    TOAST_DURATION: 3000,
    PREVIEW_DEBOUNCE: 500,
    FORM_TIMEOUT: 10000,
    META_DESC_MAX: 160
  };

  var SELECTORS = {
    sidebar: '#admin-sidebar',
    sidebarOverlay: '#admin-sidebar-overlay',
    sidebarToggle: '#admin-sidebar-toggle',
    toast: '#admin-toast',
    toastProgress: '#admin-toast-progress',
    confirmModal: '#admin-confirm-modal',
    confirmOverlay: '#admin-confirm-overlay',
    confirmMessage: '#admin-confirm-message',
    confirmCancel: '#admin-confirm-cancel',
    confirmOk: '#admin-confirm-ok',
    seoToggle: '#seo-toggle',
    seoSection: '#seo-section',
    seoChevron: '#seo-chevron'
  };

  var CSS_CLASSES = {
    activeTab: 'border-b-2 border-[#2F5233] text-[#2F5233]',
    inactiveTab: 'text-gray-600',
    hidden: 'hidden'
  };

  // ============================================================================
  // UTILITY FUNCTIONS
  // ============================================================================
  var Utils = {
    /**
     * Get element by ID
     */
    getElement: function(id) {
      return document.getElementById(id);
    },

    /**
     * Get elements by selector
     */
    querySelector: function(selector) {
      return document.querySelector(selector);
    },

    /**
     * Get all elements by selector
     */
    querySelectorAll: function(selector) {
      return document.querySelectorAll(selector);
    },

    /**
     * Get cookie value
     */
    getCookie: function(name) {
      if (!document.cookie) return null;
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          return decodeURIComponent(cookie.substring(name.length + 1));
        }
      }
      return null;
    },

    /**
     * Get CSRF token from meta tag or cookie
     */
    getCSRFToken: function() {
      var metaTag = document.querySelector('meta[name="csrf-token"]');
      if (metaTag) {
        return metaTag.getAttribute('content');
      }
      return this.getCookie('csrftoken');
    },

    /**
     * Format string to URL-friendly slug
     */
    formatSlug: function(text) {
      if (!text) return '';
      return text
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '') // Remove diacritics
        .replace(/[^a-z0-9\s-]/g, '') // Remove special chars
        .replace(/\s+/g, '-') // Replace spaces with hyphens
        .replace(/-+/g, '-') // Replace multiple hyphens with single
        .replace(/^-|-$/g, ''); // Remove leading/trailing hyphens
    },

    /**
     * Validate URL format
     */
    isValidUrlFormat: function(url) {
      if (!url || url.trim() === '') return false;
      
      // Accept data URLs
      if (url.startsWith('data:image/')) return true;
      
      // Accept relative paths
      if (url.startsWith('/') || url.startsWith('./') || url.startsWith('../')) return true;
      
      // Accept URLs that look like they're being typed
      if (url.match(/^https?:\/\//i)) return true;
      
      // Try to parse as absolute URL
      try {
        var urlObj = new URL(url);
        return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
      } catch (e) {
        return url.match(/^https?:\/\/[^\s]+/i) !== null;
      }
    },

    /**
     * Debounce function
     */
    debounce: function(func, wait) {
      var timeout;
      return function() {
        var context = this;
        var args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(function() {
          func.apply(context, args);
        }, wait);
      };
    },

    /**
     * Retry function with delay
     */
    retry: function(fn, maxRetries, delay, onComplete) {
      var retries = 0;
      function attempt() {
        if (fn()) {
          if (onComplete) onComplete(true);
          return;
        }
        retries++;
        if (retries >= maxRetries) {
          if (onComplete) onComplete(false);
          return;
        }
        setTimeout(attempt, delay);
      }
      attempt();
    },

    /**
     * Wait for element to be available
     */
    waitForElement: function(selector, callback, maxRetries, delay) {
      maxRetries = maxRetries || CONFIG.RETRY_MAX;
      delay = delay || CONFIG.RETRY_DELAY;
      
      var retries = 0;
      function check() {
        var element = typeof selector === 'string' 
          ? document.querySelector(selector) 
          : selector();
        if (element) {
          callback(element);
          return;
        }
        retries++;
        if (retries < maxRetries) {
          setTimeout(check, delay);
        }
      }
      check();
    }
  };

  // ============================================================================
  // TOAST NOTIFICATION MODULE
  // ============================================================================
  var Toast = {
    icons: {
      success: 'check-circle',
      error: 'exclamation-circle',
      warning: 'exclamation-triangle',
      info: 'info-circle'
    },
    colors: {
      success: 'bg-green-600',
      error: 'bg-red-600',
      warning: 'bg-yellow-600',
      info: 'bg-blue-600'
    },

    show: function(msg, type) {
      var el = Utils.getElement('admin-toast');
      var progressEl = Utils.getElement('admin-toast-progress');
      if (!el) return;
      
      var icon = this.icons[type] || this.icons.success;
      var color = this.colors[type] || this.colors.success;
      
      el.innerHTML = '<div class="flex items-center gap-3"><div class="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center"><i class="fas fa-' + icon + '"></i></div><span class="font-medium">' + msg + '</span></div>';
      
      if (progressEl) {
        progressEl.style.width = '100%';
        progressEl.style.transition = 'width ' + (CONFIG.TOAST_DURATION / 1000) + 's linear';
      }
      
      el.className = 'fixed bottom-6 right-6 z-50 flex items-center gap-2 px-5 py-4 rounded-xl shadow-2xl ' + color + ' text-white transform transition-all duration-300 min-w-[300px]';
      el.classList.remove(CSS_CLASSES.hidden, 'opacity-0', 'translate-y-4');
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
      
      setTimeout(function() {
        if (progressEl) progressEl.style.width = '0%';
        el.style.opacity = '0';
        el.style.transform = 'translateY(1rem)';
        setTimeout(function() {
          el.classList.add(CSS_CLASSES.hidden);
          if (progressEl) progressEl.style.width = '100%';
        }, 300);
      }, CONFIG.TOAST_DURATION);
    },

    init: function() {
      var urlParams = new URLSearchParams(window.location.search);
      var successMsg = urlParams.get('success');
      var errorMsg = urlParams.get('error');
      
      if (successMsg) {
        this.show(successMsg, 'success');
        var u = new URL(window.location);
        u.searchParams.delete('success');
        window.history.replaceState({}, '', u);
      }
      if (errorMsg) {
        this.show(decodeURIComponent(errorMsg), 'error');
        var u2 = new URL(window.location);
        u2.searchParams.delete('error');
        window.history.replaceState({}, '', u2);
      }
    }
  };

  // ============================================================================
  // CONFIRM MODAL MODULE
  // ============================================================================
  var ConfirmModal = {
    elements: {},
    pendingAction: null,

    init: function() {
      this.elements.modal = Utils.getElement('admin-confirm-modal');
      this.elements.overlay = Utils.getElement('admin-confirm-overlay');
      this.elements.message = Utils.getElement('admin-confirm-message');
      this.elements.cancel = Utils.getElement('admin-confirm-cancel');
      this.elements.ok = Utils.getElement('admin-confirm-ok');
      this.elements.dialog = Utils.getElement('admin-confirm-dialog');

      if (!this.elements.modal || !this.elements.cancel || !this.elements.ok) return;

      this.elements.cancel.textContent = 'Hủy';
      this.elements.ok.textContent = 'Xác nhận';
      this.elements.cancel.addEventListener('click', this.close.bind(this));
      if (this.elements.overlay) {
        this.elements.overlay.addEventListener('click', this.close.bind(this));
      }
      this.elements.ok.addEventListener('click', this.handleConfirm.bind(this));

      // Delegate [data-confirm] clicks
      document.addEventListener('click', function(e) {
        var target = e.target.closest('[data-confirm]');
        if (!target) return;
        e.preventDefault();
        e.stopPropagation();
        var msg = target.getAttribute('data-confirm');
        var form = target.closest('form');
        var href = target.getAttribute('href');
        ConfirmModal.open(msg, form ? { form: form } : (href ? { href: href } : null));
      });
    },

    open: function(msg, action) {
      if (this.elements.message) this.elements.message.textContent = msg;
      this.pendingAction = action || null;
      
      if (this.elements.modal) {
        this.elements.modal.classList.remove(CSS_CLASSES.hidden);
        if (this.elements.dialog) {
          setTimeout(function() {
            this.elements.dialog.classList.remove('scale-95', 'opacity-0');
            this.elements.dialog.classList.add('scale-100', 'opacity-100');
          }.bind(this), 10);
        }
      }
    },

    close: function() {
      if (this.elements.dialog) {
        this.elements.dialog.classList.remove('scale-100', 'opacity-100');
        this.elements.dialog.classList.add('scale-95', 'opacity-0');
        setTimeout(function() {
          if (this.elements.modal) this.elements.modal.classList.add(CSS_CLASSES.hidden);
          this.pendingAction = null;
        }.bind(this), 300);
      } else {
        if (this.elements.modal) this.elements.modal.classList.add(CSS_CLASSES.hidden);
        this.pendingAction = null;
      }
    },

    handleConfirm: function() {
      if (!this.pendingAction) {
        this.close();
        return;
      }

      var action = this.pendingAction;
      
      if (action.form) {
        if (!action.form.parentNode) {
          action.form.style.display = 'none';
          document.body.appendChild(action.form);
        }
        action.form.submit();
      } else if (action.url) {
        var form = document.createElement('form');
        form.method = 'POST';
        form.action = action.url;
        form.style.display = 'none';
        
        if (action.csrfToken) {
          var csrfInput = document.createElement('input');
          csrfInput.type = 'hidden';
          csrfInput.name = 'csrfmiddlewaretoken';
          csrfInput.value = action.csrfToken;
          form.appendChild(csrfInput);
        }
        
        document.body.appendChild(form);
        form.submit();
      } else if (action.href) {
        window.location.href = action.href;
      }
      
      this.pendingAction = null;
      this.close();
    }
  };

  // ============================================================================
  // DELETE CONFIRMATION MODULE
  // ============================================================================
  var DeleteConfirmation = {
    confirmDelete: function(id, url) {
      if (!id || id === 'None' || !url || url.includes('None')) {
        console.error('Invalid delete parameters:', id, url);
        return;
      }
      
      var deleteAction = {
        url: url,
        csrfToken: Utils.getCSRFToken()
      };
      
      ConfirmModal.open('Bạn có chắc chắn muốn xóa mục này không?', deleteAction);
    }
  };

  // ============================================================================
  // SIDEBAR MODULE
  // ============================================================================
  var Sidebar = {
    elements: {},

    init: function() {
      this.elements.sidebar = Utils.getElement('admin-sidebar');
      this.elements.overlay = Utils.getElement('admin-sidebar-overlay');
      this.elements.toggle = Utils.getElement('admin-sidebar-toggle');

      if (!this.elements.toggle || !this.elements.sidebar || !this.elements.overlay) return;

      this.elements.toggle.addEventListener('click', this.toggle.bind(this));
      this.elements.overlay.addEventListener('click', this.close.bind(this));
    },

    open: function() {
      this.elements.sidebar.classList.remove('-translate-x-full');
      this.elements.overlay.classList.remove(CSS_CLASSES.hidden);
      document.body.style.overflow = 'hidden';
    },

    close: function() {
      this.elements.sidebar.classList.add('-translate-x-full');
      this.elements.overlay.classList.add(CSS_CLASSES.hidden);
      document.body.style.overflow = '';
    },

    toggle: function() {
      if (this.elements.sidebar.classList.contains('-translate-x-full')) {
        this.open();
      } else {
        this.close();
      }
    }
  };

  // ============================================================================
  // FORM HANDLING MODULE
  // ============================================================================
  var FormHandler = {
    init: function() {
      document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', this.handleSubmit.bind(this));
      }.bind(this));
    },

    handleSubmit: function(e) {
      // Sync editor content before submit
      var newsContent = Utils.getElement('news-content');
      var newsContentCodeTextarea = Utils.getElement('news-content-code-textarea');
      var newsContentCode = Utils.getElement('news-content-code');
      
      if (newsContent && newsContentCode && !newsContentCode.classList.contains(CSS_CLASSES.hidden) && newsContentCodeTextarea) {
        newsContent.value = newsContentCodeTextarea.value;
      }
      
      var btn = e.target.querySelector('button[type="submit"]');
      if (btn && !btn.disabled) {
        this.setLoadingState(btn);
      }
    },

    setLoadingState: function(btn) {
      btn.disabled = true;
      var origHtml = btn.innerHTML;
      var origClasses = btn.className;
      btn.className = origClasses + ' opacity-75 cursor-not-allowed';
      btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Đang xử lý...';
      
      // Re-enable after timeout as fallback
      setTimeout(function() {
        btn.disabled = false;
        btn.className = origClasses;
        btn.innerHTML = origHtml;
      }, CONFIG.FORM_TIMEOUT);
    }
  };

  // ============================================================================
  // SEO SECTION MODULE
  // ============================================================================
  var SEOSection = {
    init: function() {
      var toggle = Utils.getElement('seo-toggle');
      var section = Utils.getElement('seo-section');
      var chevron = Utils.getElement('seo-chevron');

      if (toggle) {
        toggle.addEventListener('click', function() {
          if (section && chevron) {
            section.classList.toggle(CSS_CLASSES.hidden);
            chevron.classList.toggle('rotate-180');
          }
        });
      }

      // Initialize as hidden
      if (section) {
        section.classList.add(CSS_CLASSES.hidden);
      }
    }
  };

  // ============================================================================
  // NEWS EDITOR MODULE
  // ============================================================================
  var NewsEditor = {
    elements: {},
    slugManuallyEdited: false,

    init: function() {
      var self = this;
      
      // Wait a bit for DOM to be fully ready
      setTimeout(function() {
        self.elements.titleInput = Utils.getElement('news-title');
        self.elements.coverImageInput = Utils.getElement('news-cover-image');
        
        if (!self.elements.titleInput && !self.elements.coverImageInput) return;

        self.initElements();
        self.initPermalink();
        self.initSlugGeneration();
        self.initEditorTabs();
        self.initWordCount();
        self.initMetaDescription();
        self.initFeaturedImage();
      }, 100);
    },

    initElements: function() {
      this.elements.slugInput = Utils.getElement('news-slug');
      this.elements.permalinkDisplay = Utils.getElement('permalink-display');
      this.elements.permalinkEdit = Utils.getElement('permalink-edit');
      this.elements.editPermalinkBtn = Utils.getElement('edit-permalink-btn');
      this.elements.savePermalinkBtn = Utils.getElement('save-permalink-btn');
      this.elements.featuredImagePlaceholder = Utils.getElement('featured-image-placeholder');
      this.elements.featuredImagePreview = Utils.getElement('featured-image-preview');
      this.elements.featuredImagePreviewImg = Utils.getElement('featured-image-preview-img');
      this.elements.removeFeaturedImageBtn = Utils.getElement('remove-featured-image');
      this.elements.editorTabVisual = Utils.getElement('editor-tab-visual');
      this.elements.editorTabCode = Utils.getElement('editor-tab-code');
      this.elements.newsContentEditor = Utils.getElement('news-content-editor');
      this.elements.newsContentCode = Utils.getElement('news-content-code');
      this.elements.newsContentCodeTextarea = Utils.getElement('news-content-code-textarea');
      this.elements.newsContent = Utils.getElement('news-content');
      this.elements.wordCountEl = Utils.getElement('word-count');
      this.elements.metaDescInput = Utils.getElement('meta-description');
      this.elements.metaDescCounter = Utils.getElement('meta-desc-counter');
    },

    initPermalink: function() {
      this.updatePermalinkDisplay();

      if (!this.elements.editPermalinkBtn || !this.elements.permalinkEdit || !this.elements.savePermalinkBtn) return;

      this.elements.editPermalinkBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        if (this.elements.permalinkEdit) {
          this.elements.permalinkEdit.classList.remove(CSS_CLASSES.hidden);
          if (this.elements.slugInput) {
            this.elements.slugInput.focus();
            this.elements.slugInput.select();
          }
        }
      }.bind(this));

      this.elements.savePermalinkBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.savePermalink();
      }.bind(this));

      if (this.elements.slugInput) {
        this.elements.slugInput.addEventListener('keydown', function(e) {
          if (e.key === 'Enter') {
            e.preventDefault();
            if (this.elements.savePermalinkBtn) {
              this.elements.savePermalinkBtn.click();
            }
          }
        }.bind(this));
      }
    },

    savePermalink: function() {
      if (!this.elements.slugInput) return;
      
      var slug = this.elements.slugInput.value.trim();
      if (slug) {
        slug = Utils.formatSlug(slug);
        if (!slug) slug = 'slug-se-chua-co';
      } else {
        slug = 'slug-se-chua-co';
      }
      
      this.elements.slugInput.value = slug;
      this.updatePermalinkDisplay();
      this.slugManuallyEdited = true;
      
      if (this.elements.permalinkEdit) {
        this.elements.permalinkEdit.classList.add(CSS_CLASSES.hidden);
      }
    },

    updatePermalinkDisplay: function() {
      if (!this.elements.permalinkDisplay || !this.elements.slugInput) return;
      var slug = this.elements.slugInput.value.trim() || 'slug-se-chua-co';
      this.elements.permalinkDisplay.textContent = '/news/' + slug;
    },

    initSlugGeneration: function() {
      if (!this.elements.titleInput || !this.elements.slugInput) return;

      this.elements.titleInput.addEventListener('input', function() {
        if (!this.slugManuallyEdited && this.elements.slugInput) {
          var title = this.elements.titleInput.value.trim();
          var slug = Utils.formatSlug(title);
          this.elements.slugInput.value = slug;
          this.updatePermalinkDisplay();
        }
      }.bind(this));

      this.elements.slugInput.addEventListener('input', function() {
        this.slugManuallyEdited = true;
        this.updatePermalinkDisplay();
      }.bind(this));

      this.elements.slugInput.addEventListener('blur', function() {
        var slug = Utils.formatSlug(this.elements.slugInput.value.trim());
        this.elements.slugInput.value = slug;
        this.updatePermalinkDisplay();
      }.bind(this));
    },

    initEditorTabs: function() {
      var self = this;
      var retries = 0;
      
      function trySetup() {
        // Refresh elements before checking
        self.elements.editorTabVisual = Utils.getElement('editor-tab-visual');
        self.elements.editorTabCode = Utils.getElement('editor-tab-code');
        self.elements.newsContentEditor = Utils.getElement('news-content-editor');
        self.elements.newsContentCode = Utils.getElement('news-content-code');
        self.elements.newsContentCodeTextarea = Utils.getElement('news-content-code-textarea');
        self.elements.newsContent = Utils.getElement('news-content');
        
        if (self.elements.editorTabVisual && self.elements.editorTabCode && 
            self.elements.newsContentEditor && self.elements.newsContentCode) {
          if (self.setupEditorTabs()) {
            console.log('Editor tabs initialized successfully');
            return true;
          }
        }
        
        retries++;
        if (retries < CONFIG.RETRY_MAX) {
          setTimeout(trySetup, CONFIG.RETRY_DELAY);
          return false;
        }
        
        // Fallback to delegation
        console.log('Using event delegation fallback for editor tabs');
        self.setupEditorTabsDelegation();
        return false;
      }
      
      // Also setup delegation immediately as backup
      this.setupEditorTabsDelegation();
      
      // Try direct setup
      trySetup();
    },

    setupEditorTabs: function() {
      var visualTab = this.elements.editorTabVisual;
      var codeTab = this.elements.editorTabCode;
      var contentEditor = this.elements.newsContentEditor;
      var contentCode = this.elements.newsContentCode;

      if (!visualTab || !codeTab || !contentEditor || !contentCode) {
        return false;
      }

      var self = this;
      
      // Check if already initialized
      if (visualTab.dataset.tabInitialized === 'true') {
        return true;
      }
      
      // Mark as initialized
      visualTab.dataset.tabInitialized = 'true';
      codeTab.dataset.tabInitialized = 'true';
      
      function handleVisualClick(e) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        console.log('Visual tab clicked');
        self.switchToVisual();
      }
      
      function handleCodeClick(e) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        console.log('Code tab clicked');
        self.switchToCode();
      }
      
      function handleVisualMousedown(e) {
        e.preventDefault();
        console.log('Visual tab mousedown');
        self.switchToVisual();
      }
      
      function handleCodeMousedown(e) {
        e.preventDefault();
        console.log('Code tab mousedown');
        self.switchToCode();
      }
      
      visualTab.addEventListener('click', handleVisualClick, true);
      codeTab.addEventListener('click', handleCodeClick, true);
      visualTab.addEventListener('mousedown', handleVisualMousedown);
      codeTab.addEventListener('mousedown', handleCodeMousedown);

      return true;
    },

    setupEditorTabsDelegation: function() {
      var tabContainer = Utils.querySelector('.border-b.border-gray-300');
      if (!tabContainer) {
        console.warn('Tab container not found for delegation');
        return;
      }

      var self = this;
      
      // Refresh elements
      self.elements.editorTabVisual = Utils.getElement('editor-tab-visual');
      self.elements.editorTabCode = Utils.getElement('editor-tab-code');
      self.elements.newsContentEditor = Utils.getElement('news-content-editor');
      self.elements.newsContentCode = Utils.getElement('news-content-code');
      self.elements.newsContentCodeTextarea = Utils.getElement('news-content-code-textarea');
      self.elements.newsContent = Utils.getElement('news-content');
      
      tabContainer.addEventListener('click', function(e) {
        var target = e.target.closest('button[id^="editor-tab-"]');
        if (!target) return;
        e.preventDefault();
        e.stopPropagation();
        console.log('Tab clicked via delegation:', target.id);
        
        if (target.id === 'editor-tab-visual') {
          self.switchToVisual();
        } else if (target.id === 'editor-tab-code') {
          self.switchToCode();
        }
      });
      
      console.log('Editor tabs delegation setup complete');
    },

    switchToVisual: function() {
      var visualTab = this.elements.editorTabVisual;
      var codeTab = this.elements.editorTabCode;
      var contentEditor = this.elements.newsContentEditor;
      var contentCode = this.elements.newsContentCode;
      var contentCodeTextarea = this.elements.newsContentCodeTextarea;
      var contentHidden = this.elements.newsContent;

      if (!visualTab || !codeTab || !contentEditor || !contentCode) {
        console.warn('Missing elements for switchToVisual');
        return;
      }

      // Update tab styles - add classes one by one
      var activeClasses = CSS_CLASSES.activeTab.split(' ');
      activeClasses.forEach(function(cls) {
        visualTab.classList.add(cls);
        codeTab.classList.remove(cls);
      });
      visualTab.classList.remove(CSS_CLASSES.inactiveTab);
      codeTab.classList.add(CSS_CLASSES.inactiveTab);
      
      // Show visual editor, hide code editor
      contentEditor.classList.remove(CSS_CLASSES.hidden);
      contentCode.classList.add(CSS_CLASSES.hidden);
      
      // Sync code content to Quill editor
      if (contentCodeTextarea && contentHidden) {
        var codeContent = contentCodeTextarea.value || '';
        contentHidden.value = codeContent;
        
        // Wait for Quill to be ready
        var self = this;
        var retries = 0;
        function syncToQuill() {
          if (window.newsQuillEditor && window.newsQuillEditor.root) {
            try {
              var currentContent = window.newsQuillEditor.root.innerHTML || '';
              // Only update if content differs to avoid unnecessary updates
              if (currentContent !== codeContent) {
                window.newsQuillEditor.root.innerHTML = codeContent;
                if (contentHidden) {
                  contentHidden.value = window.newsQuillEditor.root.innerHTML;
                }
              }
            } catch (e) {
              console.warn('Could not sync code to editor:', e);
              try {
                window.newsQuillEditor.setText(codeContent);
                if (contentHidden) {
                  contentHidden.value = window.newsQuillEditor.root.innerHTML;
                }
              } catch (e2) {
                console.error('Failed to set editor content:', e2);
              }
            }
          } else if (retries < 10) {
            retries++;
            setTimeout(syncToQuill, 100);
          }
        }
        setTimeout(syncToQuill, 100);
      }
    },

    switchToCode: function() {
      var visualTab = this.elements.editorTabVisual;
      var codeTab = this.elements.editorTabCode;
      var contentEditor = this.elements.newsContentEditor;
      var contentCode = this.elements.newsContentCode;
      var contentCodeTextarea = this.elements.newsContentCodeTextarea;
      var contentHidden = this.elements.newsContent;

      if (!visualTab || !codeTab || !contentEditor || !contentCode) {
        console.warn('Missing elements for switchToCode');
        return;
      }

      // Update tab styles - add classes one by one
      var activeClasses = CSS_CLASSES.activeTab.split(' ');
      activeClasses.forEach(function(cls) {
        codeTab.classList.add(cls);
        visualTab.classList.remove(cls);
      });
      codeTab.classList.remove(CSS_CLASSES.inactiveTab);
      visualTab.classList.add(CSS_CLASSES.inactiveTab);
      
      // Show code editor, hide visual editor
      contentCode.classList.remove(CSS_CLASSES.hidden);
      contentEditor.classList.add(CSS_CLASSES.hidden);
      
      // Sync Quill editor content to code textarea
      if (contentHidden && contentCodeTextarea) {
        var editorContent = '';
        
        // Try to get content from Quill first, fallback to hidden input
        if (window.newsQuillEditor && window.newsQuillEditor.root) {
          try {
            editorContent = window.newsQuillEditor.root.innerHTML || '';
            // Ensure hidden input is also updated
            if (contentHidden) {
              contentHidden.value = editorContent;
            }
          } catch (e) {
            console.warn('Could not get editor content:', e);
            editorContent = contentHidden.value || '';
          }
        } else {
          // Quill not ready, use hidden input value
          editorContent = contentHidden.value || '';
        }
        
        // Update both hidden input and textarea
        contentHidden.value = editorContent;
        contentCodeTextarea.value = editorContent;
        
        setTimeout(function() {
          if (contentCodeTextarea) {
            contentCodeTextarea.focus();
            // Scroll to top of textarea
            contentCodeTextarea.scrollTop = 0;
          }
        }, 50);
      }
    },

    initWordCount: function() {
      if (!this.elements.wordCountEl || !this.elements.newsContent) return;

      var self = this;
      function updateWordCount() {
        var content = '';
        // Try to get content from Quill editor first, fallback to hidden input
        if (window.newsQuillEditor && window.newsQuillEditor.root) {
          try {
            content = window.newsQuillEditor.root.innerHTML || '';
          } catch (e) {
            content = self.elements.newsContent.value || '';
          }
        } else {
          content = self.elements.newsContent.value || '';
        }
        var text = content.replace(/<[^>]*>/g, '').trim();
        var words = text ? text.split(/\s+/).filter(function(w) { return w.length > 0; }).length : 0;
        self.elements.wordCountEl.textContent = 'Word count: ' + words;
      }

      this.elements.newsContent.addEventListener('input', updateWordCount);
      
      // Listen to Quill editor changes
      setTimeout(function() {
        if (window.newsQuillEditor) {
          window.newsQuillEditor.on('text-change', function() {
            setTimeout(updateWordCount, 100);
          });
        } else {
          // Fallback: try to find Quill editor element
          var quillEditor = Utils.querySelector('#news-content-editor .ql-editor');
          if (quillEditor) {
            quillEditor.addEventListener('input', function() {
              setTimeout(updateWordCount, 100);
            });
          }
        }
      }, 500);
      
      updateWordCount();
    },

    initMetaDescription: function() {
      if (!this.elements.metaDescInput || !this.elements.metaDescCounter) return;

      var self = this;
      function updateCounter() {
        var length = self.elements.metaDescInput.value.length;
        self.elements.metaDescCounter.textContent = length + '/' + CONFIG.META_DESC_MAX;
        if (length > CONFIG.META_DESC_MAX) {
          self.elements.metaDescCounter.classList.add('text-red-600');
          self.elements.metaDescCounter.classList.remove('text-gray-400');
        } else {
          self.elements.metaDescCounter.classList.remove('text-red-600');
          self.elements.metaDescCounter.classList.add('text-gray-400');
        }
      }

      this.elements.metaDescInput.addEventListener('input', updateCounter);
      updateCounter();
    },

    initFeaturedImage: function() {
      if (!this.elements.coverImageInput) return;

      var self = this;
      var debouncedUpdate = Utils.debounce(function() {
        self.updateFeaturedImagePreview();
      }, CONFIG.PREVIEW_DEBOUNCE);

      this.elements.coverImageInput.addEventListener('input', debouncedUpdate);
      this.elements.coverImageInput.addEventListener('blur', function() {
        clearTimeout(this._previewTimeout);
        self.updateFeaturedImagePreview();
      });
      this.elements.coverImageInput.addEventListener('paste', function() {
        setTimeout(function() {
          self.updateFeaturedImagePreview();
        }, 100);
      });

      if (this.elements.removeFeaturedImageBtn) {
        this.elements.removeFeaturedImageBtn.addEventListener('click', function(e) {
          e.preventDefault();
          self.elements.coverImageInput.value = '';
          self.updateFeaturedImagePreview();
          self.elements.coverImageInput.focus();
        });
      }

      if (this.elements.featuredImagePreviewImg) {
        this.elements.featuredImagePreviewImg.addEventListener('error', function() {
          self.handleImageError();
        });
        this.elements.featuredImagePreviewImg.addEventListener('load', function() {
          self.handleImageLoad();
        });
      }

      setTimeout(function() {
        if (self.elements.coverImageInput.value && self.elements.coverImageInput.value.trim()) {
          self.updateFeaturedImagePreview();
        }
      }, 200);
    },

    updateFeaturedImagePreview: function() {
      if (!this.elements.coverImageInput || !this.elements.featuredImagePlaceholder || 
          !this.elements.featuredImagePreview || !this.elements.featuredImagePreviewImg) {
        return;
      }
      
      var imageUrl = this.elements.coverImageInput.value.trim();
      
      if (!imageUrl) {
        this.elements.featuredImagePlaceholder.classList.remove(CSS_CLASSES.hidden);
        this.elements.featuredImagePreview.classList.add(CSS_CLASSES.hidden);
        this.elements.coverImageInput.classList.remove('border-red-500');
        return;
      }
      
      if (Utils.isValidUrlFormat(imageUrl)) {
        this.elements.featuredImagePreviewImg.src = imageUrl;
        this.elements.featuredImagePlaceholder.classList.add(CSS_CLASSES.hidden);
        this.elements.featuredImagePreview.classList.remove(CSS_CLASSES.hidden);
        this.elements.coverImageInput.classList.remove('border-red-500');
      } else {
        this.elements.featuredImagePlaceholder.classList.remove(CSS_CLASSES.hidden);
        this.elements.featuredImagePreview.classList.add(CSS_CLASSES.hidden);
        this.elements.coverImageInput.classList.add('border-red-500');
      }
    },

    handleImageError: function() {
      if (this.elements.featuredImagePlaceholder) {
        this.elements.featuredImagePlaceholder.classList.remove(CSS_CLASSES.hidden);
        var placeholderText = this.elements.featuredImagePlaceholder.querySelector('span');
        if (placeholderText) {
          var originalText = placeholderText.textContent || 'Chưa có ảnh';
          placeholderText.textContent = 'Không thể tải ảnh';
          placeholderText.classList.add('text-red-500');
          setTimeout(function() {
            placeholderText.textContent = originalText;
            placeholderText.classList.remove('text-red-500');
          }, 3000);
        }
      }
      if (this.elements.featuredImagePreview) {
        this.elements.featuredImagePreview.classList.add(CSS_CLASSES.hidden);
      }
      if (this.elements.coverImageInput) {
        this.elements.coverImageInput.classList.add('border-red-500');
        setTimeout(function() {
          this.elements.coverImageInput.classList.remove('border-red-500');
        }.bind(this), 3000);
      }
    },

    handleImageLoad: function() {
      if (this.elements.featuredImagePlaceholder) {
        this.elements.featuredImagePlaceholder.classList.add(CSS_CLASSES.hidden);
      }
      if (this.elements.featuredImagePreview) {
        this.elements.featuredImagePreview.classList.remove(CSS_CLASSES.hidden);
      }
      if (this.elements.coverImageInput) {
        this.elements.coverImageInput.classList.remove('border-red-500');
      }
    }
  };

  // ============================================================================
  // BULK DELETE MODULE
  // ============================================================================
  var BulkDelete = {
    elements: {},

    init: function() {
      this.elements.selectAll = Utils.getElement('select-all-news');
      this.elements.bulkActions = Utils.getElement('bulk-actions');
      
      if (!this.elements.selectAll || !this.elements.bulkActions) return;

      this.initElements();
      this.attachEventListeners();
      this.updateBulkActions();
    },

    initElements: function() {
      this.elements.newsCheckboxes = Utils.querySelectorAll('.news-checkbox');
      this.elements.selectedCount = Utils.getElement('selected-count');
      this.elements.bulkDeleteBtn = Utils.getElement('bulk-delete-btn');
      this.elements.bulkCancelBtn = Utils.getElement('bulk-cancel-btn');
      this.elements.bulkDeleteForm = Utils.getElement('bulk-delete-form');
    },

    attachEventListeners: function() {
      var self = this;

      if (this.elements.selectAll) {
        this.elements.selectAll.addEventListener('change', function() {
          self.elements.newsCheckboxes.forEach(function(checkbox) {
            checkbox.checked = self.elements.selectAll.checked;
          });
          self.updateBulkActions();
        });
      }

      this.elements.newsCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
          self.updateBulkActions();
        });
      });

      if (this.elements.bulkDeleteBtn) {
        this.elements.bulkDeleteBtn.addEventListener('click', function() {
          self.handleBulkDelete();
        });
      }

      if (this.elements.bulkCancelBtn) {
        this.elements.bulkCancelBtn.addEventListener('click', function() {
          self.cancelSelection();
        });
      }
    },

    updateBulkActions: function() {
      var checked = Utils.querySelectorAll('.news-checkbox:checked');
      var count = checked.length;
      
      if (count > 0) {
        this.elements.bulkActions.classList.remove(CSS_CLASSES.hidden);
        if (this.elements.selectedCount) {
          this.elements.selectedCount.textContent = count + ' mục đã chọn';
        }
        
        if (this.elements.bulkDeleteForm) {
          var oldInputs = this.elements.bulkDeleteForm.querySelectorAll('input[name="news_ids"]');
          oldInputs.forEach(function(input) {
            input.remove();
          });
          
          checked.forEach(function(checkbox) {
            var input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'news_ids';
            input.value = checkbox.value;
            this.elements.bulkDeleteForm.appendChild(input);
          }.bind(this));
        }
      } else {
        this.elements.bulkActions.classList.add(CSS_CLASSES.hidden);
      }
      
      if (this.elements.selectAll) {
        this.elements.selectAll.checked = count === this.elements.newsCheckboxes.length && count > 0;
        this.elements.selectAll.indeterminate = count > 0 && count < this.elements.newsCheckboxes.length;
      }
    },

    handleBulkDelete: function() {
      var checked = Utils.querySelectorAll('.news-checkbox:checked');
      if (checked.length === 0) {
        alert('Vui lòng chọn ít nhất một mục để xóa');
        return;
      }
      
      if (confirm('Bạn có chắc chắn muốn xóa ' + checked.length + ' mục đã chọn không?')) {
        if (this.elements.bulkDeleteForm) {
          this.elements.bulkDeleteForm.submit();
        }
      }
    },

    cancelSelection: function() {
      this.elements.newsCheckboxes.forEach(function(checkbox) {
        checkbox.checked = false;
      });
      if (this.elements.selectAll) {
        this.elements.selectAll.checked = false;
        this.elements.selectAll.indeterminate = false;
      }
      this.updateBulkActions();
    }
  };

  // ============================================================================
  // INITIALIZATION
  // ============================================================================
  function init() {
    Sidebar.init();
    Toast.init();
    ConfirmModal.init();
    FormHandler.init();
    SEOSection.init();
    NewsEditor.init();
    BulkDelete.init();
  }

  // Expose global functions
  window.adminShowToast = Toast.show.bind(Toast);
  window.confirmDelete = DeleteConfirmation.confirmDelete.bind(DeleteConfirmation);

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
