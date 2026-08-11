from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Movie, Actor, Room, Showtime, Ticket
from .forms import MovieForm, MovieActorFormSet, ActorForm, RoomForm, ShowtimeForm, TicketStatusForm
from .booking import cancel_showtime, sync_showtime_status
from django.core.paginator import Paginator


def staff_required(view):
    return login_required(user_passes_test(lambda u: u.is_staff)(view))


@staff_required
def manage_home(request):
    return render(request, 'cinema/manage/home.html')


@staff_required
def movie_list(request):
    movies = Movie.objects.order_by("-created_at")
    return render(request, "cinema/manage/movie_list.html", {"movies": movies})


@staff_required
def movie_create(request):
    if request.method == "POST":
        movie = Movie()
        form = MovieForm(request.POST, instance=movie)
        formset = MovieActorFormSet(request.POST, instance=movie)
        if form.is_valid() and formset.is_valid():
            movie = form.save()
            formset.instance = movie
            formset.save()
            messages.success(request, "Đã tạo phim.")
            return redirect("cinema:manage_movie_list")
    else:
        form = MovieForm() 
        formset = MovieActorFormSet()
    return render(request, "cinema/manage/movie_form.html", {
        "form": form,
        "formset": formset,
        "title": "Thêm phim",
        "api_url": "/api/movies/",
        "api_method": "POST",
        "cancel_url": "cinema:manage_movie_list",
    })


@staff_required
def movie_edit(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == "POST":
        form = MovieForm(request.POST, instance=movie)
        formset = MovieActorFormSet(request.POST, instance=movie)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Đã cập nhật phim.")
            return redirect("cinema:manage_movie_list")
    else:
        form = MovieForm(instance=movie)
        formset = MovieActorFormSet(instance=movie)
    return render(request, "cinema/manage/movie_form.html", {
        "form": form,
        "formset": formset,
        "title": f"Sửa: {movie.title}",
        "api_url": f"/api/movies/{movie.pk}/",
        "api_method": "PATCH",
        "cancel_url": "cinema:manage_movie_list",
    })


@staff_required
def movie_toggle_active(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == "POST":
        movie.is_active = not movie.is_active
        movie.save(update_fields=["is_active", "updated_at"])
        messages.success(request, f"{movie.title}: is_active={movie.is_active}")
    return redirect("cinema:manage_movie_list")


@staff_required
def actor_list(request):
    actors = Actor.objects.order_by("name")
    return render(request, "cinema/manage/actor_list.html", {"actors": actors})


@staff_required
def actor_create(request):
    if request.method == "POST":
        form = ActorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã tạo diễn viên.")
            return redirect("cinema:manage_actor_list")
    else:
        form = ActorForm()
    return render(request, "cinema/manage/form_simple.html", {
        "form": form,
        "title": "Thêm diễn viên",
        "cancel_url": "cinema:manage_actor_list",
        "api_url": "/api/actors/",
        "api_method": "POST",
    })


@staff_required
def actor_edit(request, pk):
    actor = get_object_or_404(Actor, pk=pk)
    if request.method == "POST":
        form = ActorForm(request.POST, instance=actor)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã cập nhật diễn viên.")
            return redirect("cinema:manage_actor_list")
    else:
        form = ActorForm(instance=actor)
    return render(request, "cinema/manage/form_simple.html", {
        "form": form,
        "title": f"Sửa: {actor.name}",
        "cancel_url": "cinema:manage_actor_list",
        "api_url": f"/api/actors/{actor.pk}/",
        "api_method": "PATCH",
    })
    

@staff_required
def room_list(request):
    rooms = Room.objects.order_by("name")
    return render(request, "cinema/manage/room_list.html", {"rooms": rooms})


@staff_required
def room_create(request):
    if request.method == "POST":
        room = Room()
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            room = form.save()
            messages.success(request, "Đã tạo phòng.")
            return redirect("cinema:manage_room_list")
    else:
        form = RoomForm()
    return render(request, "cinema/manage/form_simple.html", {
        "form": form,
        "title": "Thêm phòng",
        "cancel_url": "cinema:manage_room_list",
        "api_url": "/api/rooms/",
        "api_method": "POST",
    })


@staff_required
def room_edit(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã cập nhật phòng.")
            return redirect("cinema:manage_room_list")
    else:
        form = RoomForm(instance=room)
    return render(request, "cinema/manage/form_simple.html", {
        "form": form,
        "title": f"Sửa: {room.name}",
        "cancel_url": "cinema:manage_room_list",
        "api_url": f"/api/rooms/{room.pk}/",
        "api_method": "PATCH",
    })
    
    
@staff_required
def showtime_list(request):
    showtimes = Showtime.objects.select_related("movie", "room").order_by("-start_at")
    for st in showtimes:
        sync_showtime_status(st)

    movie_id = (request.GET.get("movie") or "").strip()
    status = (request.GET.get("status") or "").strip()
    if status:
        showtimes = showtimes.filter(status=status)
    if movie_id:
        showtimes = showtimes.filter(movie_id=movie_id)

    paginator = Paginator(showtimes, 9)
    page_obj = paginator.get_page(request.GET.get("page"))
    query = request.GET.copy()
    query.pop("page", None)

    return render(request, "cinema/manage/showtime_list.html", {
        "showtimes": page_obj.object_list,
        "page_obj": page_obj,
        "query": query.urlencode(),
        "movies": Movie.objects.order_by("title"),
        "status_choices": Showtime.Status.choices,
        "movie_id": movie_id,
        "status": status,
    })


@staff_required
def showtime_create(request):
    if request.method == "POST":
        form = ShowtimeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã tạo suất.")
            return redirect("cinema:manage_showtime_list")
    else:
        form = ShowtimeForm()
    return render(request, "cinema/manage/form_simple.html", {
        "form": form,
        "title": "Thêm suất",
        "cancel_url": "cinema:manage_showtime_list",
        "api_url": "/api/showtimes/",
        "api_method": "POST",
    })
    

@staff_required
def showtime_edit(request, pk):
    showtime = get_object_or_404(Showtime, pk=pk)
    sync_showtime_status(showtime)
    if request.method == "POST":
        form = ShowtimeForm(request.POST, instance=showtime)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã cập nhật suất.")
            return redirect("cinema:manage_showtime_list")
    else:
        form = ShowtimeForm(instance=showtime)
    return render(request, "cinema/manage/form_simple.html", {
        "form": form,
        "title": f"Sửa suất: {showtime}",
        "cancel_url": "cinema:manage_showtime_list",
        "api_url": f"/api/showtimes/{showtime.pk}/",
        "api_method": "PATCH",
    })


@staff_required
def showtime_cancel(request, pk):
    showtime = get_object_or_404(Showtime, pk=pk)
    sync_showtime_status(showtime)
    if request.method == "POST":
        if showtime.status == Showtime.Status.CANCELLED:
            messages.info(request, "Suất đã hủy trước đó.")
        elif showtime.status == Showtime.Status.COMPLETED:
            messages.info(request, "Suất đã hoàn thành.")
        else:
            n = cancel_showtime(showtime)
            if showtime.status == Showtime.Status.CANCELLED:
                messages.success(request, f"Đã hủy suất. {n} vé active → cancelled.")
            else:
                messages.warning(request, f"Không thể hủy suất. {n} vé active → cancelled.")
    return redirect("cinema:manage_showtime_list")


@staff_required
def ticket_list(request):
    tickets = (
        Ticket.objects.select_related("showtime", "showtime__movie", "showtime__room", "customer")
        .order_by("-created_at")
    )
    showtime_id = request.GET.get("showtime")
    status = request.GET.get("status")
    if showtime_id:
        tickets = tickets.filter(showtime_id=showtime_id)
    if status:
        tickets = tickets.filter(status=status)

    paginator = Paginator(tickets, 9)
    page_obj = paginator.get_page(request.GET.get("page"))
    query = request.GET.copy()
    query.pop("page", None)

    return render(request, "cinema/manage/ticket_list.html", {
        "tickets": tickets,
        "page_obj": page_obj,
        "query": query.urlencode(),
        "showtimes": Showtime.objects.select_related("movie", "room").order_by("-start_at"),
        "status_choices": Ticket.Status.choices,
        "showtime_id": showtime_id or "",
        "status": status or "",
    })


@staff_required
def ticket_edit_status(request, pk):
    ticket = get_object_or_404(
        Ticket.objects.select_related("showtime", "customer"),
        pk=pk,
    )
    if request.method == "POST":
        form = TicketStatusForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, f"Vé #{ticket.pk}: status → {ticket.status}")
            return redirect("cinema:manage_ticket_list")
    else:
        form = TicketStatusForm(instance=ticket)
    return render(request, "cinema/manage/ticket_status_form.html", {
        "form": form,
        "ticket": ticket,
    })
