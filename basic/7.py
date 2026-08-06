def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


def sum_array(numbers: list[int]) -> int:
    return sum(numbers)


def find_max(numbers: list[int]) -> int:
    if not numbers:
        raise ValueError("numbers must not be empty")
    return max(numbers)

def square(x: int) -> int:
    return x * x

def is_even(x: int) -> bool:
    return x % 2 == 0


def demo_map_filter_sorted(numbers: list[int]) -> tuple[list[int], list[int], list[int]]:
    squared = list(map(square, numbers))
    evens = list(filter(is_even, numbers))
    sorted_desc = sorted(numbers, reverse=True)
    return squared, evens, sorted_desc

def test_is_prime() -> None:
    assert is_prime(2) is True
    assert is_prime(3) is True
    assert is_prime(4) is False
    assert is_prime(17) is True
    assert is_prime(1) is False
    assert is_prime(-5) is False


def test_sum_array() -> None:
    assert sum_array([1, 2, 3, 4]) == 10
    assert sum_array([]) == 0
    assert sum_array([-1, 1, 5]) == 5


def test_find_max() -> None:
    assert find_max([1, 3, 2]) == 3
    assert find_max([-10, -3, -7]) == -3


def test_demo_map_filter_sorted() -> None:
    numbers = [5, 2, 9, 4, 1]
    squared, evens, sorted_desc = demo_map_filter_sorted(numbers)
    assert squared == [25, 4, 81, 16, 1]
    assert evens == [2, 4]
    assert sorted_desc == [9, 5, 4, 2, 1]


if __name__ == "__main__":
    data = [5, 2, 9, 4, 1]
    print("is_prime(17):", is_prime(17))
    print("sum_array(data):", sum_array(data))
    print("find_max(data):", find_max(data))

    squared_values, even_values, sorted_values = demo_map_filter_sorted(data)
    print("map (square):", squared_values)
    print("filter (even):", even_values)
    print("sorted (desc):", sorted_values)