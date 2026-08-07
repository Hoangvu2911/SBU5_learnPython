from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone

from cinema.models import Movie, Actor, MovieActor, Room, Showtime, Ticket

class Command(BaseCommand):
    help = "Seed cinema mock data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding cinema mock data...")
        movies = [
            {
                "title": "The Dark Knight",
                "description": "A superhero movie about a man who becomes a superhero and fights crime.",
                "release_date": datetime(2008, 7, 18),
                "genre": "Action",
                "rating": 9.0,
                "duration_minutes": 152,
                "director": "Christopher Nolan",
            },
            {
                "title": "The Dark Knight Rises",
                "description": "A superhero movie about a man who becomes a superhero and fights crime.",
                "release_date": datetime(2012, 7, 20),
                "genre": "Action",
                "rating": 7.2,
                "duration_minutes": 165,
                "director": "Christopher Nolan",
            },
        ]
        for movie in movies:
            movie, created = Movie.objects.get_or_create(
                title=movie['title'],
                defaults={**movie, "is_active": True, "rating": Decimal(str(movie['rating']))},
            )

        actors = [
            {
                "name": "Christian Bale",
                "bio": "Christian Bale is a British actor known for his roles in The Dark Knight trilogy.",
            },
            {
                "name": "Heath Ledger",
                "bio": "Heath Ledger is an Australian actor known for his roles in The Dark Knight trilogy.",
            },
        ]
        for actor in actors:
            Actor.objects.get_or_create(
                name=actor['name'],
                defaults={**actor, "bio": actor['bio']},
            )

        movie_actors = [
            {
                "movie": 1,
                "actor": 1,
            },
            {
                "movie": 1,
                "actor": 2,
            },
        ]
        movie = Movie.objects.get(title="The Dark Knight")
        a1 = Actor.objects.get(name="Christian Bale")
        a2 = Actor.objects.get(name="Heath Ledger")
        MovieActor.objects.get_or_create(
            movie=movie,
            actor=a1,
        )
        MovieActor.objects.get_or_create(
            movie=movie,
            actor=a2,
        )
        
        rooms = [
            {
                "name": "Room 1",
                "capacity": 100,
            },
        ]
        room, _ = Room.objects.get_or_create(
            name="Room 1",
            defaults={"capacity": 100},
        )

        showtimes = [
            {
                "movie": 1,
                "room": 1,
                "start_at": datetime(2026, 1, 1, 10, 0, 0),
                "end_at": datetime(2026, 1, 1, 12, 0, 0),
                "base_price": 10.0,
            },
        ]
        start = timezone.now() + timedelta(days=1)
        Showtime.objects.get_or_create(
            room=room,
            start_at=start,
            defaults={
                "movie": movie,
                "end_at": start + timedelta(minutes=movie.duration_minutes),
                "base_price": Decimal("10.00"),
                "status": Showtime.Status.SCHEDULED,
            }
        )
        self.stdout.write("Done!")