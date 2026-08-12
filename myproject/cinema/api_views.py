from django.db.models import Q
from .permissions import IsStaffOrReadOnly
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status as http_status

from .booking import (
    sync_showtime_status, sync_showtimes_bulk, seat_map, book, pay,
    cancel_ticket, BookingError, cancel_showtime, cleanup_all_expired_pending, cleanup_pending,
)
from .models import Movie, Room, Showtime, Ticket, Actor
from .serializers import ( MovieSerializer, ShowtimeSerializer, TicketSerializer, RegisterSerializer, 
LoginSerializer, UserSerializer, ActorSerializer, RoomSerializer)
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from .forms import TicketStatusForm

class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = MovieSerializer
    permission_classes = [IsStaffOrReadOnly]
    http_method_names = ["get", "head", "options", "post", "patch"]

    def get_queryset(self):
        is_staff = self.request.user.is_authenticated and self.request.user.is_staff
        if self.action == "list" and is_staff:
            order_by = "-created_at"
        else:
            order_by = "release_date"

        qs = (
            Movie.objects.prefetch_related("movie_actors__actor")
            .order_by(order_by)
        )
        if not is_staff:
            qs = qs.filter(is_active=True)

        q = self.request.query_params.get("q", "").strip()
        genre = self.request.query_params.get("genre", "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(genre__icontains=q))
        if genre:
            qs = qs.filter(genre=genre)
        return qs

    @action(detail=True, methods=["post"], url_path="toggle", permission_classes=[IsAdminUser])
    def toggle(self, request, pk=None):
        movie = self.get_object()
        movie.is_active = not movie.is_active
        movie.save(update_fields=["is_active", "updated_at"])
        return Response(MovieSerializer(movie).data)

class ShowtimeViewSet(viewsets.ModelViewSet):
    serializer_class = ShowtimeSerializer
    permission_classes = [IsStaffOrReadOnly]
    http_method_names = ["get", "head", "options", "post", "patch"]

    def get_queryset(self):
        is_staff = self.request.user.is_authenticated and self.request.user.is_staff
        order_by = "-start_at" if (self.action == "list" and is_staff) else "start_at"

        qs = (
            Showtime.objects.select_related("movie", "room")
            .order_by(order_by)
        )

        movie_id = self.request.query_params.get("movie", "").strip()
        status = self.request.query_params.get("status", "").strip()
        if movie_id:
            qs = qs.filter(movie_id=movie_id)

        if self.action == "list":
            sync_showtimes_bulk(qs)
            if status:
                qs = qs.filter(status=status)
            elif not is_staff:
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

    @action(detail=True, methods=["post"], url_path="cancel", permission_classes=[IsAdminUser])
    def cancel_showtime(self, request, pk=None):
        showtime = self.get_object()
        if showtime.status in (Showtime.Status.ONGOING, Showtime.Status.CANCELLED, Showtime.Status.COMPLETED):
            return Response(
                {"detail": f"Không thể hủy suất đã {showtime.status}."},
                status=http_status.HTTP_400_BAD_REQUEST,
            )
        n = cancel_showtime(showtime)
        showtime.refresh_from_db()
        return Response({
            "showtime": ShowtimeSerializer(showtime).data,
            "tickets_cancelled": n,
        })

class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options", "post"]
    
    def get_queryset(self):
        qs = (
            Ticket.objects.select_related("showtime", "showtime__movie", "showtime__room", "customer")
            .order_by("-created_at")
        )
        user = self.request.user
        is_staff = user.is_staff
        mine = self.request.query_params.get("mine", "").strip().lower() in {"1", "true", "yes"}
        if (not is_staff) or mine:
            qs = qs.filter(customer=user)

        q = self.request.query_params.get("q", "").strip()
        status = self.request.query_params.get("status", "").strip()
        showtime_id = self.request.query_params.get("showtime", "").strip()
        if q:
            qs = qs.filter(Q(showtime__movie__title__icontains=q))
        if status:
            qs = qs.filter(status=status)
        if showtime_id:
            qs = qs.filter(showtime_id=showtime_id)
        return qs

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": 'Method "POST" không được phép.'},
            status=http_status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"detail": "Chỉ quản trị viên mới có quyền thay đổi trạng thái vé."},
                status=http_status.HTTP_403_FORBIDDEN,
            )
        ticket = self.get_object()
        form = TicketStatusForm(data=request.data, instance=ticket)
        if not form.is_valid():
            return Response(form.errors, status=http_status.HTTP_400_BAD_REQUEST)
        ticket = form.save()
        return Response(TicketSerializer(ticket).data)
    
    def list(self, request, *args, **kwargs):
        cleanup_all_expired_pending()
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        ticket = self.get_object()
        cleanup_pending(ticket.showtime)
        ticket.refresh_from_db()
        return Response(TicketSerializer(ticket).data)

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
            return Response({"detail": "Invalid credentials"}, status=401)
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response({"detail": "Logged out."})


class ActorViewSet(viewsets.ModelViewSet):
    serializer_class = ActorSerializer
    permission_classes = [IsAdminUser]
    queryset = Actor.objects.order_by("name")
    http_method_names = ["get", "post", "head", "options", "patch"]


class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [IsAdminUser]
    queryset = Room.objects.order_by("name")
    http_method_names = ["get", "post", "head", "options", "patch"]