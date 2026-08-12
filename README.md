# Pet project: Cinema Ticket Booking API

Demo backend (Django + DRF) cho hệ thống đặt vé rạp theo **suất chiếu** (Movie + Room + Showtime) và **giữ ghế tạm** bằng Redis.

## Tính năng chính

API REST:
- `movies`: CRUD phim (staff quản lý, customer chỉ xem)
- `showtimes`: CRUD suất chiếu, xem danh sách + lấy `seats` cho 1 suất, booking ghế qua action `book`
- `tickets`: customer xem vé của mình, hủy vé qua action `cancel`, staff thay đổi status vé qua `patch`
- `auth`: `register`, `login`, `logout` (token-based)
- `actors`, `rooms`: CRUD cho staff (admin)

Nghiệp vụ booking:
- Customer book 1 ghế cho 1 suất -> tạo `Ticket.status=pending`
- Redis key `hold:{showtime_id}:{seat}` để chống double-hold trong TTL
- Pay/Cancel được kiểm tra theo trạng thái suất (API sync status theo thời gian)

Tài liệu API:
- Swagger UI: `/api/docs/`
- OpenAPI schema: `/api/schema/`

## Tech stack

- Django 6.1
- Django REST Framework
- drf-spectacular (OpenAPI/Swagger)
- PostgreSQL
- Redis
- REST token auth (`rest_framework.authtoken`)

## Cài đặt

### Setup với Docker (khuyến nghị)

Project có sẵn `Dockerfile` và `docker-compose.yml` tại `myproject/`.

1. Tạo file cấu hình:
```bash
cd myproject
cp .env.example .env
```

2. Điền các biến tối thiểu trong `myproject/.env` (ví dụ dùng đúng với docker network):
```bash
# Django
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
WEB_PUBLISH_PORT=8000

# PostgreSQL (trong docker network sẽ là host=db)
POSTGRES_DB=cinema_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=secret
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_PUBLISH_PORT=5433

# Redis (trong docker network sẽ là host=redis)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://redis:6379/0
REDIS_PUBLISH_PORT=6379

# TTL giữ ghế
SEAT_HOLD_TTL_SECONDS=600
```

3. Build & chạy:
```bash
docker compose up -d --build
```

Sau khi container `web` chạy xong, API sẽ có tại:
- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI schema: `http://localhost:8000/api/schema/`

## Chạy dự án

Bạn chạy Docker ở trên thì `docker-compose` đã tự `migrate` trước khi `runserver`.

### (Tuỳ chọn) Tạo superuser

```bash
docker compose exec web python manage.py createsuperuser
```

## Endpoint API quan trọng

Base: `/api/`

Auth:
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `GET/POST /api/token/` (DRF token view)

Movies:
- `GET /api/movies/`
- `POST /api/movies/` (staff)
- `GET /api/movies/{id}/`
- `PATCH /api/movies/{id}/` (staff)
- `POST /api/movies/{id}/toggle/` (staff/admin)

Showtimes:
- `GET /api/showtimes/`
- `GET /api/showtimes/{id}/`
- `GET /api/showtimes/{id}/seats/` (trả về sơ đồ ghế theo trạng thái)
- `POST /api/showtimes/{id}/book/` (customer, body: `{ "seat": "A1" }`)
- `POST /api/showtimes/{id}/cancel/` (admin)

Tickets:
- `GET /api/tickets/` (customer: tự động lọc theo `customer=self`)
- `POST /api/tickets/{id}/cancel/` (customer)
- `POST /api/tickets/{id}/pay/` (action có sẵn trong API)
- `PATCH /api/tickets/{id}/` (staff: đổi `status`)

Staff/Admin resources:
- `actors`, `rooms` (staff quản lý)

## Chạy test

```bash
python myproject/manage.py test
```

## Spec / tài liệu nghiệp vụ

`myproject/SPEC.md` chứa phân tích thiết kế và logic đặt vé (booking state machine, redis hold, quy tắc bookable, v.v.).
