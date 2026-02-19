export const translations = {
  en: {
    topbar: {
      freeShipping: "Free shipping for orders over 500k",
      hotline: "Hotline: 1900 1234",
      support: "Customer Support",
    },
    nav: {
      account: "Account",
      cart: "Cart",
      fresh: "Fresh",
      dry: "Dry Food",
      beverage: "Beverages",
      cosmetics: "Cosmetics",
    },
    search: {
      placeholder: "Search products...",
      all: "All",
      agricultural: "Agricultural Products",
      essentials: "Essentials",
      button: "Search",
    },
    cart: {
      title: "Your Cart",
      loading: "Loading...",
      empty: "Cart is empty",
      total: "Total:",
      checkout: "Checkout Now",
    },
    hero: {
      promo: "Summer Sale",
      title: "Fresh Produce <br> For Green Living",
      subtitle: "Up to 20% off on vegetables and fruits this week.",
      button: "Shop Now",
    },
    filter: {
      title: "Product Filters",
    },
    products: {
      featured: "Featured Products",
      subtitle: "Best selection from Mountain Harvest farm",
      viewAll: "View All",
    },
    category: {
      fresh: {
        title: "Fresh Produce",
        desc: "Harvested from Da Lat farms, delivered same day to ensure freshness.",
        button: "Shop Now",
      },
      essentials: {
        title: "Green Essentials",
        desc: "Natural home care products, safe for children.",
        button: "Explore",
      },
    },
    newsletter: {
      title: "Subscribe to Promotions",
      subtitle: "Get 10% off your first order and updates on fresh produce.",
      placeholder: "Enter your email...",
      button: "Subscribe",
    },
    toast: {
      addedToCart: "Added to cart",
    },
  },
  vi: {
    topbar: {
      freeShipping: "Miễn phí vận chuyển cho đơn hàng từ 500k",
      hotline: "Hotline: 1900 1234",
      support: "Hỗ trợ khách hàng",
    },
    nav: {
      account: "Tài khoản",
      cart: "Giỏ hàng",
      fresh: "Tươi sống",
      dry: "Thực phẩm khô",
      beverage: "Đồ uống",
      cosmetics: "Hoá mỹ phẩm",
    },
    search: {
      placeholder: "Tìm sản phẩm (vd: Cà chua, Gạo, Nước giặt...)",
      all: "Tất cả",
      agricultural: "Nông sản",
      essentials: "Nhu yếu phẩm",
      button: "Tìm",
    },
    cart: {
      title: "Giỏ hàng của bạn",
      loading: "Đang tải...",
      empty: "Giỏ hàng trống",
      total: "Tổng cộng:",
      checkout: "Thanh toán ngay",
    },
    hero: {
      promo: "Khuyến mãi mùa hè",
      title: "Nông Sản Sạch <br> Cho Cuộc Sống Xanh",
      subtitle: "Giảm giá đến 20% cho các đơn hàng Rau củ quả trong tuần này.",
      button: "Mua Ngay",
    },
    filter: {
      title: "Bộ lọc sản phẩm",
    },
    products: {
      featured: "Sản Phẩm Nổi Bật",
      subtitle: "Lựa chọn tốt nhất từ nông trại Mountain Harvest",
      viewAll: "Xem tất cả",
    },
    category: {
      fresh: {
        title: "Nông Sản Tươi",
        desc: "Thu hoạch từ nông trại Đà Lạt, vận chuyển trong ngày để đảm bảo độ tươi ngon.",
        button: "Mua ngay",
      },
      essentials: {
        title: "Nhu Yếu Phẩm Xanh",
        desc: "Sản phẩm chăm sóc nhà cửa từ thiên nhiên, an toàn cho cả trẻ nhỏ.",
        button: "Khám phá",
      },
    },
    newsletter: {
      title: "Đăng Ký Nhận Tin Khuyến Mãi",
      subtitle: "Nhận mã giảm giá 10% cho đơn hàng đầu tiên và cập nhật tin tức về nông sản sạch.",
      placeholder: "Nhập địa chỉ email của bạn...",
      button: "Đăng ký",
    },
    toast: {
      addedToCart: "Đã thêm vào giỏ hàng",
    },
  },
};

export type Language = "en" | "vi";
export type TranslationKey = keyof typeof translations.en;
