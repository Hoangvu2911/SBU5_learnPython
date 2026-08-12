from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.db import transaction, IntegrityError
from .models import Ticket, Showtime
from .seats import generate_seats, is_valid_seat, SeatHoldStore


def sync_showtime_status(showtime, now=None):
    now = now or timezone.now()
    if showtime.status == Showtime.Status.CANCELLED:
        return showtime
    if now >= showtime.end_at:
        new_status = Showtime.Status.COMPLETED
    elif now >= showtime.start_at:
        new_status = Showtime.Status.ONGOING
    else:
        new_status = Showtime.Status.SCHEDULED
    if showtime.status != new_status:
        showtime.status = new_status
        showtime.save(update_fields=["status", "updated_at"])
    return showtime


def sync_showtimes_bulk(qs=None, now=None):
    now = now or timezone.now()
    qs = Showtime.objects.all() if qs is None else qs
    qs = qs.exclude(status=Showtime.Status.CANCELLED)
    qs.filter(end_at__lte=now).exclude(status=Showtime.Status.COMPLETED).update(
        status=Showtime.Status.COMPLETED,
        updated_at=now,
    )
    qs.filter(start_at__lte=now, end_at__gt=now).exclude(status=Showtime.Status.ONGOING).update(
        status=Showtime.Status.ONGOING,
        updated_at=now,
    )
    qs.filter(start_at__gt=now).exclude(status=Showtime.Status.SCHEDULED).update(
        status=Showtime.Status.SCHEDULED,
        updated_at=now,
    )


def cleanup_pending(showtime) -> int:
    sync_showtime_status(showtime)
    now = timezone.now()
    ttl = timedelta(seconds=settings.SEAT_HOLD_TTL_SECONDS)
    expired_qs = Ticket.objects.filter(
        showtime=showtime,
        status=Ticket.Status.PENDING,
        created_at__lte=now - ttl
    )
    for t in expired_qs.only("seat"):
        SeatHoldStore.release(showtime.id, t.seat)
    updated = expired_qs.update(status=Ticket.Status.CANCELLED)

    if not showtime.is_bookable(now):
        pending_qs = Ticket.objects.filter(
            showtime=showtime,
            status=Ticket.Status.PENDING,
        )
        for t in pending_qs.only("seat"):
            SeatHoldStore.release(showtime.id, t.seat)
        updated += pending_qs.update(status=Ticket.Status.CANCELLED)
    return updated


@transaction.atomic
def cancel_showtime(showtime) -> int:
    sync_showtime_status(showtime)
    if showtime.status not in (Showtime.Status.SCHEDULED):
        raise BookingError("Suất không thể hủy")
    showtime.status = Showtime.Status.CANCELLED
    showtime.save(update_fields=["status", "updated_at"])
    SeatHoldStore.clear_showtime(showtime.id)
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
    taken_held = SeatHoldStore.held_seats(showtime.id)
    if not taken_held:
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
    if not SeatHoldStore.acquire(showtime.id, seat, user.id):
        raise BookingError("Ghế đã được giữ/đặt")
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
    SeatHoldStore.release(showtime.id, ticket.seat)
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
    SeatHoldStore.release(showtime.id, ticket.seat)
    return ticket