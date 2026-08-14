from typing import Protocol
from django.conf import settings

from cinema.services.redis import get_client, redis_available

def _hold_key(showtime_id: int, seat: str) -> str:
    return f"Hold:{showtime_id}:{seat}"

class SeatHoldPort(Protocol):
    def acquire(self, showtime_id: int, seat: str, user_id: int) -> bool:
        pass
    
    def release(self, showtime_id: int, seat: str) -> None:
        pass

    def held_seats(self, showtime_id: int) -> set[str]:
        pass
    
    def clear_showtime(self, showtime_id: int) -> None:
        pass

class RedisSeatHoldAdapter:
    def acquire(self, showtime_id: int, seat: str, user_id: int) -> bool:
        return bool(
            get_client().set(
                _hold_key(showtime_id, seat),
                user_id,
                ex=settings.SEAT_HOLD_TIMEOUT,
                nx=True,
            )
        )

    def release(self, showtime_id: int, seat: str) -> None:
        get_client().delete(_hold_key(showtime_id, seat))

    def held_seats(self, showtime_id: int) -> set[str]:
        prefix = f"Hold:{showtime_id}:"
        return {
            k[len(prefix):]
            for k in get_client().scan_iter(match=f"{prefix}*", count=200)
        }

    def clear_showtime(self, showtime_id: int) -> None:
        r = get_client()
        keys = list(r.scan_iter(match=f"Hold:{showtime_id}:*", count=100))
        if keys:
            r.delete(*keys)

class RedisHoldStrategy:
    def __init__(self, port: SeatHoldPort | None = None):
        self.port = port or RedisSeatHoldAdapter()

    def acquire(self, showtime_id: int, seat: str, user_id: int) -> bool:
        return self.port.acquire(showtime_id, seat, user_id)

    def release(self, showtime_id: int, seat: str) -> None:
        self.port.release(showtime_id, seat)

    def held_seats(self, showtime_id: int) -> set[str]:
        return self.port.held_seats(showtime_id)

    def clear_showtime(self, showtime_id: int) -> None:
        self.port.clear_showtime(showtime_id)

class PassthroughSeatHold:
    def acquire(self, showtime_id: int, seat: str, user_id: int) -> bool:
        return True
    
    def release(self, showtime_id: int, seat: str) -> None:
        return None

    def held_seats(self, showtime_id: int) -> set[str]:
        return set()

    def clear_showtime(self, showtime_id: int) -> None:
        return None

def get_hold_strategy() -> SeatHold:
    if redis_available():
        return RedisHoldStrategy()
    return PassthroughSeatHold()