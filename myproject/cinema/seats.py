import re
import string

SEAT_RE = re.compile(r'^([A-Z])([1-9]|10)$')

def generate_seats(capacity: int) -> list[str]:
    if capacity < 1 or capacity > 260:
        raise ValueError("Capacity must be between 1 and 260")
    seats = []
    for i, row in enumerate(string.ascii_uppercase):
        for n in range(1, 11):
            seats.append(f"{row}{n}")
            if len(seats) == capacity:
                return seats
    return seats


def is_valid_seat(seat: str, capacity: int) -> bool:
    if not SEAT_RE.match(seat):
        return False
    return seat in generate_seats(capacity)
    