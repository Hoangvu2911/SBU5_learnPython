import pickle

class Vehicle:
    def __init__(self, brand, model, year):
        self.brand = brand
        self.model = model
        self.year = year

with open("vehicle.pkl", "rb") as file:
    serialized = file.read()
    vehicle = pickle.loads(serialized)

print(vehicle.brand, vehicle.model, vehicle.year)