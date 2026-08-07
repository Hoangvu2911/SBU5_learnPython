# Phân tích thiết kế — Cinema

Hệ thống đặt vé theo **suất chiếu** (Phim + Phòng + giờ).

| | |
|--|--|
| Vai trò | Admin (`User.is_staff`) · Customer (đã đăng nhập) · Guest |
| CSDL | PostgreSQL |
| Cache / giữ chỗ nhanh | **Redis** (TTL hold ghế · cache lịch/sơ đồ ghế) |
| Thời gian | Lưu `timestamptz` (UTC) · hiển thị giờ VN |

| Vai trò | Chức năng |
|---------|-----------|
| Admin | `is_staff=True` — quản lý phim, diễn viên, phòng, suất, vé |
| Guest | Xem lịch chiếu |
| Customer | Đăng ký/đăng nhập · xem lịch · đặt ghế · thanh toán giả lập · xem/hủy vé |

**Phân tầng lưu trữ**

| Nơi | Dùng cho | Vì sao |
|-----|----------|--------|
| PostgreSQL | Movie, Room, Showtime, Ticket `booked`/`cancelled`, audit | Bền vững, transaction, ràng buộc UNIQUE |
| Redis | Giữ ghế tạm (`pending`), cache danh sách suất/ghế trống | TTL tự hết hạn · SET NX atomic · giảm quét/ghi DB nóng |

---

## 1. Use Case

### 1.1 Sơ đồ Use Case

```mermaid
flowchart LR
  subgraph Actors
    Admin((Admin))
    Guest((Guest))
    Customer((Customer))
  end

  subgraph AdminUC
    UC01[UC01 Quản lý phim]
    UC02[UC02 Quản lý diễn viên]
    UC03[UC03 Gán cast]
    UC04[UC04 Quản lý phòng]
    UC05[UC05 Quản lý suất]
    UC06[UC06 Quản lý vé]
    UC07[UC07 Lọc vé]
  end

  subgraph CustomerUC
    UC08[UC08 Auth]
    UC09[UC09 Xem lịch]
    UC10[UC10 Đặt ghế]
    UC10a[UC10a Thanh toán]
    UC11[UC11 Vé của tôi]
    UC12[UC12 Hủy vé]
  end

  Admin --> UC01 & UC02 & UC03 & UC04 & UC05 & UC06 & UC07
  Guest --> UC09
  Customer --> UC08 & UC09 & UC10 & UC10a & UC11 & UC12
  UC10 --> UC10a
```

### 1.2 Danh sách Use Case

| ID | Actor | Mô tả |
|----|-------|-------|
| UC01 | Admin | CRUD phim, bật/tắt hiển thị |
| UC02 | Admin | CRUD diễn viên |
| UC03 | Admin | Gán diễn viên–phim (cặp duy nhất) |
| UC04 | Admin | CRUD phòng chiếu |
| UC05 | Admin | CRUD suất chiếu, hủy suất (cascade vé) |
| UC06 | Admin | Xem vé; chỉ được đổi `Ticket.status` (không đổi ghế / suất / giá / khách) |
| UC07 | Admin | Lọc vé theo suất, trạng thái |
| UC08 | Customer | Đăng ký / đăng nhập / đăng xuất |
| UC09 | Guest, Customer | Xem lịch chiếu |
| UC10 | Customer | Đặt 1 ghế → vé `pending` |
| UC10a | Customer | Thanh toán giả lập → `booked` |
| UC11 | Customer | Xem vé của tôi |
| UC12 | Customer | Hủy vé `pending` / `booked` |

---

## 2. Class Diagram

```mermaid
classDiagram
  direction TB

  class User {
    +username
    +password
    +is_staff
  }

  class Movie {
    +title
    +description
    +release_date
    +genre
    +rating
    +duration_minutes
    +director
    +is_active
  }

  class Actor {
    +name
    +bio
  }

  class MovieActor {
    +movie_id
    +actor_id
  }

  class Room {
    +name
    +capacity
    +validSeats()
  }

  class Showtime {
    +start_at
    +end_at
    +base_price
    +status
    +isBookable(now)
    +effectiveStatus(now)
  }

  class Ticket {
    +seat
    +price
    +status
  }

  class ShowtimeDbStatus {
    <<enumeration>>
    scheduled
    cancelled
  }

  class ShowtimeEffectiveStatus {
    <<enumeration>>
    scheduled
    ongoing
    completed
    cancelled
  }

  class TicketStatus {
    <<enumeration>>
    pending
    booked
    cancelled
  }

  class SeatHelper {
    <<utility>>
    +generateSeats(capacity)
    +isValidSeat(seat, capacity)
  }

  class BookingService {
    +book(user, showtime, seat)
    +pay(user, ticket)
    +cancel(user, ticket)
    +cleanupPending(showtime)
    +listSeatMap(showtime)
  }

  class ShowtimeService {
    +checkRoomOverlap(showtime)
    +cancelShowtime(showtime)
  }

  class SeatHoldStore {
    <<Redis>>
    +tryHold(showtimeId, seat, userId, ttlSec) bool
    +getHolder(showtimeId, seat) userId?
    +release(showtimeId, seat, userId)
    +listHeldSeats(showtimeId)
  }

  class CacheStore {
    <<Redis>>
    +getShowtimeSeatSummary(showtimeId)
    +invalidateShowtime(showtimeId)
    +getActiveShowtimes(movieId?)
    +invalidateSchedule()
  }

  User "1" --> "*" Ticket
  Movie "1" --> "*" Showtime
  Room "1" --> "*" Showtime
  Showtime "1" --> "*" Ticket
  Movie "1" --> "*" MovieActor
  Actor "1" --> "*" MovieActor
  Showtime --> ShowtimeDbStatus
  Showtime ..> ShowtimeEffectiveStatus : effectiveStatus()
  Ticket --> TicketStatus
  Room ..> SeatHelper
  Ticket ..> SeatHelper
  BookingService ..> Showtime
  BookingService ..> Ticket
  BookingService ..> SeatHoldStore
  BookingService ..> CacheStore
  ShowtimeService ..> Showtime
  ShowtimeService ..> CacheStore
  ShowtimeService ..> SeatHoldStore
```

| Thành phần | Trách nhiệm |
|------------|-------------|
| Model | Dữ liệu bền vững trên PostgreSQL, validate field |
| `SeatHelper` | Sinh / kiểm tra mã ghế (10 ghế/hàng, hàng A–Z) |
| `Showtime.isBookable(now)` | `status != cancelled` ∧ `start_at > now` |
| `Showtime.effectiveStatus(now)` | Suy `scheduled`/`ongoing`/`completed`/`cancelled` (§5.1) |
| `SeatHoldStore` (Redis) | Giữ ghế tạm TTL 10 phút · `SET key NX EX 600` · giải phóng khi hủy/pay/hết hạn |
| `CacheStore` (Redis) | Cache lịch chiếu (UC09) · cache tóm tắt ghế trống/đã giữ (giảm query Ticket) |
| `BookingService.cleanupPending` | Đồng bộ DB: hủy `pending` hết hạn / suất không bookable; xóa hold Redis tương ứng |
| `BookingService` | `book` / `pay` / `cancel` / `listSeatMap` — hold Redis trước, DB sau |
| `ShowtimeService` | Trùng lịch phòng · hủy suất cascade · invalidate cache/hold Redis |

---

## 3. ERD

```mermaid
erDiagram
  User ||--o{ Ticket : "customer"
  Movie ||--o{ Showtime : "has"
  Room ||--o{ Showtime : "hosts"
  Showtime ||--o{ Ticket : "has"
  Movie ||--o{ MovieActor : ""
  Actor ||--o{ MovieActor : ""

  User {
    int id PK
    string username UK
    string password
    bool is_staff
  }

  Movie {
    int id PK
    string title
    text description
    date release_date
    string genre
    decimal rating
    int duration_minutes
    string director
    bool is_active
    timestamptz created_at
    timestamptz updated_at
  }

  Actor {
    int id PK
    string name
    text bio
    timestamptz created_at
    timestamptz updated_at
  }

  MovieActor {
    int id PK
    int movie_id FK
    int actor_id FK
  }

  Room {
    int id PK
    string name UK
    int capacity
    timestamptz created_at
    timestamptz updated_at
  }

  Showtime {
    int id PK
    int movie_id FK
    int room_id FK
    timestamptz start_at
    timestamptz end_at
    decimal base_price
    string status "scheduled|cancelled"
    timestamptz created_at
    timestamptz updated_at
  }

  Ticket {
    int id PK
    int showtime_id FK
    int customer_id FK
    string seat
    decimal price
    string status
    timestamptz created_at
    timestamptz updated_at
  }
```

### 3.1 Quan hệ & ràng buộc

| Quan hệ | Cardinality | Ghi chú |
|---------|-------------|---------|
| User → Ticket | 1:N | `customer_id` |
| Movie → Showtime | 1:N | |
| Room → Showtime | 1:N | |
| Showtime → Ticket | 1:N | |
| Movie ↔ Actor | M:N | qua `MovieActor` |

| Bảng | Ràng buộc |
|------|-----------|
| MovieActor | UNIQUE `(movie_id, actor_id)` |
| Room | UNIQUE `name` · CHECK capacity 1–260 |
| Movie | CHECK rating 0–10 · CHECK duration ≥ 1 |
| Showtime | CHECK `end_at` > `start_at` · CHECK `base_price` ≥ 0 · UNIQUE `(room_id, start_at)` · CHECK status ∈ (`scheduled`, `cancelled`) |
| Ticket | Partial unique: UNIQUE `(showtime_id, seat)` WHERE status IN (`pending`, `booked`) · INDEX `(showtime_id, status)` · INDEX `(status, created_at)` |
| FK | RESTRICT — không xóa cha khi còn con |

| Enum (DB) | Giá trị |
|-----------|---------|
| `Showtime.status` | **`scheduled` · `cancelled`** (chỉ 2 giá trị lưu DB) |
| `Ticket.status` | `pending` · `booked` · `cancelled` |

| Snapshot | Nguồn | Khi nào |
|----------|--------|---------|
| `Showtime.end_at` | `start_at` + duration phim | Tạo / sửa suất |
| `Ticket.price` | `Showtime.base_price` | Đặt ghế (UC10) |

Kiểu cột: tiền `NUMERIC(10,2)` · thời gian `TIMESTAMPTZ` · status `VARCHAR` + CHECK.

---

## 4. Sequence Diagram

### 4.1 Đặt ghế (UC10)

```mermaid
sequenceDiagram
  actor C as Customer
  participant S as Hệ thống
  participant R as Redis
  participant DB as PostgreSQL

  C->>S: Chọn suất + ghế
  S->>S: cleanupPending(showtime)
  S->>S: Đăng nhập? · bookable? · ghế hợp lệ?
  S->>R: SET hold:{showtime}:{seat} = userId NX EX 600
  alt Key đã tồn tại
    R-->>S: Fail
    S-->>C: Ghế đang được giữ
  else Hold OK
    S->>DB: INSERT ticket (pending, price = base_price)
    alt Unique violation / lỗi DB
      DB-->>S: Lỗi
      S->>R: DEL hold key
      S-->>C: Ghế đã được giữ / lỗi
    else OK
      S->>R: Invalidate seat-map cache
      S-->>C: Sang màn thanh toán
    end
  end
```

### 4.2 Thanh toán giả lập (UC10a)

```mermaid
sequenceDiagram
  actor C as Customer
  participant S as Hệ thống
  participant R as Redis
  participant DB as PostgreSQL

  C->>S: Xác nhận thanh toán
  S->>S: cleanupPending(showtime của vé)
  S->>S: Đúng chủ? · vẫn pending? · bookable?
  S->>R: getHolder == user? (hoặc key còn / thuộc user)
  S->>DB: status → booked
  S->>R: DEL hold key · invalidate seat-map
  S-->>C: Thành công / Lỗi
```

### 4.3 Hủy vé (UC12)

```mermaid
sequenceDiagram
  actor C as Customer
  participant S as Hệ thống
  participant R as Redis
  participant DB as PostgreSQL

  C->>S: Hủy vé
  S->>S: cleanupPending(showtime của vé)
  S->>S: Đúng chủ? · pending/booked? · bookable?
  S->>DB: status → cancelled
  S->>R: DEL hold key (nếu pending) · invalidate seat-map
  S-->>C: Thành công / Lỗi
```

### 4.4 Admin hủy suất (UC05)

```mermaid
sequenceDiagram
  actor A as Admin
  participant S as Hệ thống
  participant R as Redis
  participant DB as PostgreSQL

  A->>S: Hủy suất
  S->>DB: BEGIN
  S->>DB: Showtime.status → cancelled
  S->>DB: Tickets pending/booked → cancelled
  S->>DB: COMMIT
  S->>R: Xóa mọi hold:{showtime}:* · invalidate cache suất/ghế
  S-->>A: Xong
```

### 4.5 Xem sơ đồ ghế / lịch (UC09 · listSeatMap)

```mermaid
sequenceDiagram
  actor U as Guest/Customer
  participant S as Hệ thống
  participant R as Redis
  participant DB as PostgreSQL

  U->>S: Xem ghế / lịch
  S->>R: GET cache seat-map / showtimes
  alt Cache hit
    R-->>S: data
  else Cache miss
    S->>S: cleanupPending (lazy)
    S->>DB: tickets booked (+ pending còn hạn)
    S->>R: SMEMBERS / SCAN hold:{showtime}:*
    S->>R: SET cache TTL ngắn (vd. 3–10s)
  end
  S-->>U: Ghế trống / đang giữ / đã bán
```

---

## 5. State Diagram

### 5.1 Suất chiếu — chốt mô hình (A)

**DB chỉ lưu 2 giá trị:** `scheduled` | `cancelled`.  
**Hiệu lực hiển thị / rule:** `effectiveStatus(now)` suy ra 4 trạng thái — không dùng cron.

```text
effectiveStatus(now):
  if status == cancelled           → cancelled
  elif now < start_at              → scheduled
  elif now < end_at                → ongoing
  else                             → completed
```

```mermaid
stateDiagram-v2
  [*] --> scheduled : tạo suất (DB = scheduled)
  scheduled --> ongoing : now ≥ start_at (chỉ hiệu lực)
  ongoing --> completed : now ≥ end_at (chỉ hiệu lực)
  scheduled --> cancelled : admin hủy (DB = cancelled)
  ongoing --> cancelled : admin hủy (DB = cancelled)
```

| effectiveStatus | Đặt ghế / Pay / Hủy vé user |
|-----------------|------------------------------|
| scheduled | Cho phép (`isBookable`) |
| ongoing · completed · cancelled | Không |

### 5.2 Vé

```mermaid
stateDiagram-v2
  [*] --> pending : UC10
  pending --> booked : UC10a
  pending --> cancelled : UC12 / cleanupPending / admin hủy suất
  booked --> cancelled : UC12 / admin hủy suất
```

**`cleanupPending(showtime)`** (gọi trong book / pay / cancel / xem ghế):

1. Mọi vé `pending` của suất có `created_at` + 10 phút ≤ now → `cancelled` + **DEL** hold Redis tương ứng  
2. Nếu suất **không bookable** → mọi vé `pending` còn lại → `cancelled` + xóa hold Redis của suất  
3. (Bổ trợ) Hold Redis đã hết TTL nhưng DB còn `pending` → coi hết hạn, chuyển `cancelled` khi chạm cleanup

> Redis TTL là đường nhanh để ghế “nhả” khỏi sơ đồ; PostgreSQL vẫn là nguồn sự thật cho Ticket.

---

## 6. Logic nghiệp vụ

**Bookable** = `status != cancelled` ∧ `start_at` > now  
(= `effectiveStatus` là `scheduled`).

**Suất chưa chiếu** (khi đổi duration phim) = `status != cancelled` ∧ `start_at` > now.  
Suất `cancelled`, hoặc đã tới/qua giờ (`ongoing`/`completed` hiệu lực) **không chặn** đổi duration.

| Rule | Chi tiết |
|------|----------|
| Admin | `User.is_staff == True` |
| Hiện lịch (UC09) | Phim `is_active` · suất bookable · **ưu tiên đọc cache Redis** |
| Ghế | 10 ghế/hàng (A1–A10, B1–B10, …) · tối đa 26 hàng A–Z · capacity 1–260 · số ghế hợp lệ = capacity |
| Đặt ghế | 1 ghế / lần |
| Giữ chỗ | Redis hold TTL **600s** + Ticket DB `pending` · dọn bởi TTL + `cleanupPending` |
| Trạng thái ghế (UI) | `booked` ← DB · `held` ← Redis hold còn sống · còn lại `available` |
| Giá vé | Snapshot lúc đặt · không đổi theo suất sau |
| `base_price` | ≥ 0 |
| Trùng lịch phòng | `[start_at, end_at)` không giao suất khác cùng phòng có `status = scheduled` |
| Đổi duration phim | Từ chối nếu còn **suất chưa chiếu**; không recalc `end_at` hàng loạt |
| Sửa suất đã có vé `pending`/`booked` | Không đổi phim / phòng / `start_at` / `base_price` |
| UC06 sửa vé | Chỉ đổi `Ticket.status`; **không** đổi `seat`, suất, giá, khách |
| Hủy suất | DB `cancelled` + cascade vé active → `cancelled` + **clear Redis holds/cache** |
| Thanh toán | Giả lập trên UI |

### 6.1 Redis — thiết kế key & TTL

| Key pattern | Kiểu | TTL | Giá trị | Mục đích |
|-------------|------|-----|---------|----------|
| `hold:{showtime_id}:{seat}` | STRING | **600s** | `user_id` | Giữ ghế tạm (UC10); `SET NX EX` chống double-hold |
| `seatmap:{showtime_id}` | STRING/HASH | 3–10s | JSON tóm tắt ghế | Cache sơ đồ ghế, giảm join Ticket |
| `schedule:active` / `schedule:movie:{id}` | STRING | 30–60s | JSON list suất | Cache UC09 xem lịch |
| `showtime:meta:{id}` | STRING | 30–60s | bookable, price, room… | Cache metadata suất nóng |

**Quy tắc đồng bộ**

| Sự kiện | Redis | PostgreSQL |
|---------|-------|------------|
| UC10 book | `SET hold … NX EX 600` | INSERT Ticket `pending` |
| UC10a pay | DEL hold · invalidate `seatmap` | `pending` → `booked` |
| UC12 cancel | DEL hold (nếu có) · invalidate | → `cancelled` |
| TTL hold hết | Key tự mất (ghế hiện available trên map) | `cleanupPending` sửa `pending` → `cancelled` khi request chạm |
| UC05 hủy suất | DEL `hold:{showtime}:*` · invalidate schedule/seatmap | Suất + vé active → `cancelled` |
| Admin sửa lịch/phim ảnh hưởng list | invalidate `schedule:*` | UPDATE models |

**Fail-safe:** Redis down → fallback đọc/ghi PostgreSQL (hold bằng partial unique `pending`/`booked`); chấp nhận chậm hơn, không mất đúng sai dữ liệu bền vững.

---

## 7. Kiến trúc tổng quan

```mermaid
flowchart TB
  subgraph Presentation
    AdminUI[Admin — is_staff]
    CustomerUI[Customer / Guest]
  end

  subgraph Application
    BookingService
    ShowtimeService
  end

  subgraph Domain
    Models[Movie · Actor · Room · Showtime · Ticket]
    SeatHelper
  end

  subgraph Infrastructure
    DB[(PostgreSQL)]
    Redis[(Redis)]
  end

  AdminUI --> ShowtimeService
  AdminUI --> Models
  CustomerUI --> BookingService
  BookingService --> Models
  BookingService --> Redis
  ShowtimeService --> Models
  ShowtimeService --> Redis
  Models --> SeatHelper
  Models --> DB
```

| Lớp | Nội dung |
|-----|----------|
| Presentation | Admin CRUD · lịch · chọn ghế · thanh toán · vé của tôi · auth |
| Application | `BookingService` · `ShowtimeService` |
| Domain | Models + `SeatHelper` |
| Infrastructure | **PostgreSQL** (durable) · **Redis** (hold TTL + cache nóng) |

---

## 8. Kiểm thử

| # | Kịch bản | Mong đợi |
|---|----------|----------|
| 1 | Hai suất cùng phòng trùng giờ | Từ chối |
| 2 | Đổi duration khi còn suất chưa chiếu | Từ chối |
| 3 | Đổi duration khi chỉ còn suất cancelled / đã qua giờ | Cho phép |
| 4 | Hai lần đặt cùng ghế (Redis SET NX) | Một hold + một `pending`, một lỗi |
| 5 | Đặt lại ghế đã `cancelled` | Thành công (hold mới) |
| 6 | Pay / hủy sau giờ chiếu | Từ chối |
| 7 | Admin hủy suất | Suất + vé active → `cancelled` · Redis holds bị xóa |
| 8 | Pay `pending` còn hạn | → `booked` · DEL hold |
| 9 | Pay hết hạn / sai chủ | Từ chối |
| 10 | Hold/pending > 10 phút | Redis hết TTL · DB `pending` → `cancelled` khi cleanup |
| 11 | `pending` còn hạn nhưng suất đã bắt đầu | → `cancelled` + clear hold |
| 12 | Hủy `pending` trước pay | → `cancelled` · DEL hold |
| 13 | Admin UC06 đổi ghế vé | Từ chối / không cho sửa field ghế |
| 14 | Xem sơ đồ ghế cache hit | Không query nặng Ticket nếu cache còn |
| 15 | Redis down khi book | Fallback DB partial unique; không mất toàn vẹn |
