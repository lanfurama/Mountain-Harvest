# Deploy Mountain Harvest với Django

## Sẵn sàng deploy

- Django project với `mountain_harvest/wsgi.py` hoặc `mountain_harvest/asgi.py`
- `requirements.txt`: Django, psycopg2-binary, python-dotenv, dj-database-url
- Database: PostgreSQL (giữ nguyên schema từ FastHTML)

## Cấu hình Environment Variables

- `POSTGRES_URL` hoặc `DATABASE_URL` – PostgreSQL connection string
- `ADMIN_USER`, `ADMIN_PASSWORD` – Basic auth cho `/admin`
- `SECRET_KEY` – Django secret key (generate với `python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `DEBUG` – Set to `False` trong production
- `ALLOWED_HOSTS` – Comma-separated list of allowed hosts

## Deployment Platforms

### Railway / Render / Heroku

1. Connect repository
2. Set environment variables
3. Run migrations: `python manage.py migrate`
4. Collect static files: `python manage.py collectstatic --noinput`
5. Deploy

### Vercel (Serverless)

Vercel không phù hợp với Django vì:
- Django không được optimize cho serverless
- Cold starts có thể chậm
- Cần config phức tạp với Vercel Serverless Functions

Nên dùng Railway, Render, hoặc VPS thay thế.

### VPS (DigitalOcean, AWS EC2, etc.)

1. Setup Python environment
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Collect static: `python manage.py collectstatic`
5. Setup WSGI server (Gunicorn + Nginx)
6. Configure domain và SSL

## Lưu ý

- Database schema giữ nguyên từ FastHTML
- Static files được serve qua Django trong development, cần Nginx/CDN trong production
- Admin auth dùng Basic Auth middleware (có thể thay bằng Django admin sau)
