# Báo cáo — RESTful API
---

## 1. API và REST khác nhau thế nào?

**API** (Application Programming Interface) là cách một chương trình gọi chương trình khác: gửi yêu cầu, nhận kết quả. Trên web, API thường chạy trên **HTTP**.

**REST** (Representational State Transfer) không phải thư viện hay ngôn ngữ. Đó là **phong cách thiết kế** API HTTP, với ý tưởng:

1. Client làm việc với **tài nguyên (resource)**, không gọi “hàm từ xa” đặt tên tùy ý.
2. Mỗi resource có **địa chỉ ổn định (URI)**.
3. Client nhận **biểu diễn trạng thái (representation)** — thường JSON — không nhận object sống trên server.
4. Hành động dùng **động từ HTTP chuẩn** (GET, POST, PUT, PATCH, DELETE…).

So sánh tư duy:

| Hướng RPC (đặt tên lệnh) | Hướng REST (tài nguyên + method) |
|--------------------------|----------------------------------|
| Một URL kiểu “thực hiện đặt ghế” | Resource = suất chiếu; method POST = tạo vé trên suất đó |
| Một URL kiểu “lấy danh sách phim” | Resource = tập phim; method GET = đọc |
| Một URL kiểu “xóa vé” kèm id trên query | Resource = một vé; DELETE nếu xóa cứng, hoặc POST/PATCH nếu chỉ đổi trạng thái hủy |

REST giúp nhiều loại client (trang web, ứng dụng, công cụ thử API) **dùng chung một hợp đồng**: đã biết quy tắc HTTP thì đoán được cách gọi, không học protocol riêng từng chức năng.

---

## 2. Các khái niệm then chốt

### 2.1 Resource và URI

**Resource** là thứ client quan tâm: một phim, danh sách phim, một suất chiếu, một vé.

URI nên:

- Diễn đạt **danh từ** (tài nguyên), không diễn đạt lệnh.
- Phân biệt **tập hợp** và **một phần tử** (collection vs instance).
- Dùng **path** cho định danh ổn định.
- Dùng **query string** cho lọc, tìm kiếm, phân trang — đó không phải id mới, mà là cách **thu hẹp representation**.

Hành động nghiệp vụ không map sạch sang CRUD (đặt ghế, thanh toán, hủy) vẫn gắn vào **resource liên quan**. URI chỉ ra resource; **method** mới nói “làm gì”.

### 2.2 Representation

Cùng một resource có thể có nhiều dạng biểu diễn: HTML cho người xem trên trình duyệt, JSON cho API, XML… Client và server thỏa thuận qua header (ví dụ Accept / Content-Type). API hiện đại thường chọn **JSON** vì gọn, phổ biến, dễ đọc máy.

Representation là **ảnh chụp trạng thái tại thời điểm request**, không phải kết nối lâu dài tới bản ghi trong cơ sở dữ liệu.

### 2.3 Stateless

Mỗi request phải **tự chứa đủ ngữ cảnh** để server xử lý: URI, method, header, body. Server không dựa vào “bước hội thoại trước đó” lưu trong bộ nhớ chu kỳ request.

Hệ quả:

- Dễ mở rộng: mọi máy chủ xử lý cùng một request theo cùng cách.
- Client chịu trách nhiệm gửi lại thông tin xác thực và tham số mỗi lần gọi.
- Trạng thái nghiệp vụ (vé đang giữ, ghế đã bán) nằm ở **dữ liệu bền vững**, không nằm ở “phiên API ẩn”.

Stateless **không** có nghĩa hệ thống không có trạng thái — chỉ nghĩa một request HTTP không phụ thuộc hội thoại nhớ trên server.

### 2.4 Uniform interface

Mọi resource dùng **cùng bộ quy tắc HTTP**. Client đã biết GET là đọc, POST là tạo hoặc kích hoạt thay đổi… thì áp dụng được cho phim, suất, vé mà không học API khác biệt từng endpoint.

Các ràng buộc thường gặp:

- Định danh resource trên URI.
- Thao tác qua method chuẩn.
- Response tự mô tả: status code + body + header.
- Hypermedia (tùy mức độ): response có thể gợi ý bước tiếp (link). Nhiều đồ án nhỏ chỉ làm mức URI + method + JSON.

### 2.5 Tách client và server

Giao diện người dùng và logic lưu trữ độc lập. Đổi client (trang web khác, ứng dụng di động, công cụ thử API) không bắt buộc đổi cách lưu dữ liệu, miễn hợp đồng HTTP còn đúng. Ngược lại, server đổi nội bộ (bảng, cache) không bắt buộc đổi URI và method nếu representation giữ ổn định.

---

## 3. HTTP methods

Method trả lời câu hỏi: **hành động gì** trên resource mà URI đã chỉ ra?

### 3.1 GET

- Mục đích: **lấy representation**, không làm thay đổi trạng thái resource chỉ vì việc gọi GET.
- Tính chất: **an toàn (safe)** và **idempotent**.
- Dùng cho: xem danh sách, xem chi tiết, xem sơ đồ / báo cáo chỉ-đọc.
- Lặp lại GET nhiều lần không được tạo thêm bản ghi hay đổi trạng thái nghiệp vụ.

### 3.2 POST

- Mục đích: **tạo resource mới**, hoặc **kích hoạt một xử lý** không mô tả sạch bằng PUT / PATCH / DELETE (đặt chỗ, xác nhận thanh toán, cấp token, hủy suất…).
- Tính chất: **không safe**, **không idempotent** — gửi hai lần có thể tạo hai kết quả hoặc hai side-effect.
- Body thường chứa dữ liệu đầu vào. Server quyết định định danh resource mới (nếu có) và trả về representation sau khi xử lý.

### 3.3 PUT

- Mục đích: **thay thế toàn bộ** resource bằng representation client gửi lên.
- Tính chất: không safe, nhưng **idempotent** — gửi lại cùng toàn bộ dữ liệu thì trạng thái đích giống nhau.
- Client phải nắm đủ field; thiếu field thường bị hiểu là xóa hoặc để mặc định, tùy hợp đồng API.
- Phù hợp cập nhật kiểu “ghi đè cả bản ghi”.

### 3.4 PATCH

- Mục đích: **cập nhật một phần** resource (chỉ field đổi).
- Tính chất: không safe; idempotent nếu cùng một bản vá dẫn tới cùng một trạng thái đích.
- Phù hợp sửa vài thuộc tính, không gửi lại toàn bộ đối tượng.

### 3.5 DELETE

- Mục đích: **gỡ resource**.
- Tính chất: không safe, **idempotent** — xóa rồi gọi lại, resource vẫn không còn (không tạo side-effect mới).
- Một số hệ thống không xóa cứng mà chuyển trạng thái (ví dụ vé sang `cancelled`): đó là **đổi representation / status**, gần PATCH hoặc POST nghiệp vụ hơn là DELETE vật lý.

### 3.6 HEAD và OPTIONS

- **HEAD:** giống GET về ý nghĩa “đọc metadata”, nhưng không trả body. Dùng kiểm tra tồn tại, cache, header.
- **OPTIONS:** hỏi resource **chấp nhận method nào** (và chính sách CORS). Không đổi dữ liệu; safe và idempotent.

---

## 4. Safe và idempotent

Hai tính chất này giúp thiết kế đúng method và giúp trung gian (cache, proxy, retry) hành xử an toàn.

| Tính chất | Ý nghĩa | Method điển hình |
|-----------|---------|------------------|
| **Safe** | Request không làm thay đổi trạng thái tài nguyên | GET, HEAD, OPTIONS |
| **Idempotent** | Gọi một lần hay nhiều lần với cùng request → cùng trạng thái đích | GET, HEAD, OPTIONS, PUT, DELETE |
| Không safe, không idempotent | Mỗi lần gọi có thể tạo thêm thay đổi | POST (thường gặp) |

Ví dụ tư duy trên rạp chiếu:

- Đọc danh sách phim → GET (safe).
- Đặt ghế → POST (mỗi lần thành công thêm một lượt giữ chỗ; lần hai cùng ghế phải thất bại hoặc xung đột — không phải “gọi lại như không có gì”).
- Ghi đè toàn bộ thông tin phòng → PUT (gửi lại cùng dữ liệu không nhân đôi phòng).
- Chỉ đổi một cờ hiển thị → PATCH.
- Gỡ bản ghi không còn liên kết → DELETE.
- Hủy vé nhưng vẫn cần xem lịch sử → đổi status (POST hoặc PATCH), không DELETE cứng.

Không nhét side-effect vào GET (ví dụ GET mà tự giữ ghế): phá tính safe, phá cache và retry.

---

## 5. Status code — phần gắn với method

Status code là một phần của **uniform interface**: client đọc mã để biết kết quả, không cần đoán nội dung body.

| Nhóm | Vai trò |
|------|---------|
| 2xx | Thành công |
| 4xx | Lỗi phía client (sai URI, sai dữ liệu, thiếu xác thực, không có quyền) |
| 5xx | Lỗi phía server |

Một số mã thường đi với REST:

- **200 OK** — GET thành công; một số POST “xử lý xong, không tạo resource mới” cũng dùng 200.
- **201 Created** — POST (hoặc PUT tạo mới) đã tạo resource; thường kèm representation hoặc vị trí resource mới.
- **204 No Content** — thành công, không cần body (hay gặp DELETE / đăng xuất / một số PATCH).
- **400 Bad Request** — cú pháp hoặc rule nghiệp vụ không thỏa (thiếu field, ghế không hợp lệ…).
- **401 Unauthorized** — chưa xác thực hoặc thông tin xác thực không hợp lệ.
- **403 Forbidden** — đã biết danh tính nhưng không đủ quyền.
- **404 Not Found** — URI không trỏ tới resource (id không tồn tại, hoặc không nằm trong tập client được thấy).
- **409 Conflict** — xung đột trạng thái (ví dụ tạo trùng ràng buộc duy nhất).

Chọn method đúng nhưng status sai (GET trả 201, POST tạo mới trả 200 mà không nói rõ đã tạo) làm API khó hiểu dù URI đẹp.

---

## 6. Xác thực gắn với REST

Vì REST **stateless**, mỗi request tự mang thông tin nhận diện client, ví dụ token trên header hoặc session cookie. Không gửi lại mật khẩu cho mọi thao tác sau khi đăng nhập.

Xác thực chỉ trả lời “đây là ai”. **Phân quyền** (khách xem lịch, khách hàng đặt vé, nhân viên quản trị) vẫn do server quyết theo danh tính đó. Thiếu chứng thực → 401; đã biết ai nhưng không đủ quyền → 403.

---

## 7. Áp vào domain Cinema (tư duy, không phải đặc tả cài đặt)

Áp dụng khái niệm vào bài toán rạp chiếu — chỉ để thấy **resource × method**.

| Resource | Đọc (GET) | Đổi dữ liệu |
|----------|-----------|-------------|
| Phim | Xem danh sách / chi tiết | Tạo–sửa thuộc lớp quản trị (PUT/PATCH); xóa cứng nếu có thì DELETE |
| Suất chiếu | Xem lịch, xem một suất, xem sơ đồ ghế | Đặt ghế là **tạo vé** (POST trên ngữ cảnh suất), không phải GET có side-effect |
| Vé | Xem vé của mình / một vé | Thanh toán hoặc hủy là **đổi trạng thái vé** (thường POST nghiệp vụ hoặc PATCH status); giữ lịch sử thì không DELETE vật lý |

Nguyên tắc khi chọn method:

1. Mọi thao tác **chỉ xem** → GET.
2. **Sinh bản ghi mới** (vé đang giữ, token phiên làm việc, tài khoản mới) → POST.
3. **Sửa field** đã có → PATCH (một phần) hoặc PUT (cả bản ghi).
4. **Bỏ hẳn bản ghi** và không cần nhật ký → DELETE; nếu chỉ đánh dấu hủy → đổi status, không giả DELETE.
5. Không nhét side-effect vào GET.

Trên pet project Cinema, hợp đồng khách điển hình đọc như sau (ý nghĩa, không phải hướng dẫn implement):

- Public: đọc phim, đọc suất, đọc sơ đồ ghế; đổi mật khẩu/tên đăng nhập lấy token bằng POST.
- Khách hàng đã xác thực: POST đặt ghế trên một suất (tạo vé, thường 201); GET vé của mình; POST thanh toán hoặc hủy (đổi status, thường 200).
- Phân trang list trả về thông tin “tổng số / trang sau / trang trước / danh sách”, không trả một mảng trần không kiểm soát được.

Vì sao đặt ghế / thanh toán / hủy dùng POST: đặt ghế **tạo resource mới**; thanh toán và hủy là **xử lý nghiệp vụ** đổi status, không thay thế toàn bộ vé (PUT) và không xóa bản ghi (DELETE). Tính idempotent không đảm bảo — đúng chỗ của POST.

---

## 8. Kết luận

- REST tổ chức API theo **resource**, **URI**, **representation**, **stateless**, **uniform interface**.
- HTTP methods phân vai rõ: GET đọc; POST tạo hoặc kích hoạt xử lý; PUT thay toàn bộ; PATCH sửa một phần; DELETE gỡ resource; HEAD / OPTIONS hỗ trợ metadata và khám phá khả năng.
- **Safe** và **idempotent** là tiêu chí chọn method, không phải chi tiết công nghệ.
- Status code hoàn thiện hợp đồng REST: method đúng phải đi kèm mã kết quả đúng nghĩa.
- Xác thực đi kèm từng request; quyền hạn là lớp quyết định phía server.

Nắm các khái niệm trên là đủ để đọc, thiết kế và giải thích một RESTful API. Phần cài đặt cụ thể thuộc thực hành kỹ thuật, nằm ngoài phạm vi báo cáo này.
