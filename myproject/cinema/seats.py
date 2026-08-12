import re
import string

from cinema.redis_client import get_client, redis_available
from django.conf import settings

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
    

def _hold_key(showtime_id: int, seat: str) -> str:
    return f"Hold:{showtime_id}:{seat}"

class SeatHoldStore:
    @staticmethod
    def ttl() -> int:
        return settings.SEAT_HOLD_TTL_SECONDS

    @classmethod
    def acquire(cls, showtime_id: int, seat: str, user_id: int) -> bool:
        if not redis_available():
            return True
        return bool(
            get_client().set(
                _hold_key(showtime_id, seat),
                user_id,
                ex=cls.ttl(),
                nx=True,
            )
        )
    
    @classmethod
    def release(cls, showtime_id: int, seat: str) -> bool:
        if not redis_available():
            return
        get_client().delete(_hold_key(showtime_id, seat))

    @classmethod
    def clear_showtime(cls, showtime_id: int) -> None:
        if not redis_available():
            return
        r = get_client()
        for key in r.scan_iter(match=f"Hold:{showtime_id}:*", count=100):
            r.delete(key)
        
    @classmethod
    def held_seats(cls, showtime_id: int) -> set[str]:
        if not redis_available():
            return set()
        prefix = f"Hold:{showtime_id}:"
        return {
            k[len(prefix):]
            for k in get_client().scan_iter(match=f"{prefix}*", count=200)
        }