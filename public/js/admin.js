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
    if (!el) return;
    el.innerHTML = '<i class="fas fa-' + (type === 'error' ? 'exclamation-circle' : 'check-circle') + '"></i> <span>' + msg + '</span>';
    el.className = 'fixed bottom-4 right-4 z-50 flex items-center gap-2 px-4 py-3 rounded-lg shadow-lg ' +
      (type === 'error' ? 'bg-red-600' : 'bg-[#2F5233]') + ' text-white transform transition-all duration-300';
    el.classList.remove('hidden');
    setTimeout(function() {
      el.classList.add('opacity-0', 'translate-y-4');
      setTimeout(function() {
        el.classList.add('hidden');
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

  function closeConfirm() {
    if (confirmModal) confirmModal.classList.add('hidden');
    pendingAction = null;
  }

  function openConfirm(msg, formOrHref) {
    if (confirmMsg) confirmMsg.textContent = msg;
    pendingAction = formOrHref || null;
    if (confirmModal) confirmModal.classList.remove('hidden');
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
    form.addEventListener('submit', function() {
      var btn = form.querySelector('button[type="submit"]');
      if (btn && !btn.disabled) {
        btn.disabled = true;
        var origHtml = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Đang lưu...';
        setTimeout(function() {
          btn.disabled = false;
          btn.innerHTML = origHtml;
        }, 5000);
      }
    });
  });
})();
