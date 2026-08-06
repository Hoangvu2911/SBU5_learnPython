"""
Report ngắn: Garbage Collection & Reference Counting (Python)

1) Reference counting (đếm tham chiếu)
- Mỗi object có bộ đếm: bao nhiêu tên/biến đang trỏ tới nó.
- a = obj → +1; del a / gán lại → -1.
- Khi count = 0 → object bị giải phóng ngay (thường là vậy với CPython).
- sys.getrefcount(x) trả về số tham chiếu hiện tại.
  Lưu ý: kết quả thường lớn hơn 1 vì chính lời gọi getrefcount cũng tạm giữ thêm 1 ref.

2) Garbage Collection (GC)
- Reference counting không xử lý được vòng tròn (cycle):
  A → B → A, count không về 0 dù không còn dùng từ bên ngoài.
- Module `gc` quét và thu hồi các cycle này (generational GC).
- Có thể: gc.collect(), gc.get_count(), gc.disable()/enable().

3) Tóm tắt
- Refcount = cơ chế chính, giải phóng nhanh khi hết tham chiếu.
- GC = bổ sung cho cyclic references.
"""

import gc
import sys


def show_refcount(label: str, obj) -> None:
    print(f"{label}: getrefcount = {sys.getrefcount(obj)}")

print("=== Demo Reference Counting ===")

x = []
show_refcount("sau khi tạo x", x)

y = x 
show_refcount("sau y = x", x)

z = x
show_refcount("sau z = x", x)

del y
show_refcount("sau del y", x)

del z
show_refcount("sau del z", x)

print("\n=== Demo Cyclic GC ===")


class Node:
    def __init__(self, name: str):
        self.name = name
        self.other = None


a = Node("A")
b = Node("B")
a.other = b
b.other = a

print(f"Trước del: refcount(a)={sys.getrefcount(a)}, refcount(b)={sys.getrefcount(b)}")

del a, b
collected = gc.collect()
print(f"gc.collect() thu hồi ~{collected} object")

