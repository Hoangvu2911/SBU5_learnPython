num_string = input("Enter a number string: ")
num_integer = 23

print("Before:", type(num_string))

try:
    num_string = int(num_string)
    print("After:", type(num_string))
    num_sum = num_integer + num_string
    print("Sum:", num_sum)
    print("Type of sum:", type(num_sum))
except ValueError:
    print("Please enter a valid numeric string.")