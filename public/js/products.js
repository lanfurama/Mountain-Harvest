/**
 * Mountain Harvest - Products Management
 */

const PRODUCTS_PER_PAGE = 8;
let products = [];
let productsPage = 1, productsTotal = 0, productsTotalPages = 0;
let productsLoading = false;

function getFilterState() {
  const searchEl = document.getElementById('filter-search');
  return {
    search: (searchEl && searchEl.value && searchEl.value.trim()) || '',
    category: (document.getElementById('filter-category') && document.getElementById('filter-category').value) || '',
    price: (document.getElementById('filter-price') && document.getElementById('filter-price').value) || '',
    standard: (document.getElementById('filter-standard') && document.getElementById('filter-standard').value) || '',
    sort: (document.getElementById('filter-sort') && document.getElementById('filter-sort').value) || 'newest',
  };
}

function buildProductsUrl(page) {
  const f = getFilterState();
  const params = new URLSearchParams({ page: String(page), limit: String(PRODUCTS_PER_PAGE), sort: f.sort });
  if (f.search) params.set('search', f.search);
  if (f.category) params.set('category', f.category);
  if (f.price) params.set('price', f.price);
  if (f.standard) params.set('standard', f.standard);
  return '/api/products?' + params.toString();
}

function showProductsLoading() {
  const container = document.getElementById('product-list');
  if (!container) return;
  container.innerHTML = Array(PRODUCTS_PER_PAGE).fill(0).map(() => `
    <div class="skeleton-card">
      <div class="skeleton skeleton-image"></div>
      <div class="skeleton skeleton-text"></div>
      <div class="skeleton skeleton-text skeleton-text-sm"></div>
      <div class="skeleton skeleton-text" style="width: 40%; margin-top: 1rem;"></div>
    </div>
  `).join('');
}

async function loadProducts(page) {
  if (productsLoading) return;
  productsLoading = true;
  
  showProductsLoading();
  setPaginationLoading(true);
  
  try {
    const res = await fetch(buildProductsUrl(page));
    const data = res.ok ? await res.json() : {};
    products = Array.isArray(data.items) ? data.items : [];
    productsTotal = typeof data.total === 'number' ? data.total : products.length;
    productsPage = typeof data.page === 'number' ? data.page : 1;
    const limit = typeof data.limit === 'number' ? data.limit : PRODUCTS_PER_PAGE;
    productsTotalPages = typeof data.totalPages === 'number' ? data.totalPages : Math.max(1, Math.ceil(productsTotal / limit));
  } catch (e) {
    console.warn('Products API failed', e);
    products = [];
    productsTotal = 0;
    productsPage = 1;
    productsTotalPages = 1;
  } finally {
    productsLoading = false;
    setPaginationLoading(false);
  }
  
  renderProducts();
  renderProductPagination();
  renderActiveFilters();
}

function setPaginationLoading(loading) {
  const pagination = document.getElementById('product-pagination');
  if (!pagination) return;
  if (loading) {
    pagination.classList.add('pagination-loading');
  } else {
    pagination.classList.remove('pagination-loading');
  }
}

function renderProductPagination() {
  const el = document.getElementById('product-pagination');
  if (!el) return;
  if (productsTotalPages <= 1) {
    el.innerHTML = '';
    return;
  }
  const disabledClass = productsLoading ? ' opacity-50 pointer-events-none' : '';
  const prevDisabled = productsPage <= 1 || productsLoading ? ' opacity-50 pointer-events-none' : '';
  const nextDisabled = productsPage >= productsTotalPages || productsLoading ? ' opacity-50 pointer-events-none' : '';
  
  let html = '<a href="#" data-page="prev" class="inline-flex items-center justify-center w-9 h-9 border border-warm-300 rounded-lg hover:bg-warm-200 text-warm-700 transition' + prevDisabled + '"><i class="fas fa-chevron-left"></i></a>';
  for (let p = 1; p <= productsTotalPages; p++) {
    const active = p === productsPage ? ' bg-brand-green text-white border-brand-green' : ' border-warm-300 hover:bg-warm-200 text-warm-700';
    const disabled = productsLoading && p !== productsPage ? ' opacity-50 pointer-events-none' : '';
    html += '<a href="#" data-page="' + p + '" class="inline-flex items-center justify-center w-9 h-9 border rounded-lg transition' + active + disabled + '">' + p + '</a>';
  }
  html += '<a href="#" data-page="next" class="inline-flex items-center justify-center w-9 h-9 border border-warm-300 rounded-lg hover:bg-warm-200 text-warm-700 transition' + nextDisabled + '"><i class="fas fa-chevron-right"></i></a>';
  el.innerHTML = html;
  el.querySelectorAll('a[data-page]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      if (productsLoading) return;
      const v = a.getAttribute('data-page');
      if (v === 'prev') loadProducts(productsPage - 1);
      else if (v === 'next') loadProducts(productsPage + 1);
      else loadProducts(parseInt(v, 10));
    });
  });
}

function renderActiveFilters() {
  const f = getFilterState();
  const tags = [];
  if (f.category) tags.push({ label: f.category, key: 'category' });
  if (f.price) tags.push({ label: f.price === 'under50' ? 'Dưới 50k' : f.price === '50-200' ? '50k-200k' : 'Trên 200k', key: 'price' });
  if (f.standard) tags.push({ label: f.standard, key: 'standard' });
  const container = document.getElementById('active-filters');
  const tagsEl = document.getElementById('active-filters-tags');
  if (!container || !tagsEl) return;
  if (tags.length === 0) {
    container.classList.add('hidden');
    return;
  }
  container.classList.remove('hidden');
  tagsEl.innerHTML = tags.map(function (t) {
    return '<span class="bg-brand-green/10 text-brand-green px-3 py-1 rounded-full flex items-center gap-1 cursor-pointer hover:bg-brand-green/20 transition" data-clear="' + t.key + '">' + t.label + ' <i class="fas fa-times text-xs"></i></span>';
  }).join('');
  tagsEl.querySelectorAll('[data-clear]').forEach(function (span) {
    span.addEventListener('click', function () {
      const key = span.getAttribute('data-clear');
      const sel = document.getElementById('filter-' + key);
      if (sel) { sel.value = ''; loadProducts(1); }
    });
  });
}

function clearAllFilters() {
  const searchEl = document.getElementById('filter-search');
  if (searchEl) searchEl.value = '';
  ['filter-category', 'filter-price', 'filter-standard'].forEach(function (id) {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  const sortEl = document.getElementById('filter-sort');
  if (sortEl) sortEl.value = 'newest';
  loadProducts(1);
}

function renderProducts() {
  const container = document.getElementById('product-list');
  if (!container) return;
  const list = Array.isArray(products) ? products : [];
  const tags = (p) => Array.isArray(p.tags) ? p.tags : [];

  container.innerHTML = list.map(product => `
    <div class="bg-warm-50 rounded-xl shadow-ring hover:shadow-lift transition duration-300 group overflow-hidden border border-warm-200">
        <div class="relative h-64 overflow-hidden bg-white">
            ${product.discount ? `<span class="absolute top-3 left-3 bg-brand-terracotta text-white text-xs font-semibold px-2.5 py-1 rounded-full z-10">${product.discount}</span>` : ''}
            <div class="absolute top-3 right-3 z-10 flex flex-col gap-1.5">
              ${tags(product).map(tag => {
    let colorClass = 'bg-warm-300/80 text-warm-800';
    if (tag === 'Best Seller') colorClass = 'bg-brand-terracotta/90 text-white';
    if (tag === 'Organic') colorClass = 'bg-brand-green/90 text-white';
    return `<span class="${colorClass} text-xs font-semibold px-2.5 py-1 rounded-full backdrop-blur-sm">${tag}</span>`;
  }).join('')}
            </div>

            <img src="${product.image}" class="w-full h-full object-cover transform group-hover:scale-105 transition duration-500" onerror="handleImageError(this)">

            <div class="absolute bottom-0 left-0 right-0 bg-warm-50/90 p-2 translate-y-full group-hover:translate-y-0 transition duration-300 flex justify-center gap-2 backdrop-blur-sm border-t border-warm-200">
                <button class="p-2 rounded-lg bg-warm-200 hover:bg-brand-green hover:text-white transition text-warm-700" title="Xem nhanh" onclick="openProductModal(${product.id})">
                    <i class="fas fa-eye"></i>
                </button>
            </div>
        </div>
        <div class="p-4">
            <div class="text-xs text-warm-600 mb-1 font-medium uppercase tracking-wide">${product.category}</div>
            <h3 class="font-semibold text-base text-warm-900 hover:text-brand-green cursor-pointer truncate leading-snug" onclick="openProductModal(${product.id})">${product.name}</h3>
            <div class="flex items-center my-2">
                <div class="flex text-amber-400 text-xs gap-0.5">
                    ${Array(5).fill(0).map((_, i) =>
    i < Math.floor(product.rating) ? '<i class="fas fa-star"></i>' :
      (i < product.rating ? '<i class="fas fa-star-half-alt"></i>' : '<i class="far fa-star text-warm-300"></i>')
  ).join('')}
                </div>
                <span class="text-xs text-warm-500 ml-2">(${product.reviews})</span>
            </div>
            <div class="flex justify-between items-center mt-3 pt-3 border-t border-warm-200">
                <div>
                    <span class="text-lg font-bold text-brand-terracotta">${formatCurrency(product.price)}</span>
                    ${product.originalPrice ? `<span class="text-sm text-warm-500 line-through ml-1">${formatCurrency(product.originalPrice)}</span>` : ''}
                    ${product.unit ? `<span class="text-xs text-warm-500 ml-1">${product.unit}</span>` : ''}
                </div>
                <button onclick="addToCart(${product.id})" class="bg-brand-green text-white p-2 rounded-lg hover:bg-brand-darkGreen transition">
                    <i class="fas fa-cart-plus"></i>
                </button>
            </div>
        </div>
    </div>
`).join('');
}

function openProductModal(id) {
  const product = products.find(p => p.id === id);
  if (!product) return;

  const modal = document.getElementById('product-modal');
  const content = document.getElementById('modal-content');

  content.innerHTML = `
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div class="h-64 md:h-full rounded-xl overflow-hidden bg-white">
            <img src="${product.image}" class="w-full h-full object-cover" onerror="handleImageError(this)">
        </div>
        <div>
            <span class="text-xs text-brand-green font-semibold bg-brand-green/10 px-3 py-1.5 rounded-full uppercase tracking-wide">${product.category}</span>
            <h2 class="text-2xl font-medium text-warm-950 mt-3 mb-2" style="font-family:'Playfair Display',Georgia,serif;">${product.name}</h2>
            <div class="flex items-center mb-4">
                <div class="flex text-amber-400 text-sm gap-0.5">
                    ${Array(5).fill(0).map((_, i) =>
    i < Math.floor(product.rating) ? '<i class="fas fa-star"></i>' :
      (i < product.rating ? '<i class="fas fa-star-half-alt"></i>' : '<i class="far fa-star text-warm-300"></i>')
  ).join('')}
                </div>
                <span class="text-sm text-warm-600 ml-2">(${product.reviews} đánh giá)</span>
            </div>

            <div class="text-3xl font-bold text-brand-terracotta mb-4">
                ${formatCurrency(product.price)}
                ${product.unit ? `<span class="text-base font-normal text-warm-600 ml-1">${product.unit}</span>` : ''}
            </div>

            <p class="text-warm-700 mb-6 leading-relaxed">${product.description}</p>

            <div class="flex gap-3">
                 <div class="inline-flex items-center border border-warm-300 rounded-lg">
                    <button class="px-3 py-2 hover:bg-warm-100 text-warm-700 font-semibold">-</button>
                    <input type="text" value="1" class="w-12 text-center border-none focus:ring-0 text-sm font-semibold">
                    <button class="px-3 py-2 hover:bg-warm-100 text-warm-700 font-semibold">+</button>
                </div>
                <button onclick="addToCart(${product.id}); closeModal()" class="flex-1 bg-brand-green text-white py-2 rounded-lg font-semibold hover:bg-brand-darkGreen transition">
                    Thêm vào giỏ
                </button>
                <button class="p-3 border border-warm-300 rounded-lg text-warm-500 hover:text-red-500 hover:border-red-400 transition">
                    <i class="far fa-heart"></i>
                </button>
            </div>
        </div>
    </div>
`;

  // Add Product structured data (JSON-LD)
  const productSchema = {
    "@context": "https://schema.org",
    "@type": "Product",
    "name": product.name,
    "description": product.description || product.name,
    "image": product.image || "",
    "category": product.category,
    "brand": {
      "@type": "Brand",
      "name": "Mountain Harvest"
    },
    "offers": {
      "@type": "Offer",
      "price": product.price,
      "priceCurrency": "VND",
      "availability": "https://schema.org/InStock"
    },
    "aggregateRating": product.rating > 0 ? {
      "@type": "AggregateRating",
      "ratingValue": product.rating,
      "reviewCount": product.reviews || 0
    } : undefined
  };
  
  // Remove undefined fields
  if (!productSchema.aggregateRating) {
    delete productSchema.aggregateRating;
  }
  
  // Remove existing product schema if any
  const existingSchema = document.querySelector('script[data-product-schema]');
  if (existingSchema) {
    existingSchema.remove();
  }
  
  // Add new schema
  const schemaScript = document.createElement('script');
  schemaScript.type = 'application/ld+json';
  schemaScript.setAttribute('data-product-schema', 'true');
  schemaScript.textContent = JSON.stringify(productSchema);
  document.head.appendChild(schemaScript);

  modal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  const modal = document.getElementById('product-modal');
  modal.classList.add('hidden');
  document.body.style.overflow = '';
}
