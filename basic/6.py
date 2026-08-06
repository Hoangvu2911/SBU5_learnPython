def divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "Error: Division by zero"
    except ValueError:
        return "Error: Invalid value"
    except Exception as e:
        return f"Error: {e}"
    finally:
        print("Finally block executed")

if __name__ == "__main__":
    print(divide(10, 2))
    print(divide(10, 0))
    print(divide(10, "2"))
    print(divide(10, None))