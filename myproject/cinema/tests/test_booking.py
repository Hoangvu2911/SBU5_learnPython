from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from cinema.booking import book, cancel_showtime, cleanup_pending, pay, seat_map
from cinema.models import Movie, Room, Showtime, Ticket
from cinema.seats import SeatHoldStore


class BookingDomainTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="customer", password="123123")
        self.room = Room.objects.create(name="Room 1", capacity=20)
        self.movie = Movie.objects.create(
            title="Test Movie",
            description="Test Description",
            release_date="2026-01-01",
            genre="Action",
            rating=8.5,
            duration_minutes=120,
            director="Director",
            is_active=True,
        )
        now = timezone.now()
        self.showtime = Showtime.objects.create(
            movie=self.movie,
            room=self.room,
            start_at=now + timedelta(days=1),
            end_at=now + timedelta(days=1, hours=2),
            base_price=100000,
            status=Showtime.Status.SCHEDULED,
        )
        SeatHoldStore.clear_showtime(self.showtime.id)

    def test_cleanup_pending_expires_old_ticket(self):
        ticket = Ticket.objects.create(
            showtime=self.showtime,
            customer=self.user,
            seat="A1",
            price=100000,
            status=Ticket.Status.PENDING,
        )
        old = timezone.now() - timedelta(seconds=settings.SEAT_HOLD_TTL_SECONDS + 5)
        Ticket.objects.filter(pk=ticket.pk).update(created_at=old)
        n = cleanup_pending(self.showtime)
        self.assertEqual(n, 1)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, Ticket.Status.CANCELLED)

    def test_seat_map_statuses(self):
        Ticket.objects.create(
            showtime=self.showtime,
            customer=self.user,
            seat="A1",
            price=100000,
            status=Ticket.Status.BOOKED,
        )
        Ticket.objects.create(
            showtime=self.showtime,
            customer=self.user,
            seat="A2",
            price=100000,
            status=Ticket.Status.PENDING,
        )
        rows = {row["seat"]: row["status"] for row in seat_map(self.showtime)}
        self.assertEqual(rows["A1"], "booked")
        self.assertEqual(rows["A2"], "held")
        self.assertEqual(rows["A3"], "available")

    def test_book_pay_then_cancel_showtime(self):
        ticket = book(self.user, self.showtime, "B1")
        pay(self.user, ticket)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, Ticket.Status.BOOKED)
        n = cancel_showtime(self.showtime)
        self.assertEqual(n, 1)
        self.showtime.refresh_from_db()
        ticket.refresh_from_db()
        self.assertEqual(self.showtime.status, Showtime.Status.CANCELLED)
        self.assertEqual(ticket.status, Ticket.Status.CANCELLED)
