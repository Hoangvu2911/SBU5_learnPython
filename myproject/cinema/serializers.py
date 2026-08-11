from rest_framework import serializers
from .models import Movie, Actor, Showtime, Ticket, Room, MovieActor
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from .forms import ShowtimeForm, TicketStatusForm

class MovieSerializer(serializers.ModelSerializer):
    cast = serializers.SerializerMethodField()
    actor_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Movie
        fields = (
            "id", "title", "description", "release_date", "genre", "rating", 
            "duration_minutes", "director", "is_active", "cast", "actor_ids",
        )
        read_only_fields = ("id",)

    def get_cast(self, obj):
        return [
            {"id": ma.actor_id, "name": ma.actor.name}
            for ma in obj.movie_actors.all()
        ]

    def validate_actor_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Actor IDs must be unique.")
        found = set(Actor.objects.filter(id__in=value).values_list("id", flat=True))
        missing = set(value) - found
        if missing:
            raise serializers.ValidationError(f"Actor IDs {missing} not found.")
        return value

    def validate_duration_minutes(self, value):
        if self.instance and self.instance.pk:
            if value != self.instance.duration_minutes:
                has_upcoming = Showtime.objects.filter(
                    movie=self.instance,
                    status=Showtime.Status.SCHEDULED,
                    start_at__gt=timezone.now(),
                ).exists()
                if has_upcoming:
                    raise serializers.ValidationError("Cannot change duration for a movie with upcoming showtimes.")
        return value

    def _set_cast(self, movie, actor_ids):
        if actor_ids is None:
            return
        movie.movie_actors.all().delete()
        MovieActor.objects.bulk_create([
            MovieActor(movie=movie, actor_id=actor_id) for actor_id in actor_ids
        ])

    def create(self, validated_data):
        actor_ids = validated_data.pop("actor_ids", [])
        movie = Movie.objects.create(**validated_data)
        self._set_cast(movie, actor_ids)
        return movie

    def update(self, instance, validated_data):
        actor_ids = validated_data.pop("actor_ids", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self._set_cast(instance, actor_ids)
        return instance

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
        read_only_fields = ("id", "end_at", "status", "movie_title", "room_name", "is_bookable")

    def _save_via_form(self, instance=None):
        form = ShowtimeForm(data=self.initial_data, instance=instance)
        if not form.is_valid():
            raise serializers.ValidationError(form.errors)
        return form.save()
    
    def create(self, validated_data):
        return self._save_via_form()
    
    def update(self, instance, validated_data):
        return self._save_via_form(instance=instance)


class TicketSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source="showtime.movie.title", read_only=True)
    room_name = serializers.CharField(source="showtime.room.name", read_only=True)
    start_at = serializers.DateTimeField(source="showtime.start_at", read_only=True)
    customer = serializers.CharField(source="customer.username", read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id", "showtime", "movie_title", "room_name", "start_at",
            "seat", "price", "status", "created_at", "customer",
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


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ("id", "name", "bio")
        read_only_fields = ("id",)

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("id", "name", "capacity")
        read_only_fields = ("id",)

    def validate_name(self, name):
        name = name.strip()
        qs = Room.objects.filter(name=name)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Room with this name already exists.")
        return name

    def validate_capacity(self, value):
        if value < 1 or value > 260:
            raise serializers.ValidationError("Capacity must be between 1 and 260.")
        return value
