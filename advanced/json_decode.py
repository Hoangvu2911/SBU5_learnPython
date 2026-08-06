import json

with open("vehicle.json", "r") as file:
    data = json.load(file)

print(data)
print(data["brand"], data["model"], data["year"])
