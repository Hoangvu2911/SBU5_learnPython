
class Ticket:
    def __init__(self, customer: str, movie: str, seat: str = "A1") -> None:
        self._customer = customer
        self.__movie = movie
        self.__seat = seat
        self.__status = "booked"

    def get_customer(self) -> str:
        return self._customer

    def get_movie(self) -> str:
        return self.__movie

    def get_seat(self) -> str:
        return self.__seat

    def set_seat(self, seat: str) -> None:
        self.__seat = seat

    def get_status(self) -> str:
        return self.__status

    def cancel(self) -> None:
        self.__status = "cancelled"

    def summary(self) -> str:
        return (
            f"{self.get_customer()} | {self.get_movie()} | "
            f"seat {self.get_seat()} | {self.get_status()}"
        )


if __name__ == "__main__":
    t = Ticket("Hoang", "Dune 2", "A5")
    print(t.summary())
    print("getter:", t.get_customer(), t.get_movie(), t.get_seat())

    t.set_seat("B2")
    print("sau setter seat:", t.summary())

    print("\n=== Chan truy cap truc tiep __movie ===")
    try:
        print(t.__movie)
    except AttributeError as e:
        print(e)

    t.cancel()
    print(t.summary())
