from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    def __init__(self, owner: str) -> None:
        self._owner = owner

    @abstractmethod
    def pay(self, amount: int) -> str:
        pass

    @abstractmethod
    def method_name(self) -> str:
        pass

    def receipt(self, amount: int) -> str:
        return f"{self.method_name()} | {self._owner} | {amount} VND | {self.pay(amount)}"


class CashPayment(PaymentMethod):
    def __init__(self, owner: str) -> None:
        super().__init__(owner)

    def method_name(self) -> str:
        return "Cash"

    def pay(self, amount: int) -> str:
        return f"Pay by cash with {amount} VND successfully"


class CardPayment(PaymentMethod):
    def __init__(self, owner: str, card_number: str) -> None:
        super().__init__(owner)
        self.__card_number = card_number

    def method_name(self) -> str:
        return "Card"

    def pay(self, amount: int) -> str:
        return f"Pay by card {self.__card_number[-4:]} with {amount} VND successfully"


if __name__ == "__main__":
    methods: list[PaymentMethod] = [
        CashPayment("Hoang"),
        CardPayment("An", "4111111111111234"),
    ]

    for method in methods:
        print(method.receipt(150000))
