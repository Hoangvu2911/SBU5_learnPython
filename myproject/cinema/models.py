from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q, UniqueConstraint

# Create your models here.


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()
    genre = models.CharField(max_length=255)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    duration_minutes = models.IntegerField(validators=[MinValueValidator(1)])
    director = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Actor(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class MovieActor(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="movie_actors")
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE, related_name="movie_actors")

    class Meta:
        constraints = [
            UniqueConstraint(fields=["movie", "actor"], name="uniq_movie_actor"),
        ]

    def __str__(self):
        return f"{self.movie.title} - {self.actor.name}"


class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)
    capacity = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(260)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Showtime(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        CANCELLED = "cancelled", "Cancelled"

    movie = models.ForeignKey(Movie, on_delete=models.RESTRICT, related_name="showtimes")
    room = models.ForeignKey(Room, on_delete=models.RESTRICT, related_name="showtimes")
    start_at = models.DateTimeField(db_index=True)
    end_at = models.DateTimeField()
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["room", "start_at"], name="uniq_room_start_at"),
        ]

    def __str__(self):
        return f"{self.movie.title} - {self.room.name} - {self.start_at}"


class Ticket(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        BOOKED = "booked", "Booked"
        CANCELLED = "cancelled", "Cancelled"

    showtime = models.ForeignKey(Showtime, on_delete=models.RESTRICT, related_name="tickets")
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="tickets",
    )
    seat = models.CharField(max_length=10)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["showtime", "seat"],
                condition=Q(status__in=["pending", "booked"]),
                name="unique_active_booking_per_seat",
            ),
        ]
        indexes = [
            models.Index(fields=["showtime", "status"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"{self.showtime} - {self.customer} - {self.seat}"