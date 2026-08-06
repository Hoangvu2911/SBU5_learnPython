def multiplication_table(n):
    for i in range(1, 11):
        print(f"{n} x {i} = {n * i}")

def factorial(n):
    f = 1
    for i in range(1, n + 1):
        f *= i
    return f


def triangle(n) :
    for i in range(1, n + 1):
        print("*" * i)


def demo_while_break_continue(n):
    i = 1
    while i <= 10:
        product = n * i

        if i == 5:
            i += 1
            continue

        print(f"{n} x {i} = {product}")

        if i == 10:
            break

        i += 1


if __name__ == "__main__":
    n = int(input("Enter a number: "))

    multiplication_table(n)
    print(f"Factorial of {n}: {factorial(n)}")

    demo_while_break_continue(n)
    triangle(n)