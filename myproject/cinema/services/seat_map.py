from cinema import booking as legacy
from cinema.services.seat_hold import get_hold_strategy
from cinema.seats import generate_seats
from cinema.models import Ticket

class SeatMapBuilder:
    def __init__(self, showtime):
        self._showtime = showtime
        self._booked: set[str] = set()
        self._held: set[str] = set()

    def with_cleanup(self):
        legacy.cleanup_pending(self._showtime)
        return self
    
    def with_booked_seats(self):
        self._booked = set(
            Ticket.objects.filter(
                showtime=self._showtime,
                status=Ticket.Status.BOOKED,
            ).values_list("seat", flat=True)
        )
        return self
    
    def with_held_seats(self):
        held = get_hold_strategy().held_seats(self._showtime.id)
        if not held:
            held = set(
                Ticket.objects.filter(
                    showtime=self._showtime,
                    status=Ticket.Status.PENDING,
                ).values_list("seat", flat=True)
            )
        self._held = held
        return self

    def build(self) -> list[dict]:
        rows = []
        for code in generate_seats(self._showtime.room.capacity):
            if code in self._booked:
                status = "booked"
            elif code in self._held:
                status = "held"
            else:
                status = "available"
            rows.append({
                "seat": code,
                "status": status,
            })
        return rows