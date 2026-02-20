-- Mountain Harvest CMS - Schema & Sample Data
-- Chạy: psql -U postgres -d mountain_harvest -f sql/init.sql

-- ============= TABLES =============
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price INTEGER NOT NULL,
    original_price INTEGER,
    unit VARCHAR(50),
    image TEXT,
    rating DECIMAL(2,1) DEFAULT 0,
    reviews INTEGER DEFAULT 0,
    is_hot BOOLEAN DEFAULT FALSE,
    discount VARCHAR(20),
    tags JSONB DEFAULT '[]',
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    image TEXT,
    content TEXT,
    author VARCHAR(255),
    date VARCHAR(20),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hero (
    id SERIAL PRIMARY KEY,
    promo VARCHAR(100),
    title VARCHAR(255),
    subtitle TEXT,
    image TEXT,
    button_text VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS category_brochures (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255),
    "desc" TEXT,
    image TEXT,
    button_text VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS site_config (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    sort_order INTEGER DEFAULT 0
);

-- ============= SAMPLE DATA =============
-- Chạy trên database trống. Nếu chạy lại, xóa data cũ trước: TRUNCATE products, news, hero, category_brochures, site_config, categories CASCADE;

INSERT INTO hero (promo, title, subtitle, image, button_text)
SELECT 'Summer Sale', 'Fresh Produce For Green Living', 'Up to 20% off on vegetables and fruits this week.',
 'https://images.unsplash.com/photo-1542838132-92c53300491e?ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80',
 'Shop Now'
WHERE NOT EXISTS (SELECT 1 FROM hero LIMIT 1);

INSERT INTO category_brochures (slug, title, "desc", image, button_text) VALUES
('fresh', 'Fresh Produce', 'Harvested from Da Lat farms, delivered same day to ensure freshness.',
 'https://images.unsplash.com/photo-1542838132-92c53300491e?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80',
 'Shop Now'),
('essentials', 'Green Essentials', 'Natural home care products, safe for children.',
 'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80',
 'Explore')
ON CONFLICT (slug) DO NOTHING;

INSERT INTO site_config (key, value) VALUES
('topbar', '{"freeShipping": "Miễn phí vận chuyển cho đơn hàng từ 500k", "hotline": "1900 1234", "support": "Hỗ trợ khách hàng"}'::jsonb),
('footer', '{"address": "123 Đường Mây Núi, Đà Lạt", "phone": "1900 1234", "email": "cskh@mountainharvest.vn", "links": [{"label": "Hướng dẫn mua hàng", "url": "#"}, {"label": "Chính sách giao hàng", "url": "#"}, {"label": "Đổi trả & Hoàn tiền", "url": "#"}, {"label": "Câu hỏi thường gặp", "url": "#"}], "social": [{"icon": "facebook-f", "url": "#"}, {"icon": "tiktok", "url": "#"}, {"icon": "youtube", "url": "#"}]}'::jsonb)
ON CONFLICT (key) DO NOTHING;

INSERT INTO categories (name, sort_order)
SELECT * FROM (VALUES ('Rau củ quả', 1), ('Hạt & Ngũ cốc', 2), ('Gia dụng', 3), ('Thực phẩm khô', 4), ('Đồ uống', 5), ('Hoá mỹ phẩm', 6)) AS v(name, sort_order)
WHERE NOT EXISTS (SELECT 1 FROM categories LIMIT 1);

INSERT INTO products (name, category, price, original_price, unit, image, rating, reviews, is_hot, discount, tags, description, sort_order) VALUES
('Cà Chua Cherry Hữu Cơ', 'Rau củ quả', 45000, 55000, NULL, 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80', 4.5, 45, FALSE, '-15%', '["Organic"]', 'Cà chua cherry được trồng theo phương pháp hữu cơ tại nông trại Đà Lạt.', 1),
('Gạo Lứt Đỏ Huyết Rồng', 'Thực phẩm khô', 80000, NULL, '/2kg', 'https://images.unsplash.com/photo-1586201375761-83865001e31c?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80', 5, 128, FALSE, NULL, '[]', 'Gạo lứt đỏ huyết rồng chứa nhiều chất xơ và khoáng chất.', 2),
('Cà Phê Arabica Cầu Đất', 'Đồ uống', 150000, NULL, '/500g', 'https://images.unsplash.com/photo-1594631252845-29fc4cc8cde9?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80', 4, 89, TRUE, NULL, '["Best Seller"]', 'Hạt cà phê Arabica tuyển chọn từ vùng Cầu Đất.', 3),
('Nước Giặt Bồ Hòn Tự Nhiên', 'Hoá mỹ phẩm', 120000, NULL, '/Lít', 'https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80', 5, 210, FALSE, NULL, '["Handmade"]', 'Nước giặt được chiết xuất từ quả bồ hòn lên men tự nhiên.', 4);

INSERT INTO news (title, image, content, author, date, sort_order) VALUES
('Mùa Thu Hoạch Bơ Sáp 034 Đã Bắt Đầu', 'https://images.unsplash.com/photo-1523049673856-35691f096315?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80', '<p>Những trái bơ sáp 034 dẻo, béo ngậy đầu tiên của mùa vụ năm nay đã chính thức lên kệ tại Mountain Harvest.</p>', 'Admin', '03/02/2026', 1),
('Bí Quyết Giữ Rau Củ Tươi Lâu Trong Tủ Lạnh', 'https://images.unsplash.com/photo-1566385101042-1a0aa0c1268c?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80', '<p>Chia sẻ những mẹo vặt đơn giản nhưng hiệu quả để bảo quản rau củ quả luôn tươi ngon suốt cả tuần.</p>', 'Admin', '01/02/2026', 2);
