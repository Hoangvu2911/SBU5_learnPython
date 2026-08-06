rows = [
    {"name": "Hoang", "age": 22, "amount": 123.456, "city": "Ha Noi", "country": "Viet Nam"},
    {"name": "Alice", "age": 30, "amount": 9876.5, "city": "Tokyo", "country": "Japan"},
    {"name": "Bob", "age": 18, "amount": 45.1, "city": "Berlin", "country": "Germany"},
]

COL = {"name": 8, "age": 5, "amount": 12, "city": 10, "country": 12}

header = (
    f"{'Name':<{COL['name']}} "
    f"{'Age':>{COL['age']}} "
    f"{'Amount ($)':>{COL['amount']}} "
    f"{'City':^{COL['city']}} "
    f"{'Country':<{COL['country']}}"
)

line = "-" * len(header)

print(header)
print(line)

for row in rows:
    print(
        f"{row['name']:<{COL['name']}} "
        f"{row['age']:>{COL['age']}} "
        f"{row['amount']:>{COL['amount']}.2f} "
        f"{row['city']:^{COL['city']}} "
        f"{row['country']:<{COL['country']}}"
    )
