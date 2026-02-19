# Mountain Harvest CMS - Next.js + Supabase

CMS đơn giản để quản lý sản phẩm, bài viết, header và footer cho website Mountain Harvest.

## Cài đặt

### 1. Cài đặt dependencies

```bash
npm install
```

### 2. Setup Supabase

1. Tạo tài khoản tại [Supabase](https://supabase.com)
2. Tạo project mới
3. Vào **SQL Editor** và chạy file `supabase/schema.sql` để tạo tables
4. Vào **Settings > API** để lấy:
   - Project URL
   - Anon/Public key

### 3. Cấu hình environment variables

Sao chép `.env.example` thành `.env.local`:

```bash
cp .env.example .env.local
```

Cập nhật các giá trị trong `.env.local`:

```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 4. Chạy development server

```bash
npm run dev
```

Truy cập:
- Frontend: http://localhost:3000
- Admin Panel: http://localhost:3000/admin

## Deploy lên Vercel

1. Push code lên GitHub
2. Vào [Vercel](https://vercel.com) và import project
3. Thêm environment variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
4. Deploy!

## API Endpoints

### Products
- `GET /api/products` - Danh sách sản phẩm
- `GET /api/products?category=Rau củ quả` - Lọc theo danh mục
- `GET /api/products?is_hot=true` - Sản phẩm hot
- `GET /api/products/[id]` - Chi tiết sản phẩm
- `POST /api/products` - Tạo sản phẩm mới
- `PUT /api/products/[id]` - Cập nhật sản phẩm
- `DELETE /api/products/[id]` - Xóa sản phẩm

### Articles
- `GET /api/articles` - Danh sách bài viết đã xuất bản
- `GET /api/articles/[id]` - Chi tiết bài viết
- `POST /api/articles` - Tạo bài viết mới
- `PUT /api/articles/[id]` - Cập nhật bài viết
- `DELETE /api/articles/[id]` - Xóa bài viết

### Header & Footer
- `GET /api/header` - Lấy cấu hình header
- `PUT /api/header` - Cập nhật header
- `GET /api/footer` - Lấy cấu hình footer
- `PUT /api/footer` - Cập nhật footer

## Database Schema

### Products
- id, name, category, price, original_price
- image (URL), rating, reviews
- is_hot, discount, tags
- description, unit
- created_at, updated_at

### Articles
- id, title, image (URL), summary, content
- date, is_published
- created_at, updated_at

### Header Settings (Singleton)
- id (always 1), logo, phone, email
- menu_items (JSON), search_placeholder

### Footer Settings (Singleton)
- id (always 1), company_name, address
- phone, email, social_links (JSON)
- footer_links (JSON), copyright_text

## Sử dụng Admin Panel

1. Truy cập `/admin`
2. Chọn tab tương ứng (Sản phẩm, Bài viết, Header, Footer)
3. Thêm/sửa/xóa nội dung
4. Frontend sẽ tự động lấy dữ liệu từ API

## Lưu ý

- Header và Footer sử dụng Singleton pattern (chỉ có 1 instance)
- Tất cả API routes đều public (có thể thêm authentication sau)
- Images sử dụng URL, không upload trực tiếp (có thể tích hợp Supabase Storage sau)
