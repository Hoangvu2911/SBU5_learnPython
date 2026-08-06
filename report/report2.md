# Báo cáo — OOP (4 tính chất + phạm vi truy cập) & Advanced (Modules, Decorators)

## 1. Đã hoàn thành
- **OOP:** đóng gói, kế thừa, đa hình, trừu tượng; public / protected / private (`oop/1.py`–`4.py`)
- **Advanced:** Modules & Decorators (`advanced/add.py`, `addOutput.py`, `decorator.py`)

---

## 2. Kiến thức đã nắm

### 2.1 Bốn tính chất OOP

**Đóng gói (Encapsulation)** — gom dữ liệu + hành vi trong class; hạn chế truy cập trực tiếp, dùng getter/setter.  
→ `oop/3.py`: `Ticket` dùng `_customer`, `__movie`/`__seat`/`__status`; truy cập qua `get_*` / `set_seat`.

**Kế thừa (Inheritance)** — class con nhận thuộc tính/method của class cha; có thể mở rộng / ghi đè.  
→ `oop/2.py`: `Customer(User)`, `Admin(User)`; `super().__init__(...)`.

**Đa hình (Polymorphism)** — cùng giao diện, hành vi khác theo từng class.  
→ `oop/2.py`: list `User` chứa `User`/`Customer`/`Admin`, gọi chung `describe()` / `discount_rate()` → kết quả khác nhau.  
→ `oop/4.py`: list `PaymentMethod` gọi chung `receipt()`.

**Trừu tượng (Abstraction)** — chỉ định nghĩa “phải làm gì”, ẩn chi tiết; class trừu tượng không tạo instance trực tiếp.  
→ `oop/4.py`: `PaymentMethod(ABC)` + `@abstractmethod` (`pay`, `method_name`); `CashPayment` / `CardPayment` triển khai cụ thể.

**OOP nền (`oop/1.py`)** — class `Ticket`: `__init__`, method, class attribute (`PRICE_*`), `__str__`, `__del__`.

### 2.2 Phạm vi truy cập (Python)

| Quy ước | Cú pháp | Ý nghĩa |
|---------|---------|---------|
| Public | `self.name` | Truy cập tự do từ ngoài |
| Protected | `self._name` | Nên dùng trong class / subclass (quy ước) |
| Private | `self.__name` | Name mangling → `_Class__name`; ngoài class khó gọi trực tiếp |

→ `oop/3.py`: `t.__movie` lỗi `AttributeError`; dùng getter.  
→ `oop/4.py`: `_owner` (protected), `__card_number` (private).

Python **không** có private cứng như Java — chủ yếu là quy ước + name mangling.

### 2.3 Modules (`advanced/add.py`, `addOutput.py`)
- File `.py` = module; `import add` → dùng `add.add_numbers(...)`
- `from math import sqrt` → lấy tên cụ thể
- `__doc__`: docstring hàm/module
- `__cached__` / `__file__`: thuộc **module**, không thuộc function
- Tránh đặt tên file trùng stdlib (`pickle.py`, `threading.py`, …)

### 2.4 Decorators (`advanced/decorator.py`)
- Decorator bọc hàm để thêm hành vi (log, đo thời gian) mà không sửa thân hàm
- `@deco` ≈ `f = deco(f)`; class decorator dùng `__call__`
- Wrapper nhận `*args, **kwargs` rồi gọi hàm gốc
- `functools.update_wrapper(..., updated=())` giữ `__name__` khi xếp chồng class decorator
- Demo: `@timer` + `@log` trên `greet` / `add` — decorator gần hàm chạy trước

---

## 3. Mapping file thực hành

| File | Nội dung chính |
|------|----------------|
| `oop/1.py` | Class cơ bản, constructor, method, `__str__`/`__del__` |
| `oop/2.py` | Kế thừa + đa hình (`User` / `Customer` / `Admin`) |
| `oop/3.py` | Đóng gói + public/protected/private |
| `oop/4.py` | Trừu tượng (`ABC`) + đa hình thanh toán |
| `advanced/add.py` | Module định nghĩa hàm |
| `advanced/addOutput.py` | Import module, `__doc__`, `__cached__` |
| `advanced/decorator.py` | Class decorator `@timer`, `@log` |

---

## 4. Kết luận
Đã nắm 4 tính chất OOP, phạm vi truy cập theo quy ước Python, module/import và decorator. Hướng tiếp: iterator, Context Manager,  Pickle Module, Json Module, Regex Module
