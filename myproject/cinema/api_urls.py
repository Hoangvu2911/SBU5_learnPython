from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from .api_views import MovieViewSet, ShowtimeViewSet, TicketViewSet, RegisterView, LoginView, LogoutView

router = DefaultRouter()
router.register(r"movies", MovieViewSet, basename="movie")
router.register(r"showtimes", ShowtimeViewSet, basename="showtime")
router.register(r"tickets", TicketViewSet, basename="ticket")

urlpatterns = [
    path("token/", obtain_auth_token, name="api_token_auth"),
    path("", include(router.urls)),
    path("auth/register/", RegisterView.as_view(), name="api_register"),
    path("auth/login/", LoginView.as_view(), name="api_login"),
    path("auth/logout/", LogoutView.as_view(), name="api_logout"),
]