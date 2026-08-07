from django.shortcuts import render, redirect
from .models import Movie
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from .forms import CustomerRegistrationForm
# Create your views here.

def movie_list(request):
    movies = Movie.objects.filter(is_active=True).order_by("release_date")
    return render(request, "cinema/movie_list.html", {"movies": movies})
class CinemaLoginView(LoginView):
    template_name = "cinema/login.html"
    redirect_authenticated_user = True

class CinemaLogoutView(LogoutView):
    next_page = "cinema:movie_list"

def register(request):
    if request.user.is_authenticated:
        return redirect("cinema:movie_list")
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Đăng ký thành công")
            return redirect("cinema:movie_list")
    else:
        form = CustomerRegistrationForm()
    return render(request, "cinema/register.html", {"form": form})