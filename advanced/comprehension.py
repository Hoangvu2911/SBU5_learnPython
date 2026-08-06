nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]


def show(title, loop, comp):
    print(f"\n=== {title} ===")
    print("loop:", loop)
    print("comprehension:", comp)


loop = []
for x in nums:
    loop.append(x ** 2)
show("Transform list", loop, [x ** 2 for x in nums])

loop = []
for x in nums:
    if x % 2 == 0:
        loop.append(x)
show("Filter even", loop, [x for x in nums if x % 2 == 0])

loop = []
for x in nums:
    if x % 2 == 0:
        loop.append(x ** 2)
show("Filter + transform", loop, [x ** 2 for x in nums if x % 2 == 0])

loop = set()
for x in nums:
    if x % 2 == 0:
        loop.add(x ** 2)
show("Set", loop, {x ** 2 for x in nums if x % 2 == 0})

loop = []
for row in matrix:
    for x in row:
        loop.append(x)
show("Nested flatten", loop, [x for row in matrix for x in row])
