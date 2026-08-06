# Báo cáo — Advanced: CLI args, Lambda, Format, Comprehension, Threading, Memory, Copy + CLI Log Analyzer

## 1. Đã hoàn thành
- Truyền tham số qua command line (`advanced/args.py`)
- Lambda function (`advanced/lambda.py`)
- String format (`advanced/format.py`)
- List / set comprehension (`advanced/comprehension.py`)
- Multi-thread (`advanced/threading_demo.py`)
- Quản lý và giải phóng bộ nhớ (`advanced/memory.py`)
- Shallow copy và deep copy (`advanced/copy_demo.py`)
- Demo CLI Log Analyzer (`advanced/demo_cli.py`)

---

## 2. Kiến thức đã nắm

### 2.1 Truyền arguments qua command line
- Cho phép truyền dữ liệu vào chương trình lúc chạy, không cần sửa mã nguồn
- Module `argparse` hỗ trợ định nghĩa tham số, kiểu dữ liệu, mô tả trợ giúp
- **Optional argument:** có tiền tố `--` hoặc `-`, người dùng tự chọn có truyền hay không
- **Positional argument:** bắt buộc, không cần tiền tố
- Có thể ép kiểu, giới hạn lựa chọn hợp lệ, và hiện hướng dẫn khi dùng `-h`

→ Thực hành: máy tính dòng lệnh nhận hai số và phép toán (`args.py`)

### 2.2 Lambda function
- Hàm ẩn danh, chỉ gồm một biểu thức, viết gọn khi không cần đặt tên
- Thường kết hợp với `map`, `filter`, `sorted` để biến đổi / lọc / sắp xếp nhanh
- Không phù hợp khi logic dài, cần nhiều câu lệnh, hoặc cần tài liệu hóa rõ ràng — lúc đó dùng `def`

→ Thực hành: nhân đôi phần tử, lọc số chẵn, sắp xếp giảm dần (`lambda.py`)

### 2.3 String format
- f-string cho phép nhúng biểu thức vào chuỗi và định dạng hiển thị
- Căn lề trái / phải / giữa theo độ rộng cột; làm tròn số thực theo số chữ số thập phân
- Độ rộng cột có thể lấy từ biến → dễ in bảng dữ liệu trên terminal

→ Thực hành: in bảng thông tin người dùng căn cột (`format.py`)

### 2.4 List comprehension
- Cách viết gọn để tạo list mới từ iterable, thay vòng lặp + thêm từng phần tử
- Có thể kết hợp điều kiện lọc; biến thể tương tự cho set và dict
- Comprehension lồng nhau dùng để làm phẳng cấu trúc nhiều tầng (ví dụ ma trận → list một chiều)
- Ưu điểm: ngắn, dễ đọc với thao tác đơn giản; hạn chế: phức tạp quá sẽ khó hiểu

→ Thực hành: đối chiếu kết quả vòng `for` với comprehension cho transform, filter, set, flatten (`comprehension.py`)

### 2.5 Multi-thread
- Thread cho phép nhiều luồng chạy “song song” trong một process
- Hữu ích khi công việc phải **chờ I/O** (mạng, đĩa, sleep): trong lúc một thread chờ, thread khác vẫn làm việc
- Luồng đời sống cơ bản: tạo thread → start → join (đợi hoàn tất)
- Pattern phổ biến: hàng đợi việc + nhiều worker lấy việc từ queue
- Cần giữ chỉ số gốc của từng việc nếu muốn kết quả đúng thứ tự dù hoàn thành lệch thời gian
- CPython có GIL: tác vụ nặng CPU thường không tăng tốc rõ; tác vụ chờ I/O thì threading có lợi

→ Thực hành: so sánh tải tuần tự và tải bằng nhiều worker — threaded nhanh hơn rõ khi mỗi việc có thời gian chờ (`threading_demo.py`)

### 2.6 Quản lý và giải phóng bộ nhớ

**Reference counting (CPython)**
- Mỗi object giữ bộ đếm số tham chiếu đang trỏ tới nó
- Gán thêm biến → tăng count; `del` hoặc gán lại → giảm count
- Count về 0 → object thường được giải phóng ngay
- `sys.getrefcount` dùng để quan sát; kết quả có thể cao hơn số biến thật vì bản thân lời gọi cũng tạm giữ thêm một tham chiếu

**Garbage Collection (GC)**
- Reference counting không xử lý được **vòng tham chiếu** (A trỏ B, B trỏ A): count không về 0 dù không còn dùng từ bên ngoài
- Module `gc` bổ sung cơ chế quét và thu hồi các cycle (generational GC)
- Có thể gọi `gc.collect()` để ép thu hồi

→ Thực hành: theo dõi refcount khi thêm/xóa tham chiếu; tạo cycle rồi thu hồi bằng GC (`memory.py`)

### 2.7 Shallow copy và deep copy

| | Shallow copy | Deep copy |
|--|--------------|-----------|
| Bản ngoài | Tạo object mới | Tạo object mới |
| Phần tử lồng nhau (list/dict bên trong) | Vẫn dùng chung tham chiếu với bản gốc | Sao chép đệ quy, độc lập hoàn toàn |
| Sửa phần tử bên trong bản sao | Có thể làm thay đổi bản gốc | Không ảnh hưởng bản gốc |

- Dùng shallow khi cấu trúc nông hoặc chấp nhận chia sẻ phần bên trong
- Dùng deep khi cần bản sao độc lập hoàn toàn (dữ liệu lồng nhau)

→ Thực hành: sửa list con trên bản shallow/deep và quan sát ảnh hưởng lên bản gốc (`copy_demo.py`)

---

## 3. Demo CLI Log Analyzer

Công cụ dòng lệnh đọc file log, lọc theo mức độ và từ khóa. Mục tiêu: ghép nhiều kỹ thuật đã học vào một bài thực tế.

**Ý tưởng chính**
- Nhận đường dẫn file và tùy chọn lọc từ dòng lệnh
- Đóng gói logic trong class: đọc file → lọc → hiển thị
- Lọc theo level bằng regex khớp dạng tag trong log
- Tìm từ khóa bằng lambda + `filter` (không phân biệt hoa thường)
- Dùng comprehension khi lọc theo level; đọc file trong `with` để đóng file an toàn

**Kỹ thuật được dùng:** argparse, class/method, lambda, list comprehension, regex, context manager, f-string

→ Chi tiết triển khai: `advanced/demo_cli.py` (file mẫu `demo_cli.log`)

---

## 4. Mapping file thực hành

| File | Nội dung chính |
|------|----------------|
| `advanced/args.py` | CLI calculator với argparse |
| `advanced/lambda.py` | map / filter / sorted với lambda |
| `advanced/format.py` | f-string căn cột bảng |
| `advanced/comprehension.py` | List/set comprehension vs vòng for |
| `advanced/threading_demo.py` | So sánh sequential và threaded |
| `advanced/memory.py` | Reference counting và cyclic GC |
| `advanced/copy_demo.py` | Shallow copy vs deep copy |
| `advanced/demo_cli.py` | CLI Log Analyzer tổng hợp |
| `advanced/demo_cli.log` | File log mẫu |

---

## 5. Kết luận
Đã nắm cách truyền tham số CLI, dùng lambda / định dạng chuỗi / comprehension để viết gọn hơn, hiểu khi nào multi-thread có lợi, cơ chế giải phóng bộ nhớ (refcount + GC) và khác biệt shallow/deep copy. Demo Log Analyzer cho thấy các kỹ thuật trên kết hợp được thành một công cụ CLI thực tế.
