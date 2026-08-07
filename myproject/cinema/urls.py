from django.urls import path
from . import views

app_name = "cinema"

urlpatterns = [
    path("", views.movie_list, name="movie_list"),
    path("accounts/login/", views.CinemaLoginView.as_view(), name="login"),
    path("accounts/logout/", views.CinemaLogoutView.as_view(), name="logout"),
    path("accounts/register/", views.register, name="register"),
]