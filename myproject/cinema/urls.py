from django.urls import path
from . import views, view_admin

app_name = "cinema"

urlpatterns = [
    path("", views.movie_list, name="movie_list"),
    path("accounts/login/", views.CinemaLoginView.as_view(), name="login"),
    path("accounts/logout/", views.CinemaLogoutView.as_view(), name="logout"),
    path("accounts/register/", views.register, name="register"),

    path("manage/", view_admin.manage_home, name="manage_home"),

    path("manage/movies/", view_admin.movie_list, name="manage_movie_list"),
    path("manage/movies/new/", view_admin.movie_create, name="manage_movie_create"),
    path("manage/movies/<int:pk>/edit/", view_admin.movie_edit, name="manage_movie_edit"),
    path("manage/movies/<int:pk>/toggle/", view_admin.movie_toggle_active, name="manage_movie_toggle"),

    path("manage/actors/", view_admin.actor_list, name="manage_actor_list"),
    path("manage/actors/new/", view_admin.actor_create, name="manage_actor_create"),
    path("manage/actors/<int:pk>/edit/", view_admin.actor_edit, name="manage_actor_edit"),

    path("manage/rooms/", view_admin.room_list, name="manage_room_list"),
    path("manage/rooms/new/", view_admin.room_create, name="manage_room_create"),
    path("manage/rooms/<int:pk>/edit/", view_admin.room_edit, name="manage_room_edit"),

    path("manage/showtimes/", view_admin.showtime_list, name="manage_showtime_list"),
    path("manage/showtimes/new/", view_admin.showtime_create, name="manage_showtime_create"),
    path("manage/showtimes/<int:pk>/edit/", view_admin.showtime_edit, name="manage_showtime_edit"),
    path("manage/showtimes/<int:pk>/cancel/", view_admin.showtime_cancel, name="manage_showtime_cancel"),

    path("manage/tickets/", view_admin.ticket_list, name="manage_ticket_list"),
    path("manage/tickets/<int:pk>/edit/", view_admin.ticket_edit_status, name="manage_ticket_edit_status"),

    path("movies/<int:pk>/", views.movie_detail, name="movie_detail"),
    path("showtimes/<int:pk>/seats/", views.showtime_seats, name="showtime_seats"),

    path("tickets/mine/", views.my_tickets, name="my_tickets"),
    path("tickets/<int:pk>/pay/", views.ticket_pay, name="ticket_pay"),
    path("tickets/<int:pk>/cancel/", views.ticket_cancel, name="ticket_cancel"),
]