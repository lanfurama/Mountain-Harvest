/**
 * Mountain Harvest - Cart Management
 */

let cart = JSON.parse(localStorage.getItem('cart')) || [];

function saveCart() {
  localStorage.setItem('cart', JSON.stringify(cart));
  renderCart();
}

function addToCart(productId) {
  const product = products.find(p => p.id === productId);
  if (!product) return;

  const existingItem = cart.find(item => item.id === productId);
  if (existingItem) {
    existingItem.quantity += 1;
  } else {
    cart.push({ ...product, quantity: 1 });
  }

  saveCart();
  const t = translations[currentLang];
  showToast(`${t.toast.addedToCart}: "${product.name}"`);
}

function removeFromCart(productId) {
  cart = cart.filter(item => item.id !== productId);
  saveCart();
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
}

function renderCart() {
  const cartCount = document.getElementById('cart-count');
  const cartItems = document.getElementById('cart-items');
  const cartTotal = document.getElementById('cart-total');

  const totalQty = cart.reduce((sum, item) => sum + item.quantity, 0);
  if (cartCount) cartCount.innerText = totalQty;
  if (cartCount) cartCount.classList.toggle('hidden', totalQty === 0);

  if (cartItems) {
    if (cart.length === 0) {
      cartItems.innerHTML = `<div class="text-center text-gray-500 py-4 text-sm">${translations[currentLang].cart.empty}</div>`;
    } else {
      cartItems.innerHTML = cart.map(item => `
            <div class="flex gap-2 group relative">
                <img src="${item.image}" class="w-12 h-12 object-cover rounded">
                <div class="flex-1">
                    <div class="text-xs font-bold truncate">${item.name}</div>
                    <div class="text-xs text-gray-500">${item.quantity} x ${formatCurrency(item.price)}</div>
                </div>
                 <button onclick="removeFromCart(${item.id})" class="text-gray-400 hover:text-red-500 absolute right-0 top-1">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
    }
  }

  if (cartTotal) {
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    cartTotal.innerText = formatCurrency(total);
  }
}
