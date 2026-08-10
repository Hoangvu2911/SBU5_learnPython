from rest_framework import serializers
from .models import Movie, Actor, Showtime, Ticket


class MovieSerializer(serializers.ModelSerializer):
    cast = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = (
            "id", "title", "description", "release_date", "genre", "rating", 
            "duration_minutes", "director", "is_active", "cast"
        )
        read_only_fields = ("id",)

    def get_cast(self, obj):
        return [
            {"id": ma.actor_id, "name": ma.actor.name}
            for ma in obj.movie_actors.all()
        ]


class ShowtimeSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source="room.name", read_only=True)
    movie_title = serializers.CharField(source="movie.title", read_only=True)
    is_bookable = serializers.BooleanField(read_only=True)

    class Meta:
        model = Showtime
        fields = (
            "id", "movie", "movie_title", "room", "room_name", "start_at",
            "end_at", "base_price", "status", "is_bookable"
        )
        read_only_fields = ("id",)


class TicketSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source="showtime.movie.title", read_only=True)
    room_name = serializers.CharField(source="showtime.room.name", read_only=True)
    start_at = serializers.DateTimeField(source="showtime.start_at", read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id", "showtime", "movie_title", "room_name", "start_at",
            "seat", "price", "status", "created_at",
        )
        read_only_fields = fields