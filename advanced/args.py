import argparse

parser = argparse.ArgumentParser(description="Calculator")

parser.add_argument("--num1", type=int, help="First number")
parser.add_argument("--num2", type=int, help="Second number")
parser.add_argument("--operation", type=str, help="Operation")

args = parser.parse_args()

if args.operation == "add":
    print(args.num1 + args.num2)
elif args.operation == "sub":
    print(args.num1 - args.num2)
elif args.operation == "mul":
    print(args.num1 * args.num2)
elif args.operation == "div":
    print(args.num1 / args.num2)
else:
    print("Invalid operation")