# Báo cáo — Advanced: Iterator, Context Manager, Pickle, JSON, Regex

## 1. Đã hoàn thành
- **Iterator:** tạo class iterator Fibonacci (`advanced/iter.py`)
- **Context Manager:** dùng `with` khi đọc file (`advanced/context.py`)
- **Pickle:** serialize / deserialize object ra file `.pkl` (`pickle_serialize.py`, `pickle_deseralize.py`)
- **JSON:** ghi / đọc object dạng JSON (`json_encode.py`, `json_decode.py`, `vehicle.json`)
- **Regex:** tìm email và số điện thoại bằng `re.findall` (`advanced/regex.py`)

---

## 2. Kiến thức đã nắm

### 2.1 Iterator
- **Iterable:** object có thể duyệt bằng vòng `for` — thường có `__iter__`
- **Iterator:** object trả từng phần tử qua `__next__`; hết thì ném `StopIteration`
- Protocol tối thiểu:
  - `__iter__` → trả về chính iterator
  - `__next__` → trả giá trị tiếp theo hoặc dừng bằng `StopIteration`
- Vòng `for` tự gọi `iter` rồi lặp `next` đến khi hết
- Khác generator: iterator tự viết class; generator dùng `yield` (cú pháp gọn hơn)

→ `advanced/iter.py`: class Fibonacci theo `limit` — sinh dãy đến khi vượt giới hạn, duyệt bằng `for`.

### 2.2 Context Manager
- Dùng để **mở / đóng tài nguyên an toàn** (file, kết nối, lock…), kể cả khi có exception
- Cú pháp `with ... as ...`: vào block gọi `__enter__`, thoát block gọi `__exit__`
- Protocol:
  - `__enter__` → chuẩn bị tài nguyên, có thể trả object gán vào biến `as`
  - `__exit__` → dọn dẹp; trả `True` nếu muốn nuốt exception
- **`contextlib`:** viết context manager bằng generator + decorator `@contextmanager` thay vì class đầy đủ — phần trước `yield` là setup, sau `yield` là teardown
- `open` đã là context manager sẵn → nên mở file trong khối `with`

→ `advanced/context.py`: đọc `file.txt` trong `with` và đo thời gian bằng module `time`.

### 2.3 Pickle Module
- Serialize object Python → bytes; deserialize bytes → object
- Phù hợp lưu **object Python** (class instance, list, dict phức tạp…)
- **Không** dùng pickle với dữ liệu không tin cậy (rủi ro bảo mật khi `loads`)
- API chính:

| Hàm | Việc làm |
|-----|----------|
| `dumps` | Object → bytes |
| `loads` | bytes → object |
| `dump` | Ghi thẳng vào file (binary) |
| `load` | Đọc từ file binary |

- File pickle mở mode ghi/đọc nhị phân (`wb` / `rb`)
- Khi `loads` class tùy chỉnh: class phải còn định nghĩa được trong môi trường chạy

→ `pickle_serialize.py`: tạo object `Vehicle`, serialize rồi ghi `vehicle.pkl`  
→ `pickle_deseralize.py`: đọc `.pkl`, deserialize rồi in brand / model / year

### 2.4 JSON Module
- JSON = text, dùng chung nhiều ngôn ngữ; chỉ hỗ trợ kiểu đơn giản (dict, list, str, số, bool, null)
- **Không** serialize trực tiếp class instance như Pickle → thường chuyển sang dict
- API chính:

| Hàm | Việc làm |
|-----|----------|
| `dumps` | Object → chuỗi JSON |
| `loads` | Chuỗi JSON → object Python |
| `dump` | Ghi JSON vào file |
| `load` | Đọc JSON từ file |

- Tham số `indent` giúp file JSON dễ đọc
- File JSON mở mode text (`w` / `r`), không phải binary

| Pickle | JSON |
|--------|------|
| Binary, giữ được object Python | Text, đa nền tảng |
| Nhanh, linh hoạt với class | Chỉ kiểu JSON chuẩn |
| Không an toàn nếu nguồn lạ | An toàn hơn để trao đổi dữ liệu |

→ `json_encode.py`: dict vehicle → ghi `vehicle.json`  
→ `json_decode.py`: đọc JSON → truy cập theo key

### 2.5 Regex Module (`re`) và các kí tự thường dùng
- Regex = mẫu mô tả chuỗi cần tìm / khớp
- Module `re`; hàm hay dùng: `search`, `match`, `findall`, `sub`, `compile`
- Pattern nên viết dạng raw string để dấu `\` không bị Python xử lý trước

**Kí tự / nhóm quan trọng**

| Kí hiệu | Ý nghĩa | Ví dụ ý tưởng |
|---------|---------|---------------|
| `.` | Mọi kí tự (trừ xuống dòng) | khớp 1 kí tự bất kỳ giữa hai chữ |
| `^` | Đầu chuỗi | chuỗi bắt đầu bằng Hello |
| `$` | Cuối chuỗi | chuỗi kết thúc bằng com |
| `*` | 0 hoặc nhiều | lặp phần trước 0–n lần |
| `+` | 1 hoặc nhiều | ít nhất một chữ số |
| `?` | 0 hoặc 1 | phần tùy chọn |
| `{n}` | Đúng n lần | đúng 3 chữ số |
| `{m,n}` | Từ m đến n lần | mã quốc gia 1–3 chữ số |
| `[]` | Một trong các kí tự | chữ cái a–z hoặc A–Z |
| `[^ ]` | Không thuộc tập | không phải chữ số |
| `\|` | Hoặc | khớp một trong hai mẫu |
| `()` | Nhóm bắt | tách thành các nhóm |
| `\` | Escape kí tự đặc biệt | khớp dấu `+` hoặc `.` thật |
| `\d` | Chữ số | tương đương `[0-9]` |
| `\w` | Chữ / số / `_` | từ khóa đơn giản |
| `\s` | Khoảng trắng | space, tab… |
| `\D` `\W` `\S` | Ngược của `\d` `\w` `\s` | |

→ `advanced/regex.py`: `findall` lấy email (chữ/số + `@` + domain) và số điện thoại dạng `+` kèm nhóm số cách nhau bằng khoảng trắng (vd. +84 …).

---

## 3. Mapping file thực hành

| File | Nội dung chính |
|------|----------------|
| `advanced/iter.py` | Iterator Fibonacci (`__iter__` / `__next__`) |
| `advanced/context.py` | Context manager với `with open` + đo thời gian |
| `advanced/pickle_serialize.py` | Serialize + ghi `vehicle.pkl` |
| `advanced/pickle_deseralize.py` | Đọc `.pkl` + deserialize |
| `advanced/json_encode.py` | Ghi `vehicle.json` |
| `advanced/json_decode.py` | Đọc JSON + truy cập dữ liệu |
| `advanced/vehicle.json` | File JSON mẫu (Toyota / models / year) |
| `advanced/regex.py` | Tìm email & số điện thoại bằng `findall` |

---

## 4. Kết luận
Đã nắm iterator protocol, dùng context manager (`with` / ý tưởng `contextlib`), phân biệt Pickle (object Python) vs JSON (trao đổi text), và các kí tự regex cơ bản kèm thực hành `findall`. Hướng tiếp: arguments CLI, lambda, threading, bộ nhớ, ...
