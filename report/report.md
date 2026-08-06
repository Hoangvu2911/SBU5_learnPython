# Báo cáo học Python — Basic & OOP

## 1. Đã hoàn thành
- Basic: Variables, DataType, Collections, Conditions, Loop, Function, Exception (`basic/1.py`–`8.py`)
- OOP: class, constructor, destructor, thuộc tính, method (`oop/1.py`)

---

## 2. Kiến thức đã nắm

### Variables & Data Types
- Kiểu cơ bản: `int`, `float`, `str`, `bool`
- Kiểm tra kiểu bằng `type()`
- **Mutable** (đổi được): list, dict, set  
- **Immutable** (không đổi tại chỗ): int, float, str, bool, tuple

### Conditionals
- `if / elif / else`, toán tử so sánh và logic (`and`, `or`, `%`)
- Ứng dụng: xếp loại điểm, năm nhuận (chia 4 / 100 / 400)

### Loops
- `for` + `range`, `while`
- `continue` bỏ vòng hiện tại; `break` thoát vòng
- Ứng dụng: bảng cửu chương, giai thừa, vẽ hình bằng lặp

### Typecasting
- Ép kiểu: `int()`, `float()`, `str()`, …
- Ép sai → `ValueError` → bắt bằng `try/except`

### Exceptions
- Cấu trúc: `try` / `except` / `finally`
- Lỗi hay gặp: `ZeroDivisionError`, `ValueError`, `KeyError`, `TypeError`
- Có thể `raise` lỗi khi input không hợp lệ

### Function & built-in
- Định nghĩa hàm, tham số, `return`, type hint
- Built-in: `sum`, `max`, `len`, `sorted`
- `map` biến đổi, `filter` lọc, `sorted` sắp xếp
- Kiểm thử bằng `assert`

### Collections
| Kiểu | Đặc điểm |
|------|----------|
| list | có thứ tự, trùng được, đổi được |
| tuple | có thứ tự, trùng được, **không** đổi |
| set | không thứ tự, **không trùng**, đổi được |
| dict | key → value, key không trùng |

Ứng dụng: danh bạ (dict + set chống trùng SĐT), CRUD thêm/xem/sửa/xóa.

**OOP** — `class` + object (`self`). Class attribute dùng chung; instance attribute riêng từng object. `__init__` khởi tạo; method = hành vi; `__str__` khi `print`; `__del__` khi object bị hủy. Thực hành qua class `Ticket` (vé phim).

---

## 3. File thực hành
`basic:`
`1.py` syntax → `2.py` kiểu dữ liệu → `3.py` điều kiện → `4.py` vòng lặp → `5.py` ép kiểu → `6.py` exception → `7.py` hàm → `8.py` collections
`oop:`
`1.py` → oop cơ bản 
---

## 4. Kết luận & hướng tiếp
Đã nắm cú pháp nền và OOP cơ bản. Tiếp theo: kế thừa / đa hình, Advanced (decorator, iterator, argparse, threading, …).
