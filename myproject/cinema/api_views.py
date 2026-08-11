from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status as http_status

from .booking import sync_showtime_status, seat_map, book, pay, cancel_ticket, BookingError
from .models import Movie, Showtime, Ticket
from .serializers import MovieSerializer, ShowtimeSerializer, TicketSerializer, RegisterSerializer, LoginSerializer, UserSerializer
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = (
            Movie.objects.filter(is_active=True)
            .prefetch_related("movie_actors__actor")
            .order_by("release_date")
        )
        q = self.request.query_params.get("q", "").strip()
        genre = self.request.query_params.get("genre", "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(genre__icontains=q))
        if genre:
            qs = qs.filter(genre=genre)
        return qs

class ShowtimeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShowtimeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = (
            Showtime.objects.select_related("movie", "room")
            .order_by("start_at")
        )
        movie_id = self.request.query_params.get("movie", "").strip()
        status = self.request.query_params.get("status", "").strip()
        if movie_id:
            qs = qs.filter(movie_id=movie_id)

        if self.action == "list":
            if status:
                qs = qs.filter(status=status)
            elif not (self.request.user.is_authenticated and self.request.user.is_staff):
                qs = qs.filter(status=Showtime.Status.SCHEDULED)
        return qs

    def get_object(self):
        obj = super().get_object()
        sync_showtime_status(obj)
        return obj

    @action(detail=True, methods=["get"], url_path="seats")
    def seats(self, request, pk=None):
        showtime = self.get_object()
        return Response({
            "showtime": ShowtimeSerializer(showtime).data,
            "seats": seat_map(showtime),
        })

    @action(detail=True, methods=["post"], url_path="book", permission_classes=[IsAuthenticated])
    def book_seat(self, request, pk=None):
        showtime = self.get_object()
        seat = request.data.get("seat", "").strip()
        try:
            ticket = book(request.user, showtime, seat)
        except BookingError as e:
            return Response({"detail": str(e)}, status=http_status.HTTP_400_BAD_REQUEST)
        return Response(TicketSerializer(ticket).data, status=http_status.HTTP_201_CREATED)


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = (
            Ticket.objects.filter(customer=self.request.user)
            .select_related("showtime", "showtime__movie", "showtime__room")
            .order_by("-created_at")
        )
        q = self.request.query_params.get("q", "").strip()
        status = self.request.query_params.get("status", "").strip()
        if q:
            qs = qs.filter(Q(showtime__movie__title__icontains=q))
        if status:
            qs = qs.filter(status=status)
        return qs

    @action(detail=True, methods=["post"], url_path="pay")
    def pay_ticket(self, request, pk=None):
        ticket = self.get_object()
        try:
            pay(request.user, ticket)
        except BookingError as e:
            return Response({"detail": str(e)}, status=http_status.HTTP_400_BAD_REQUEST)
        ticket.refresh_from_db()
        return Response(TicketSerializer(ticket).data, status=http_status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        ticket = self.get_object()
        try:
            cancel_ticket(request.user, ticket)
        except BookingError as e:
            return Response({"detail": str(e)}, status=http_status.HTTP_400_BAD_REQUEST)
        ticket.refresh_from_db()
        return Response(TicketSerializer(ticket).data, status=http_status.HTTP_200_OK)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        login(request, user)  # session cho browser
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user": UserSerializer(user).data},
            status=201,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=ser.validated_data["username"],
            password=ser.validated_data["password"],
        )
        if user is None:
            return Response({"detail": "Invalid credentials."}, status=400)
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response({"detail": "Logged out."})