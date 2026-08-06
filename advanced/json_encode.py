import json

vehicle = {
    "brand": "Toyota",
    "model": ["Corolla", "Camry", "Rav4"],
    "year": 2020
}

with open("vehicle.json", "w") as file:
    json.dump(vehicle, file, indent=2)