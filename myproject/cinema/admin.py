from django.contrib import admin, messages
from django.db.models import RestrictedError

from .models import Movie, Actor, MovieActor, Room, Showtime, Ticket
from .forms import MovieForm, ActorForm, RoomForm, ShowtimeForm, TicketStatusForm
from .booking import cancel_showtime, sync_showtime_status

# Register your models here.

class MovieActorInline(admin.TabularInline):
    model = MovieActor
    extra = 1


class RestrictDeleteMixin:
    def delete_model(self, request, obj):
        try:
            super().delete_model(request, obj)
        except RestrictedError:
            self.message_user(
                request,
                f"Không thể xóa '{obj}' vì còn dữ liệu liên quan khác",
                level=messages.ERROR,
            )

    def delete_queryset(self, request, queryset):
        deleted, blocked = 0, 0
        for obj in queryset:
            try:
                obj.delete()
                deleted += 1
            except RestrictedError:
                blocked += 1
        if deleted:
            self.message_user(
                request,
                f"Đã xóa {deleted} mục",
            )
        if blocked:
            self.message_user(
                request,
                f"Khóa {blocked} mục không thể xóa",
                level=messages.ERROR,
            )


@admin.register(Movie)
class MovieAdmin(RestrictDeleteMixin, admin.ModelAdmin):
    form = MovieForm
    list_display = ("title", "genre", "rating", "duration_minutes", "director", "is_active")
    list_filter = ("genre", "is_active")
    search_fields = ("title", "director", "genre")
    inlines = [MovieActorInline]


@admin.register(Actor)
class ActorAdmin(RestrictDeleteMixin, admin.ModelAdmin):
    form = ActorForm
    list_display = ("name",)
    search_fields = ("name", "bio")


@admin.register(Room)
class RoomAdmin(RestrictDeleteMixin, admin.ModelAdmin):
    form = RoomForm
    list_display = ("name", "capacity")
    search_fields = ("name",)


@admin.register(MovieActor)
class MovieActorAdmin(RestrictDeleteMixin, admin.ModelAdmin):
    def has_module_permission(self, request):
        return False  


@admin.register(Showtime)
class ShowtimeAdmin(RestrictDeleteMixin, admin.ModelAdmin):
    form = ShowtimeForm
    list_display = ("movie", "room", "start_at", "status", "base_price")
    list_filter = ("status", "room")
    search_fields = ("movie__title", "room__name")
    readonly_fields = ("status",)
    actions = ["cancel_selected"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        for s in qs:
            sync_showtime_status(s)
        return qs

    @admin.action(description="Hủy phiên chiếu vé đã đặt")
    def cancel_selected(self, request, queryset):
        n_show, n_tickets = 0, 0
        for s in queryset:
            sync_showtime_status(s)
            if s.status in (Showtime.Status.SCHEDULED, Showtime.Status.ONGOING):
                n_tickets += cancel_showtime(s)
                n_show += 1
        self.message_user(
            request,
            f"Đã hủy {n_show} phiên chiếu và {n_tickets} vé",
            level=messages.SUCCESS,
        )

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    form = TicketStatusForm
    list_display = ("id", "showtime", "customer", "seat", "price", "status")
    list_filter = ("status",)
    search_fields = ("seat", "customer__username", "showtime__movie__title")
    readonly_fields = ("showtime", "customer", "seat", "price")

    def has_delete_permission(self, request, obj=None):
        return False
