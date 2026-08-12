from rest_framework.test import APITestCase
from cinema.models import Ticket
from django.contrib.auth.models import User
from cinema.models import Movie, Room, Showtime
from rest_framework.authtoken.models import Token
from datetime import timedelta
from django.utils import timezone
from cinema.seats import SeatHoldStore

class TicketCustomerTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="customer",
            password="123123",
        )
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        self.room = Room.objects.create(name="Room 1", capacity=50)
        self.movie = Movie.objects.create(
            title="Test Movie",
            description="Test Description",
            release_date="2026-01-01",
            genre="Test Genre",
            rating=8.5,
            duration_minutes=120,
            director="Test Director",
            is_active=True,
        )
        now = timezone.now()
        start = now + timedelta(days=1)
        end = start + timedelta(hours=2)
        self.showtime = Showtime.objects.create(
            movie=self.movie,
            room=self.room,
            start_at=start,
            end_at=end,
            base_price=100000.00,
        )
        completed_start = now - timedelta(hours=3)
        completed_end = now - timedelta(hours=1)
        self.showtime2 = Showtime.objects.create(
            movie=self.movie,
            room=self.room,
            start_at=completed_start,
            end_at=completed_end,
            base_price=100000.00,
            status=Showtime.Status.COMPLETED,
        )
        self.ticket = Ticket.objects.create(
            showtime=self.showtime,
            customer=self.user,
            seat="A1",
            price=100000.00,
            status=Ticket.Status.PENDING,
        )
        SeatHoldStore.clear_showtime(self.showtime.id)
        SeatHoldStore.clear_showtime(self.showtime2.id)


    def test_list_tickets(self):
        res = self.client.get("/api/tickets/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["count"], 1)
        item = res.data["results"][0]
        self.assertEqual(item["id"], self.ticket.id)
        self.assertEqual(item["showtime"], self.showtime.id)
        self.assertEqual(item["seat"], "A1")
        self.assertEqual(item["customer"], "customer")
        self.assertEqual(item["status"], "pending")

    def test_create_ticket_via_ticket_post_method(self):
        res = self.client.post(
            "/api/tickets/",
            {
                "showtime": self.showtime.id,
                "seat": "A2",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 405)
        self.assertIn("detail", res.data)

    def test_create_ticket_via_showtime_book_method(self):
        res = self.client.post(
            f"/api/showtimes/{self.showtime.id}/book/",
            {
                "seat": "A2",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["seat"], "A2")
        self.assertEqual(res.data["price"], "100000.00")
        self.assertEqual(res.data["status"], "pending")
        self.assertEqual(res.data["customer"], "customer")
    
    def test_create_ticket_via_showtime_book_method_failure_showtime_completed(self):
        res = self.client.post(
            f"/api/showtimes/{self.showtime2.id}/book/",
            {
                "seat": "A1",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("detail", res.data)
        self.assertEqual(res.data["detail"], "Suất không còn bookable")

    def test_create_ticket_via_showtime_book_method_failure_seat_already_booked(self):
        res = self.client.post(
            f"/api/showtimes/{self.showtime.id}/book/",
            {
                "seat": "A1",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("detail", res.data)
        self.assertEqual(res.data["detail"], "Ghế đã được giữ/đặt")

    def test_cancel_ticket(self):
        res = self.client.post(
            f"/api/tickets/{self.ticket.id}/cancel/",
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["status"], "cancelled")
    
    def test_delete_ticket(self):
        res = self.client.delete(
            f"/api/tickets/{self.ticket.id}/",
            format="json",
        )
        self.assertEqual(res.status_code, 405)
        self.assertIn("detail", res.data)
        self.assertEqual(res.data["detail"], 'Method "DELETE" not allowed.')


class TicketStaffTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            password="123123",
            is_staff=True,
        )
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        self.room = Room.objects.create(name="Room 1", capacity=50)
        self.movie = Movie.objects.create(
            title="Test Movie",
            description="Test Description",
            release_date="2026-01-01",
            genre="Test Genre",
            rating=8.5,
            duration_minutes=120,
            director="Test Director",
        )
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=2)
        self.showtime = Showtime.objects.create(
            movie=self.movie,
            room=self.room,
            start_at=start,
            end_at=end,
            base_price=100000,
        )
        self.ticket = Ticket.objects.create(
            showtime=self.showtime,
            customer=self.user,
            seat="A1",
            price=100000,
            status=Ticket.Status.PENDING,
        )
