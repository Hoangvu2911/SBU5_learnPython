import copy

original = [1, 2, [3, 4, 5]]

shallow_copy = copy.copy(original)
deep_copy = copy.deepcopy(original)

shallow_copy[2][0] = 10
deep_copy[2][2] = 10

print(original)
print(shallow_copy)
print(deep_copy)

