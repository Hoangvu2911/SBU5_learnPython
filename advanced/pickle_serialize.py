import pickle

class Vehicle:
    def __init__(self, brand, model, year):
        self.brand = brand
        self.model = model
        self.year = year

vehicle = Vehicle("Toyota", "Corolla", 2020)

serialized = pickle.dumps(vehicle)

with open("vehicle.pkl", "wb") as file:
    file.write(serialized)
