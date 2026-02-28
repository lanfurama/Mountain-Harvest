(function() {
  'use strict';

  // Sidebar toggle (mobile)
  var sidebar = document.getElementById('admin-sidebar');
  var overlay = document.getElementById('admin-sidebar-overlay');
  var toggle = document.getElementById('admin-sidebar-toggle');
  if (toggle && sidebar && overlay) {
    function openSidebar() {
      sidebar.classList.remove('-translate-x-full');
      overlay.classList.remove('hidden');
      document.body.style.overflow = 'hidden';
    }
    function closeSidebar() {
      sidebar.classList.add('-translate-x-full');
      overlay.classList.add('hidden');
      document.body.style.overflow = '';
    }
    toggle.addEventListener('click', function() {
      if (sidebar.classList.contains('-translate-x-full')) {
        openSidebar();
      } else {
        closeSidebar();
      }
    });
    overlay.addEventListener('click', closeSidebar);
  }

  // Toast from query params
  var urlParams = new URLSearchParams(window.location.search);
  var successMsg = urlParams.get('success');
  var errorMsg = urlParams.get('error');
  if (successMsg) {
    showToast(successMsg, 'success');
    var u = new URL(window.location);
    u.searchParams.delete('success');
    window.history.replaceState({}, '', u);
  }
  if (errorMsg) {
    showToast(decodeURIComponent(errorMsg), 'error');
    var u2 = new URL(window.location);
    u2.searchParams.delete('error');
    window.history.replaceState({}, '', u2);
  }

  function showToast(msg, type) {
    var el = document.getElementById('admin-toast');
    var progressEl = document.getElementById('admin-toast-progress');
    if (!el) return;
    
    var icons = {
      'success': 'check-circle',
      'error': 'exclamation-circle',
      'warning': 'exclamation-triangle',
      'info': 'info-circle'
    };
    var colors = {
      'success': 'bg-green-600',
      'error': 'bg-red-600',
      'warning': 'bg-yellow-600',
      'info': 'bg-blue-600'
    };
    
    var icon = icons[type] || icons['success'];
    var color = colors[type] || colors['success'];
    
    el.innerHTML = '<div class="flex items-center gap-3"><div class="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center"><i class="fas fa-' + icon + '"></i></div><span class="font-medium">' + msg + '</span></div>';
    if (progressEl) {
      progressEl.style.width = '100%';
      progressEl.style.transition = 'width 3s linear';
    }
    el.className = 'fixed bottom-6 right-6 z-50 flex items-center gap-2 px-5 py-4 rounded-xl shadow-2xl ' + color + ' text-white transform transition-all duration-300 min-w-[300px]';
    el.classList.remove('hidden', 'opacity-0', 'translate-y-4');
    el.style.opacity = '1';
    el.style.transform = 'translateY(0)';
    
    setTimeout(function() {
      if (progressEl) progressEl.style.width = '0%';
      el.style.opacity = '0';
      el.style.transform = 'translateY(1rem)';
      setTimeout(function() {
        el.classList.add('hidden');
        if (progressEl) progressEl.style.width = '100%';
      }, 300);
    }, 3000);
  }
  window.adminShowToast = showToast;

  // Confirm modal
  var confirmModal = document.getElementById('admin-confirm-modal');
  var confirmOverlay = document.getElementById('admin-confirm-overlay');
  var confirmMsg = document.getElementById('admin-confirm-message');
  var confirmCancel = document.getElementById('admin-confirm-cancel');
  var confirmOk = document.getElementById('admin-confirm-ok');
  var pendingAction = null;

  if (confirmModal && confirmCancel && confirmOk) {
    confirmCancel.textContent = 'Hủy';
    confirmOk.textContent = 'Xác nhận';
    confirmCancel.addEventListener('click', closeConfirm);
    if (confirmOverlay) confirmOverlay.addEventListener('click', closeConfirm);
    confirmOk.addEventListener('click', function() {
      if (pendingAction) {
        if (pendingAction.form) {
          pendingAction.form.submit();
        } else if (pendingAction.href) {
          window.location.href = pendingAction.href;
        }
        pendingAction = null;
      }
      closeConfirm();
    });
  }


  function openConfirm(msg, formOrHref) {
    if (confirmMsg) confirmMsg.textContent = msg;
    pendingAction = formOrHref || null;
    if (confirmModal) {
      confirmModal.classList.remove('hidden');
      var dialog = document.getElementById('admin-confirm-dialog');
      if (dialog) {
        setTimeout(function() {
          dialog.classList.remove('scale-95', 'opacity-0');
          dialog.classList.add('scale-100', 'opacity-100');
        }, 10);
      }
    }
  }
  
  function closeConfirm() {
    var dialog = document.getElementById('admin-confirm-dialog');
    if (dialog) {
      dialog.classList.remove('scale-100', 'opacity-100');
      dialog.classList.add('scale-95', 'opacity-0');
      setTimeout(function() {
        if (confirmModal) confirmModal.classList.add('hidden');
        pendingAction = null;
      }, 300);
    } else {
      if (confirmModal) confirmModal.classList.add('hidden');
      pendingAction = null;
    }
  }

  // Delegate [data-confirm] clicks
  document.addEventListener('click', function(e) {
    var target = e.target.closest('[data-confirm]');
    if (!target) return;
    e.preventDefault();
    e.stopPropagation();
    var msg = target.getAttribute('data-confirm');
    var form = target.closest('form');
    var href = target.getAttribute('href');
    openConfirm(msg, form ? { form: form } : (href ? { href: href } : null));
  });

  // Form loading state
  document.querySelectorAll('form').forEach(function(form) {
    form.addEventListener('submit', function(e) {
      var btn = form.querySelector('button[type="submit"]');
      if (btn && !btn.disabled) {
        btn.disabled = true;
        var origHtml = btn.innerHTML;
        var origClasses = btn.className;
        btn.className = origClasses + ' opacity-75 cursor-not-allowed';
        btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Đang xử lý...';
        
        // Re-enable after 10 seconds as fallback
        setTimeout(function() {
          btn.disabled = false;
          btn.className = origClasses;
          btn.innerHTML = origHtml;
        }, 10000);
      }
    });
  });
  
  // SEO section toggle
  var seoToggle = document.getElementById('seo-toggle');
  if (seoToggle) {
    seoToggle.addEventListener('click', function() {
      var section = document.getElementById('seo-section');
      var chevron = document.getElementById('seo-chevron');
      if (section && chevron) {
        section.classList.toggle('hidden');
        chevron.classList.toggle('rotate-180');
      }
    });
  }
  
  // Initialize SEO section as hidden
  var seoSection = document.getElementById('seo-section');
  if (seoSection) {
    seoSection.classList.add('hidden');
  }
})();
