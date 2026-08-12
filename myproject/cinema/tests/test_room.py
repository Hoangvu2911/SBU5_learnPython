from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from cinema.models import Room


class RoomApiTestCase(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="admin", password="123123", is_staff=True)
        self.user = User.objects.create_user(username="customer", password="123123")
        self.room = Room.objects.create(name="IMAX", capacity=50)

    def test_staff_list_and_create_room(self):
        token = Token.objects.create(user=self.staff)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        res = self.client.get("/api/rooms/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["count"], 1)

        res = self.client.post("/api/rooms/", {"name": "VIP", "capacity": 30}, format="json")
        self.assertEqual(res.status_code, 201)

    def test_customer_cannot_list_rooms(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        res = self.client.get("/api/rooms/")
        self.assertEqual(res.status_code, 403)
