/**
 * Mountain Harvest - Frontend Logic
 */

// --- Mock Data ---
const products = [
    {
        id: 1,
        name: "Cà Chua Cherry Hữu Cơ",
        category: "Rau củ quả",
        price: 45000,
        originalPrice: 55000,
        image: "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80",
        rating: 4.5,
        reviews: 45,
        isHot: false,
        discount: "-15%",
        tags: ["Organic"],
        description: "Cà chua cherry được trồng theo phương pháp hữu cơ tại nông trại Đà Lạt. Vị ngọt thanh, giòn, giàu vitamin, thích hợp ăn sống hoặc làm salad."
    },
    {
        id: 2,
        name: "Gạo Lứt Đỏ Huyết Rồng",
        category: "Thực phẩm khô",
        price: 80000,
        originalPrice: null,
        unit: "/2kg",
        image: "https://images.unsplash.com/photo-1586201375761-83865001e31c?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80",
        rating: 5,
        reviews: 128,
        isHot: false,
        tags: [],
        description: "Gạo lứt đỏ huyết rồng chứa nhiều chất xơ và khoáng chất. Hạt gạo dài, màu đỏ nâu đặc trưng, khi nấu chín có mùi thơm nhẹ."
    },
    {
        id: 3,
        name: "Cà Phê Arabica Cầu Đất",
        category: "Đồ uống",
        price: 150000,
        originalPrice: null,
        unit: "/500g",
        image: "https://images.unsplash.com/photo-1594631252845-29fc4cc8cde9?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80",
        rating: 4,
        reviews: 89,
        isHot: true,
        tags: ["Best Seller"],
        description: "Hạt cà phê Arabica tuyển chọn từ vùng Cầu Đất. Rang mộc 100%, hương vị chua thanh, hậu ngọt, hương thơm nồng nàn quyến rũ."
    },
    {
        id: 4,
        name: "Nước Giặt Bồ Hòn Tự Nhiên",
        category: "Hoá mỹ phẩm",
        price: 120000,
        originalPrice: null,
        unit: "/Lít",
        image: "https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80",
        rating: 5,
        reviews: 210,
        isHot: false,
        tags: ["Handmade"],
        description: "Nước giặt được chiết xuất từ quả bồ hòn lên men tự nhiên. An toàn lành tính cho da tay và quần áo trẻ em. Khả năng làm sạch hiệu quả."
    }
];

const newsData = [
    {
        id: 1,
        title: "Mùa Thu Hoạch Bơ Sáp 034 Đã Bắt Đầu",
        image: "https://images.unsplash.com/photo-1523049673856-35691f096315?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80",
        summary: "Những trái bơ sáp 034 dẻo, béo ngậy đầu tiên của mùa vụ năm nay đã chính thức lên kệ tại Mountain Harvest.",
        date: "03/02/2026"
    },
    {
        id: 2,
        title: "Bí Quyết Giữ Rau Củ Tươi Lâu Trong Tủ Lạnh",
        image: "https://images.unsplash.com/photo-1566385101042-1a0aa0c1268c?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80",
        summary: "Chia sẻ những mẹo vặt đơn giản nhưng hiệu quả để bảo quản rau củ quả luôn tươi ngon suốt cả tuần.",
        date: "01/02/2026"
    },
    {
        id: 3,
        title: "Chương Trình 'Chung Tay Vì Môi Trường Xanh'",
        image: "https://images.unsplash.com/photo-1542601906990-24ccd08d7455?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80",
        summary: "Mountain Harvest cam kết giảm thiểu rác thải nhựa bằng việc sử dụng bao bì lá chuối và túi giấy tái chế.",
        date: "28/01/2026"
    },
    {
        id: 4,
        title: "Lễ Hội Trái Cây Miền Nhiệt Đới Sắp Diễn Ra",
        image: "https://images.unsplash.com/photo-1610832958506-aa56368176cf?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80",
        summary: "Cùng hòa mình vào không khí sôi động của lễ hội trái cây với hơn 50 loại đặc sản vùng miền quy tụ.",
        date: "25/01/2026"
    },
    {
        id: 5,
        title: "Cách Làm Salad Cầu Vồng Tốt Cho Sức Khỏe",
        image: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80",
        summary: "Công thức salad đơn giản, giàu vitamin với sự kết hợp của 7 loại rau củ quả nhiều màu sắc.",
        date: "20/01/2026"
    },
    {
        id: 6,
        title: "Mountain Harvest Đạt Chứng Nhận Organic Quốc Tế",
        image: "https://images.unsplash.com/photo-1621451537084-482c73073a0f?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80",
        summary: "Tự hào là đơn vị tiên phong áp dụng tiêu chuẩn canh tác hữu cơ chuẩn Châu Âu tại Việt Nam.",
        date: "15/01/2026"
    }
];

// --- State Management ---
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// --- Functions ---

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
    showToast(`Đã thêm "${product.name}" vào giỏ hàng`);
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    saveCart();
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
}

// --- Rendering ---

function renderProducts() {
    const container = document.getElementById('product-list');
    if (!container) return;

    container.innerHTML = products.map(product => `
        <div class="bg-white rounded-xl shadow-sm hover:shadow-xl transition duration-300 group overflow-hidden border border-gray-100">
            <div class="relative h-64 overflow-hidden">
                ${product.discount ? `<span class="absolute top-3 left-3 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded z-10">${product.discount}</span>` : ''}
                ${product.tags.map(tag => {
        let colorClass = 'bg-blue-100 text-blue-600';
        if (tag === 'Best Seller') colorClass = 'bg-brand-orange text-white';
        if (tag === 'Organic') colorClass = 'bg-green-100 text-brand-green';
        return `<span class="absolute top-3 right-3 ${colorClass} text-xs font-bold px-2 py-1 rounded z-10 mr-1">${tag}</span>`;
    }).join('')}
                
                <img src="${product.image}" class="w-full h-full object-cover transform group-hover:scale-110 transition duration-500">
                
                <div class="absolute bottom-0 left-0 right-0 bg-white/90 p-2 translate-y-full group-hover:translate-y-0 transition duration-300 flex justify-center gap-2 backdrop-blur-sm">
                    <button class="p-2 rounded-full bg-gray-100 hover:bg-brand-green hover:text-white transition" title="Xem nhanh" onclick="openProductModal(${product.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                </div>
            </div>
            <div class="p-4">
                <div class="text-xs text-gray-500 mb-1">${product.category}</div>
                <h3 class="font-bold text-lg text-gray-800 hover:text-brand-green cursor-pointer truncate" onclick="openProductModal(${product.id})">${product.name}</h3>
                <div class="flex items-center my-2">
                    <div class="flex text-yellow-400 text-xs">
                        ${Array(5).fill(0).map((_, i) =>
        i < Math.floor(product.rating) ? '<i class="fas fa-star"></i>' :
            (i < product.rating ? '<i class="fas fa-star-half-alt"></i>' : '<i class="far fa-star"></i>')
    ).join('')}
                    </div>
                    <span class="text-xs text-gray-400 ml-2">(${product.reviews} đánh giá)</span>
                </div>
                <div class="flex justify-between items-center mt-3">
                    <div>
                        <span class="text-lg font-bold text-brand-green">${formatCurrency(product.price)}</span>
                        ${product.originalPrice ? `<span class="text-sm text-gray-400 line-through ml-2">${formatCurrency(product.originalPrice)}</span>` : ''}
                        ${product.unit ? `<span class="text-xs text-gray-500">${product.unit}</span>` : ''}
                    </div>
                    <button onclick="addToCart(${product.id})" class="bg-brand-green text-white p-2 rounded-lg hover:bg-brand-darkGreen transition shadow-lg shadow-green-200">
                        <i class="fas fa-cart-plus"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function renderNews() {
    const container = document.getElementById('news-list');
    if (!container) return;

    container.innerHTML = newsData.map(news => `
        <div class="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition">
            <div class="h-48 overflow-hidden">
                <img src="${news.image}" class="w-full h-full object-cover transform hover:scale-105 transition duration-500">
            </div>
            <div class="p-6">
                <span class="text-xs text-gray-400 mb-2 block"><i class="far fa-calendar-alt mr-1"></i> ${news.date}</span>
                <h3 class="font-bold text-lg mb-2 hover:text-brand-green cursor-pointer">${news.title}</h3>
                <p class="text-gray-600 text-sm mb-4 line-clamp-3">${news.summary}</p>
                <button class="text-brand-green font-bold text-sm hover:underline">Đọc tiếp <i class="fas fa-arrow-right text-xs"></i></button>
            </div>
        </div>
    `).join('');
}

function renderCart() {
    const cartCount = document.getElementById('cart-count');
    const cartItems = document.getElementById('cart-items');
    const cartTotal = document.getElementById('cart-total');

    // Update Badge
    const totalQty = cart.reduce((sum, item) => sum + item.quantity, 0);
    if (cartCount) cartCount.innerText = totalQty;
    if (cartCount) cartCount.classList.toggle('hidden', totalQty === 0);

    // Update Mini Cart Items
    if (cartItems) {
        if (cart.length === 0) {
            cartItems.innerHTML = '<div class="text-center text-gray-500 py-4 text-sm">Giỏ hàng trống</div>';
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

    // Update Total
    if (cartTotal) {
        const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        cartTotal.innerText = formatCurrency(total);
    }
}

// --- Modal Logic ---

function openProductModal(id) {
    const product = products.find(p => p.id === id);
    if (!product) return;

    const modal = document.getElementById('product-modal');
    const content = document.getElementById('modal-content');

    // Populate Modal Content
    content.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div class="h-64 md:h-full rounded-lg overflow-hidden">
                <img src="${product.image}" class="w-full h-full object-cover">
            </div>
            <div>
                <span class="text-sm text-brand-green font-bold bg-green-100 px-2 py-1 rounded-full">${product.category}</span>
                <h2 class="text-2xl font-bold text-gray-800 mt-2 mb-2 font-serif">${product.name}</h2>
                <div class="flex items-center mb-4">
                    <div class="flex text-yellow-400 text-sm">
                        ${Array(5).fill(0).map((_, i) =>
        i < Math.floor(product.rating) ? '<i class="fas fa-star"></i>' :
            (i < product.rating ? '<i class="fas fa-star-half-alt"></i>' : '<i class="far fa-star"></i>')
    ).join('')}
                    </div>
                    <span class="text-sm text-gray-500 ml-2">(${product.reviews} đánh giá)</span>
                </div>
                
                <div class="text-3xl font-bold text-brand-green mb-4">
                    ${formatCurrency(product.price)}
                    ${product.unit ? `<span class="text-base font-normal text-gray-500">${product.unit}</span>` : ''}
                </div>
                
                <p class="text-gray-600 mb-6 leading-relaxed">${product.description}</p>
                
                <div class="flex gap-4">
                     <div class="inline-flex items-center border border-gray-300 rounded-lg">
                        <button class="px-3 py-2 hover:bg-gray-100 text-gray-600 font-bold">-</button>
                        <input type="text" value="1" class="w-12 text-center border-none focus:ring-0 text-sm font-bold">
                        <button class="px-3 py-2 hover:bg-gray-100 text-gray-600 font-bold">+</button>
                    </div>
                    <button onclick="addToCart(${product.id}); closeModal()" class="flex-1 bg-brand-green text-white py-2 rounded-lg font-bold hover:bg-brand-darkGreen transition shadow-lg shadow-green-200">
                        Thêm vào giỏ
                    </button>
                    <button class="p-3 border border-gray-300 rounded-lg text-gray-500 hover:text-red-500 hover:border-red-500 transition">
                        <i class="far fa-heart"></i>
                    </button>
                </div>
            </div>
        </div>
    `;

    modal.classList.remove('hidden');
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = document.getElementById('product-modal');
    modal.classList.add('hidden');
    document.body.style.overflow = '';
}

// --- Toast Notification ---
function showToast(message) {
    // Check if toast container exists, if not create it
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

    // Animate in
    requestAnimationFrame(() => {
        toast.classList.remove('translate-y-10', 'opacity-0');
    });

    // Remove after 3s
    setTimeout(() => {
        toast.classList.add('translate-y-10', 'opacity-0');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
    renderProducts();
    renderNews();
    renderCart();

    // Modal Close Event (Click outside)
    const modal = document.getElementById('product-modal');
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });
});
