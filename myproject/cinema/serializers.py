from rest_framework import serializers
from .models import Movie, Actor, Showtime, Ticket
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated


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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "is_staff")


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords do not match")
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )
        user.is_staff = False
        user.is_superuser = False
        user.save(update_fields=["is_staff", "is_superuser"])
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)