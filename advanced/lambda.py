nums = [7, 4, 3, 9, 6]

doubled = list(map(lambda x: x * 2, nums))
print(doubled)

filtered = list(filter(lambda x: x%2 == 0, nums))
print(filtered)

sorted_desc = list(sorted(nums, key=lambda x: -x))
print(sorted_desc)