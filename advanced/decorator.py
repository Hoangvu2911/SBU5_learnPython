# def uppercase_decorator(function):
#     def wrapper() :
#         return function().upper()
#     return wrapper

# @uppercase_decorator
# def say_hello():
#     return "hello"

# print(say_hello())
#######################
# def a_decorator_arguments(function):
#     def wrapper_accepting_arguments(*arg1, **arg2):
#         print('The positional arguments are: ', arg1)
#         print('The keyword arguments are: ', arg2)
#         function(*arg1, **arg2)
#     return wrapper_accepting_arguments

# @a_decorator_arguments
# def function_with_arguments(a, b, c):
#     print(a, b, c)

# @a_decorator_arguments
# def function_with_keyword_arguments(**d):
#     print(d)

# function_with_arguments(1, 2, 3)
# function_with_keyword_arguments(name="hoang", age=20, city="Hanoi")
#######################
# class uppercase_decorator:
#     def __init__(self, function):
#         self.function = function

#     def __call__(self, *args, **kwargs):
#         result = self.function(*args, **kwargs)
#         return result.upper()

# @uppercase_decorator
# def say_hello():
#     return "hello"

# print(say_hello())
#######################
import functools
import time

class timer:
    def __init__(self, function):
        self.function = function
        functools.update_wrapper(self, function, updated=())

    def __call__(self, *args, **kwargs):
        start = time.time()
        result = self.function(*args, **kwargs)
        elapsed = time.time() - start
        print(f"[timer] {self.__name__}: {elapsed:.6f}s")
        return result

class log:
    def __init__(self, function):
        self.function = function
        functools.update_wrapper(self, function, updated=())

    def __call__(self, *args, **kwargs):
        print(f"[log] call {self.__name__}(args={args}, kwargs={kwargs})")
        result = self.function(*args, **kwargs)
        print(f"[log] {self.__name__} -> {result!r}")
        return result

@timer
@log
def greet(name):
    time.sleep(0.1)
    return f"hello {name}"

@timer
@log
def add(a, b):
    time.sleep(0.05)
    return a + b


print("--- greet ---")
print(greet("Hoang"))

print("--- add ---")
print(add(1, 2))
