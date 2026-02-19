-- Products table
CREATE TABLE IF NOT EXISTS products (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  category VARCHAR(100) NOT NULL,
  price DECIMAL(10, 0) NOT NULL CHECK (price >= 0),
  original_price DECIMAL(10, 0) CHECK (original_price >= 0),
  image TEXT,
  rating DECIMAL(3, 2) DEFAULT 0 CHECK (rating >= 0 AND rating <= 5),
  reviews INTEGER DEFAULT 0 CHECK (reviews >= 0),
  is_hot BOOLEAN DEFAULT FALSE,
  discount VARCHAR(20),
  tags TEXT,
  description TEXT,
  unit VARCHAR(50),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Articles table
CREATE TABLE IF NOT EXISTS articles (
  id BIGSERIAL PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  image TEXT,
  summary TEXT NOT NULL,
  content TEXT NOT NULL,
  date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  is_published BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Header Settings (Singleton - chỉ có 1 row)
CREATE TABLE IF NOT EXISTS header_settings (
  id INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
  logo TEXT,
  phone VARCHAR(20),
  email VARCHAR(255),
  menu_items JSONB DEFAULT '[]'::jsonb,
  search_placeholder VARCHAR(100) DEFAULT 'Tìm sản phẩm...',
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Footer Settings (Singleton - chỉ có 1 row)
CREATE TABLE IF NOT EXISTS footer_settings (
  id INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
  company_name VARCHAR(200) DEFAULT 'Mountain Harvest',
  address TEXT,
  phone VARCHAR(20),
  email VARCHAR(255),
  social_links JSONB DEFAULT '{}'::jsonb,
  footer_links JSONB DEFAULT '[]'::jsonb,
  copyright_text VARCHAR(200) DEFAULT '© 2024 Mountain Harvest. Designed for E-commerce.',
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_is_hot ON products(is_hot);
CREATE INDEX IF NOT EXISTS idx_articles_is_published ON articles(is_published);
CREATE INDEX IF NOT EXISTS idx_articles_date ON articles(date DESC);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers to auto-update updated_at
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON articles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_header_settings_updated_at BEFORE UPDATE ON header_settings
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_footer_settings_updated_at BEFORE UPDATE ON footer_settings
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default header settings
INSERT INTO header_settings (id) VALUES (1)
ON CONFLICT (id) DO NOTHING;

-- Insert default footer settings
INSERT INTO footer_settings (id) VALUES (1)
ON CONFLICT (id) DO NOTHING;
