from django.contrib import admin

# Register your models here.
from .models import Movie, Actor, MovieActor, Room, Showtime, Ticket

admin.site.register(Movie)
admin.site.register(Actor)
admin.site.register(MovieActor)
admin.site.register(Room)
admin.site.register(Showtime)
admin.site.register(Ticket)
