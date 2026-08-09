from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.db import transaction, IntegrityError
from .models import Ticket, Showtime
from django.db import transaction
from .seats import generate_seats, is_valid_seat


def cleanup_pending(showtime) -> int:
    now = timezone.now()
    ttl = timedelta(seconds=settings.SEAT_HOLD_TTL_SECONDS)
    z = Ticket.objects.filter(
        showtime=showtime,
        status=Ticket.Status.PENDING,
        created_at__lte=now - ttl
    )
    updated = expired_qs.update(status=Ticket.Status.CANCELLED)

    if not showtime.is_bookable(now):
        extra = Ticket.objects.filter(
            showtime=showtime,
            status=Ticket.Status.PENDING,
        ).update(status=Ticket.Status.CANCELLED)
        updated += extra
    return updated


@transaction.atomic
def cancel_showtime(showtime) -> int:
    showtime.status = Showtime.Status.CANCELLED
    showtime.save(update_fields=["status", "updated_at"])
    return Ticket.objects.filter(
        showtime=showtime,
        status__in=[Ticket.Status.PENDING, Ticket.Status.BOOKED],
    ).update(status=Ticket.Status.CANCELLED)


class BookingError(Exception):
    pass


def seat_map(showtime) -> dict[str, str]:
    cleanup_pending(showtime)
    taken_booked = set(
        Ticket.objects.filter(showtime=showtime, status=Ticket.Status.BOOKED)
        .values_list("seat", flat=True)
    )
    taken_held = set(
        Ticket.objects.filter(showtime=showtime, status=Ticket.Status.PENDING)
        .values_list("seat", flat=True)
    )
    rows = []
    for code in generate_seats(showtime.room.capacity):
        if code in taken_booked:
            status = "booked"
        elif code in taken_held:
            status = "held"
        else:
            status = "available"
        rows.append({"seat": code, "status": status})
    return rows

@transaction.atomic
def book(user, showtime, seat: str) -> Ticket:
    cleanup_pending(showtime)
    if not showtime.is_bookable():
        raise BookingError("Suất không còn bookable")
    if not is_valid_seat(seat, showtime.room.capacity):
        raise BookingError("Ghế không hợp lệ")
    try:
        return Ticket.objects.create(
            showtime=showtime,
            customer=user,
            seat=seat,
            price=showtime.base_price,
            status=Ticket.Status.PENDING,
        )
    except IntegrityError as e:
        raise BookingError("Ghế đã được giữ/đặt") from e
    

@transaction.atomic
def pay(user, ticket) -> Ticket:
    showtime = ticket.showtime
    cleanup_pending(showtime)
    ticket.refresh_from_db()
    if ticket.customer_id != user.pk:
        raise BookingError("Không thể thanh toán vé của người khác")
    if ticket.status != Ticket.Status.PENDING:
        raise BookingError("Vé không còn ở trạng thái giữ")
    if not showtime.is_bookable():
        raise BookingError("Suất không còn bookable")
    ticket.status = Ticket.Status.BOOKED
    ticket.save(update_fields=["status", "updated_at"])
    return ticket


@transaction.atomic
def cancel_ticket(user, ticket) -> Ticket:
    showtime = ticket.showtime
    cleanup_pending(showtime)
    ticket.refresh_from_db()
    if ticket.customer_id != user.pk:
        raise BookingError("Không thể hủy vé của người khác")
    if ticket.status not in (Ticket.Status.PENDING, Ticket.Status.BOOKED):
        raise BookingError("Vé không thể hủy")
    if not showtime.is_bookable():
        raise BookingError("Suất đã bắt đầu / đã hủy")
    ticket.status = Ticket.Status.CANCELLED
    ticket.save(update_fields=["status", "updated_at"])
    return ticket