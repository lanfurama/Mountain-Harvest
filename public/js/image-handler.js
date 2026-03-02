/**
 * Mountain Harvest - Image Error Handler
 * Must be loaded FIRST before any HTML with images
 */

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
  
  // Make globally available IMMEDIATELY
  if (typeof window !== 'undefined') {
    window.handleImageError = handleImageError;
  }
  if (typeof globalThis !== 'undefined') {
    globalThis.handleImageError = handleImageError;
  }
  // Fallback for very old environments
  if (typeof global !== 'undefined') {
    global.handleImageError = handleImageError;
  }
})();
