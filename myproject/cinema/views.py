from django.shortcuts import render
from .models import Movie
# Create your views here.

def movie_list(request):
    movies = Movie.objects.filter(is_active=True).order_by("release_date")
    return render(request, "cinema/movie_list.html", {"movies": movies})