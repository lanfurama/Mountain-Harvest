/**
 * Mountain Harvest - Main Application Logic (SSR-first)
 */

// Global fallback image for broken images
const FALLBACK_IMAGE_URL = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQoSsSHOOZkAWEtkYVziWjdfYurLpB8l4Ue6Q&s';

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

// Initialize - all critical content is already server-side rendered
document.addEventListener('DOMContentLoaded', () => {
  if (typeof applyLanguage === 'function') applyLanguage();
  if (typeof updateLanguageButtons === 'function') updateLanguageButtons();
  if (typeof renderCart === 'function') renderCart();
});
