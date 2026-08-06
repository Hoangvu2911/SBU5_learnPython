class Ticket:
    PRICE_STANDARD = 70000
    PRICE_VIP = 100000

    def __init__(
        self,
        customer: str = "Guest",
        phone: str = "0000000000",
        movie: str = "Action",
        date: str = "2026-01-01",
        time: str = "18:00",
        seat: str = "A1",
        seat_type: str = "standard",
    ) -> None:
        self.customer = customer
        self.phone = phone
        self.movie = movie
        self.date = date
        self.time = time
        self.seat = seat
        self.seat_type = seat_type.lower()
        self.status = "booked"
        print(f"[INIT] Ticket: {self.customer} - {self.movie} ({self.seat})")

    def get_price(self) -> int:
        return self.PRICE_VIP if self.seat_type == "vip" else self.PRICE_STANDARD

    def change_seat(self, new_seat: str, seat_type: str = "standard") -> None:
        print(f"[CHANGE] {self.seat} -> {new_seat}")
        self.seat = new_seat
        self.seat_type = seat_type.lower()

    def cancel(self) -> None:
        self.status = "cancelled"
        print(f"[CANCEL] {self.customer}")

    def summary(self) -> str:
        return (
            f"{self.customer} | {self.movie} | {self.date} {self.time} | "
            f"seat {self.seat} ({self.seat_type}) | "
            f"{self.get_price()} VND | {self.status}"
        )

    def __str__(self) -> str:
        return self.summary()

    def __del__(self) -> None:
        print(f"[DEL] Ticket: {self.customer} - {self.movie}")


if __name__ == "__main__":
    print("=== Default object ===")
    t0 = Ticket()
    print(t0)

    print("\n=== Create object + call method ===")
    t1 = Ticket("Hoang", "0901111111", "Dune 2", "2026-08-10", "19:30", "A5")
    print(t1)
    print("Price:", t1.get_price())
    t1.change_seat("B7", "vip")
    print(t1.summary())
    t1.cancel()
    print(t1.summary())

    print("\n=== End===")
    del t0
    del t1
