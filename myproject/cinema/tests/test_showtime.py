from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from cinema.models import Movie, Room, Showtime, Ticket
from cinema.seats import SeatHoldStore


class ShowtimeApiTestCase(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="admin", password="123123", is_staff=True)
        self.user = User.objects.create_user(username="customer", password="123123")
        self.room = Room.objects.create(name="IMAX", capacity=20)
        self.movie = Movie.objects.create(
            title="Mad Max",
            description="Action",
            release_date="2026-01-01",
            genre="Action",
            rating=8.0,
            duration_minutes=120,
            director="Miller",
            is_active=True,
        )
        now = timezone.now()
        self.scheduled = Showtime.objects.create(
            movie=self.movie,
            room=self.room,
            start_at=now + timedelta(days=1),
            end_at=now + timedelta(days=1, hours=2),
            base_price=150000,
            status=Showtime.Status.SCHEDULED,
        )
        self.completed = Showtime.objects.create(
            movie=self.movie,
            room=Room.objects.create(name="VIP", capacity=20),
            start_at=now - timedelta(hours=3),
            end_at=now - timedelta(hours=1),
            base_price=200000,
            status=Showtime.Status.COMPLETED,
        )
        SeatHoldStore.clear_showtime(self.scheduled.id)

    def test_customer_list_hides_completed(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        res = self.client.get("/api/showtimes/")
        self.assertEqual(res.status_code, 200)
        ids = [item["id"] for item in res.data["results"]]
        self.assertIn(self.scheduled.id, ids)
        self.assertNotIn(self.completed.id, ids)

    def test_seats_map(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        Ticket.objects.create(
            showtime=self.scheduled,
            customer=self.user,
            seat="A1",
            price=150000,
            status=Ticket.Status.BOOKED,
        )
        res = self.client.get(f"/api/showtimes/{self.scheduled.id}/seats/")
        self.assertEqual(res.status_code, 200)
        seats = {row["seat"]: row["status"] for row in res.data["seats"]}
        self.assertEqual(seats["A1"], "booked")
        self.assertEqual(seats["A2"], "available")

    def test_staff_create_and_cancel_showtime(self):
        token = Token.objects.create(user=self.staff)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        start = timezone.now() + timedelta(days=3)
        res = self.client.post(
            "/api/showtimes/",
            {
                "movie": self.movie.id,
                "room": self.room.id,
                "start_at": start.strftime("%Y-%m-%dT%H:%M"),
                "base_price": "120000.00",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201)

        res = self.client.post(f"/api/showtimes/{self.scheduled.id}/cancel/", format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["showtime"]["status"], "cancelled")
