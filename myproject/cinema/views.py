from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Showtime, Ticket
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from .forms import CustomerRegistrationForm, SeatBookForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .booking import book, BookingError, seat_map, cleanup_pending, pay, cancel_ticket, sync_showtime_status
from django.core.paginator import Paginator
from django.db.models import Q
# Create your views here.


def movie_list(request):
    q = request.GET.get("q", "").strip()
    genre = request.GET.get("genre", "").strip()

    movies = Movie.objects.filter(is_active=True).order_by("release_date")
    if q:
        movies = movies.filter(
            Q(title__icontains=q) | Q(director__icontains=q) | Q(genre__icontains=q)
        )
    if genre:
        movies = movies.filter(genre=genre)

    genres = (
        Movie.objects.filter(is_active=True)
        .values_list("genre", flat=True)
        .distinct()
        .order_by("genre")
    )

    return render(request, "cinema/movie_list.html", {"genres": genres})


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


def movie_detail(request, pk):
    return render(request, "cinema/movie_detail.html", {"movie_id": pk})


@login_required
def showtime_seats(request, pk):
    return render(request, "cinema/seats.html", {"showtime_id": pk})


@login_required
def my_tickets(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    return render(request, "cinema/my_tickets.html", {
        "q": q,
        "status": status,
        "status_choices": Ticket.Status.choices,
    })



@login_required
def ticket_pay(request, pk):
    ticket = get_object_or_404(
        Ticket.objects.select_related("showtime", "showtime__movie", "showtime__room"),
        pk=pk,
        customer=request.user,
    )
    cleanup_pending(ticket.showtime)
    ticket.refresh_from_db()
    
    if request.method == "POST":
        try:
            pay(request.user, ticket)
            messages.success(request, f"Đã thanh toán ghế {ticket.seat}.")
            return redirect("cinema:my_tickets")
        except BookingError as e:
            messages.error(request, str(e))
            return redirect("cinema:my_tickets")
    return render(request, "cinema/ticket_pay.html", {"ticket": ticket})


@login_required
def ticket_cancel(request, pk):
    ticket = get_object_or_404(
        Ticket.objects.select_related("showtime"),
        pk=pk,
        customer=request.user,
    )
    if request.method == "POST":
        try:
            cancel_ticket(request.user, ticket)
            messages.success(request, f"Đã hủy ghế {ticket.seat}.")
        except BookingError as e:
            messages.error(request, str(e))
    return redirect("cinema:my_tickets")