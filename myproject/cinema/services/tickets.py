from django.db import IntegrityError
from cinema.models import Ticket
from cinema.booking import BookingError
from cinema.services.pricing import build_ticket_price
from decimal import Decimal

class TicketFactory:
    @staticmethod
    def create_ticket_pending(showtime, user, seat: str, enable_weekend: bool = False, discount: Decimal | None = None) -> Ticket:
        try:
            return Ticket.objects.create(
                showtime=showtime,
                customer=user,
                seat=seat,
                price=build_ticket_price(showtime, enable_weekend, discount),
                status=Ticket.Status.PENDING,
            )
        except IntegrityError as e:
            raise BookingError("Ghế đã được giữ/đặt") from e
