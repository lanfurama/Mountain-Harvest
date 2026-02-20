# Deploy Mountain Harvest lên Vercel + FastHTML

## Sẵn sàng deploy

- `vercel.json`: rewrite mọi request tới `/api/index`
- `api/index.py`: FastHTML app + `handler = app` (Vercel ASGI)
- `requirements.txt`: python-fasthtml, asyncpg, python-dotenv

## Cấu hình trên Vercel

1. **Env vars** (Project Settings → Environment Variables):
   - `POSTGRES_URL` hoặc `DATABASE_URL` – PostgreSQL connection string
   - `ADMIN_USER`, `ADMIN_PASSWORD` – Basic auth cho `/admin`
   - Vercel Postgres/Neon: tự động tạo `POSTGRES_URL` khi add addon

2. **Database**: PostgreSQL chạy sẵn (Neon, Supabase, Vercel Postgres, v.v.) và cho phép kết nối từ Vercel.

3. **Schema**: Tables được tạo tự động qua `init_db()` khi cold start. Nếu cần data mẫu, chạy `sql/init.sql` và `sql/seed_extra.sql` trực tiếp trên DB trước.

## Deploy

```bash
vercel
# hoặc production
vercel --prod
```

Hoặc: push lên GitHub/GitLab → kết nối repo trong Vercel dashboard.

## Lưu ý

- Serverless: nhiều instance có thể tạo nhiều connection pool → nên dùng pooled URL (Neon, Supabase pooler) khi traffic cao.
