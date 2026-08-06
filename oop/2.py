class User:
    def __init__(self, name: str, phone: str) -> None:
        self.name = name
        self.phone = phone

    def role(self) -> str:
        return "user"

    def discount_rate(self) -> float:
        return 0.0

    def describe(self) -> str:
        return f"{self.role()} | {self.name} | {self.phone} | discount={self.discount_rate():.0%}"


class Customer(User):
    def __init__(self, name: str, phone: str, points: int = 0) -> None:
        super().__init__(name, phone)
        self.points = points

    def role(self) -> str:
        return "customer"

    def discount_rate(self) -> float:
        return 0.1 if self.points >= 100 else 0.0

    def describe(self) -> str:
        return f"{super().describe()} | points={self.points}"


class Admin(User):
    def __init__(self, name: str, phone: str, cinema: str = "CGV") -> None:
        super().__init__(name, phone)
        self.cinema = cinema

    def role(self) -> str:
        return "admin"

    def discount_rate(self) -> float:
        return 0.2

    def describe(self) -> str:
        return f"{super().describe()} | cinema={self.cinema}"


if __name__ == "__main__":
    users: list[User] = [
        User("Guest", "0000000000"),
        Customer("Hoang", "0901111111", points=120),
        Customer("An", "0902222222", points=20),
        Admin("Lan", "0903333333", cinema="CGV Ha Noi"),
    ]

    print("=== Polimophism ===")
    for user in users:
        print(user.describe())
