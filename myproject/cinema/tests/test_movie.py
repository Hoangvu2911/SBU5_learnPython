from rest_framework.test import APITestCase
from cinema.models import Movie
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class MovieStaffTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            password="123123",
            is_staff=True,
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token.key}",
        )
        self.movie = Movie.objects.create(
            title="Test Movie",
            description="Test Description",
            release_date="2026-01-01",
            genre="Test Genre",
            rating=8.5,
            duration_minutes=120,
            director="Test Director",
        )

    def test_list_movies(self):
        res = self.client.get("/api/movies/", format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["count"], 1)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["title"], "Test Movie")

    def test_create_movie(self):
        res = self.client.post(
            "/api/movies/",
            {
                "title": "Test Movie 2",
                "description": "Test Description 2",
                "release_date": "2026-01-02",
                "genre": "Test Genre 2",
                "rating": 9.0,
                "duration_minutes": 130,
                "director": "Test Director 2",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["title"], "Test Movie 2")
        self.assertEqual(res.data["description"], "Test Description 2")
        self.assertEqual(res.data["release_date"], "2026-01-02")
        self.assertEqual(res.data["genre"], "Test Genre 2")
        self.assertEqual(res.data["rating"], "9.0")
        self.assertEqual(res.data["duration_minutes"], 130)
        self.assertEqual(res.data["director"], "Test Director 2")

    def test_create_movie_failure_missing_fields(self):
        res = self.client.post(
            "/api/movies/",
            {
                "title": "Test Movie 2",
                "description": "Test Description 2",
                "release_date": "2026-01-02",
                "genre": "Test Genre 2",
            },
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("rating", res.data)
        self.assertIn("duration_minutes", res.data)
        self.assertIn("director", res.data)

    def test_create_movie_failure_invalid_fields(self):
        res = self.client.post(
            "/api/movies/",
            {
                "title": "Test Movie 2",
                "description": "Test Description 2",
                "release_date1": "2026-01-02",
            },
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("release_date", res.data)
        self.assertIn("genre", res.data)
        self.assertIn("rating", res.data)
        self.assertIn("duration_minutes", res.data)
        self.assertIn("director", res.data)

    def test_retrieve_movie(self):
        res = self.client.get(f"/api/movies/{self.movie.id}/", format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["title"], "Test Movie")
        self.assertEqual(res.data["description"], "Test Description")
        self.assertEqual(res.data["release_date"], "2026-01-01")
        self.assertEqual(res.data["genre"], "Test Genre")
        self.assertEqual(res.data["rating"], "8.5")
        self.assertEqual(res.data["duration_minutes"], 120)
        self.assertEqual(res.data["director"], "Test Director")

    def test_edit_movie(self):
        res = self.client.patch(
            f"/api/movies/{self.movie.id}/",
            {
                "title": "Test Movie 2",
                "description": "Test Description 2",
                "release_date": "2026-01-02",
            },
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["title"], "Test Movie 2")
        self.assertEqual(res.data["description"], "Test Description 2")
        self.assertEqual(res.data["release_date"], "2026-01-02")
        self.assertEqual(res.data["genre"], "Test Genre")
        self.assertEqual(res.data["rating"], "8.5")
        self.assertEqual(res.data["duration_minutes"], 120)
        self.assertEqual(res.data["director"], "Test Director")

    def test_toggle_movie(self):
        res = self.client.post(f"/api/movies/{self.movie.id}/toggle/", format="json")
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.data["is_active"])


class MovieCustomerTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="customer",
            password="123123",
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token.key}",
        )

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
        self.movie2 = Movie.objects.create(
            title="Test Movie2",
            description="Test Description2",
            release_date="2026-01-02",
            genre="Test Genre2",
            rating=9.0,
            duration_minutes=120,
            director="Test Director2",
            is_active=False,
        )
    
    def test_list_movies(self):
        res = self.client.get("/api/movies/", format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["count"], 1)
        self.assertEqual(res.data["results"][0]["title"], "Test Movie")

    def test_create_movie(self):
        res = self.client.post(
            "/api/movies/",
            {
                "title": "Test Movie 2",
                "description": "Test Description 2",
                "release_date": "2026-01-02",
                "genre": "Test Genre 2",
                "rating": 9.0,
                "duration_minutes": 130,
                "director": "Test Director 2",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 403)
        self.assertIn("detail", res.data)
        self.assertEqual(res.data["detail"], "You do not have permission to perform this action.")

    def test_retrieve_movie(self):
        res = self.client.get(f"/api/movies/{self.movie.id}/", format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["title"], "Test Movie")
        self.assertEqual(res.data["description"], "Test Description")
        self.assertEqual(res.data["release_date"], "2026-01-01")
        self.assertEqual(res.data["genre"], "Test Genre")
        self.assertEqual(res.data["rating"], "8.5")
        self.assertEqual(res.data["duration_minutes"], 120)
        self.assertEqual(res.data["director"], "Test Director")

    def test_retrieve_movie_failure_not_found(self):
        res = self.client.get(f"/api/movies/999999/", format="json")
        self.assertEqual(res.status_code, 404)
        self.assertIn("detail", res.data)
        self.assertEqual(res.data["detail"], "No Movie matches the given query.")

    def test_retrieve_movie_failure_inactive(self):
        res = self.client.get(f"/api/movies/{self.movie2.id}/", format="json")
        self.assertEqual(res.status_code, 404)
        self.assertIn("detail", res.data)
        self.assertEqual(res.data["detail"], "No Movie matches the given query.")