from datetime import timedelta

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from django.utils import timezone
from .models import Movie, MovieActor, Actor, Showtime, Room, Ticket

class CustomerRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = (
            "title", "description", "release_date", "genre",
            "rating", "duration_minutes", "director", "is_active",
        )
    
    def clean_duration_minutes(self):
        duration = self.cleaned_data["duration_minutes"]
        if self.instance.pk:
            old = Movie.objects.get(pk=self.instance.pk).duration_minutes
            if duration != old:
                has_upcoming = Showtime.objects.filter(
                    movie = self.instance,
                    status = Showtime.Status.SCHEDULED,
                    start_at__gt = timezone.now(),
                ).exists()
                if has_upcoming:
                    raise forms.ValidationError("Cannot change duration of a movie that has upcoming showtimes.")
        return duration
    

class MovieActorForm(forms.ModelForm):
    class Meta:
        model = MovieActor
        fields = ("actor",)


class BaseMovieActorFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        actors = []
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get("DELETE"):
                continue
            actor = form.cleaned_data.get("actor")
            if not actor:
                continue
            if actor in actors:
                raise forms.ValidationError("Actor cannot be added multiple times.")
            actors.append(actor)


MovieActorFormSet = inlineformset_factory(
    Movie,
    MovieActor,
    form=MovieActorForm,
    formset=BaseMovieActorFormSet,
    fields=("actor",),
    extra=1,
    can_delete=True,
)


class ActorForm(forms.ModelForm):
    class Meta:
        model = Actor
        fields = ("name", "bio")


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ("name", "capacity")

    def clean_capacity(self):
        capacity = self.cleaned_data["capacity"]
        if capacity < 1 or capacity > 260:
            raise forms.ValidationError("Capacity must be between 1 and 260.")
        return capacity

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        qs = Room.objects.filter(name=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Room with this name already exists.")
        return name


class ShowtimeForm(forms.ModelForm):
    start_at = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )

    class Meta:
        model = Showtime
        fields = ("movie", "room", "start_at", "base_price")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.start_at:
            local = timezone.localtime(self.instance.start_at)
            self.initial["start_at"] = local.strftime("%Y-%m-%dT%H:%M")
    
    def _has_active_ticket(self):
        if not self.instance.pk:
            return False
        return self.instance.tickets.filter(
            status__in=[Ticket.Status.PENDING, Ticket.Status.BOOKED],
        ).exists()
    
    def clean(self):
        cleaned = super().clean()
        movie = cleaned.get("movie")
        room = cleaned.get("room")
        start_at = cleaned.get("start_at")
        base_price = cleaned.get("base_price")
        if not all([movie, room, start_at, base_price is not None]):
            return cleaned
        
        if timezone.is_naive(start_at):
            start_at = timezone.make_aware(start_at, timezone.get_current_timezone())
            cleaned["start_at"] = start_at
        
        end_at = start_at + timedelta(minutes=movie.duration_minutes)
        cleaned["end_at"] = end_at

        if self._has_active_ticket():
            old = Showtime.objects.get(pk=self.instance.pk)
            locked = (
                old.movie_id != movie.pk
                or old.room_id != room.pk
                or old.start_at != start_at
                or old.base_price != base_price
            )
            if locked:
                raise forms.ValidationError("Suất đã có vé pending/booked: không đổi phim, phòng, giờ, giá.")

        qs = Showtime.objects.filter(
            room=room,
            status__in=[Showtime.Status.SCHEDULED, Showtime.Status.ONGOING],
            start_at__lt=end_at,
            end_at__gt=start_at,
        )
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Trùng lịch phòng với suất scheduled khác")
        return cleaned
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.end_at = self.cleaned_data["end_at"]
        if not instance.pk:
            instance.status = Showtime.Status.SCHEDULED
        if commit:
            instance.save()
        return instance


class TicketStatusForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ("status",)


class SeatBookForm(forms.Form):
    seat = forms.CharField(max_length=10)