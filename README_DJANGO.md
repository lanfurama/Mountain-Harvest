# Django Migration Complete

Migration từ FastHTML sang Django đã hoàn tất.

## Cấu trúc mới

- `manage.py` - Django management script
- `mountain_harvest/` - Django project settings
- `api/` - Django app với models, views, urls
- `public/` - Static files (giữ nguyên)

## Chạy ứng dụng

1. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

2. Chạy migrations (nếu database chưa có):
```bash
python manage.py migrate
```

3. Chạy server:
```bash
python manage.py runserver
# → http://localhost:3005 (port mặc định)
```

## Lưu ý

- Database schema giữ nguyên, Django models map trực tiếp vào tables hiện có
- HTML rendering vẫn dùng string manipulation (có thể refactor sang Django templates sau)
- Admin auth middleware đã chuyển sang Django middleware
- Static files được serve tự động trong development mode

## Cần kiểm tra

- [ ] Test tất cả API endpoints
- [ ] Test frontend routes
- [ ] Test admin panel
- [ ] Test SEO routes (sitemap, robots.txt)
- [ ] Kiểm tra database connections
- [ ] Kiểm tra static files serving
