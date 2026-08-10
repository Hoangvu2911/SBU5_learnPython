from datetime import datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from cinema.models import Actor, Movie, MovieActor, Room, Showtime, Ticket
from cinema.seats import generate_seats

User = get_user_model()

# Mặc định đủ để test phân trang (10/trang) + lọc thể loại.
MOVIES = [
    {
        "title": "The Dark Knight",
        "description": "Batman đối đầu Joker ở Gotham.",
        "release_date": datetime(2008, 7, 18).date(),
        "genre": "Action",
        "rating": "9.0",
        "duration_minutes": 152,
        "director": "Christopher Nolan",
        "actors": ["Christian Bale", "Heath Ledger", "Aaron Eckhart"],
    },
    {
        "title": "The Dark Knight Rises",
        "description": "Batman trở lại khi Gotham bị Bane đe dọa.",
        "release_date": datetime(2012, 7, 20).date(),
        "genre": "Action",
        "rating": "8.4",
        "duration_minutes": 165,
        "director": "Christopher Nolan",
        "actors": ["Christian Bale", "Tom Hardy", "Anne Hathaway"],
    },
    {
        "title": "Inception",
        "description": "Đội xâm nhập giấc mơ để cấy ý tưởng.",
        "release_date": datetime(2010, 7, 16).date(),
        "genre": "Sci-Fi",
        "rating": "8.8",
        "duration_minutes": 148,
        "director": "Christopher Nolan",
        "actors": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Tom Hardy"],
    },
    {
        "title": "Interstellar",
        "description": "Hành trình xuyên không gian tìm hành tinh mới cho nhân loại.",
        "release_date": datetime(2014, 11, 7).date(),
        "genre": "Sci-Fi",
        "rating": "8.7",
        "duration_minutes": 169,
        "director": "Christopher Nolan",
        "actors": ["Matthew McConaughey", "Anne Hathaway"],
    },
    {
        "title": "Parasite",
        "description": "Hai gia đình Hàn Quốc giao thoa qua một ngôi nhà sang trọng.",
        "release_date": datetime(2019, 5, 30).date(),
        "genre": "Thriller",
        "rating": "8.5",
        "duration_minutes": 132,
        "director": "Bong Joon-ho",
        "actors": ["Song Kang-ho", "Cho Yeo-jeong"],
    },
    {
        "title": "Spirited Away",
        "description": "Chihiro lạc vào thế giới thần linh và phải tìm cách về nhà.",
        "release_date": datetime(2001, 7, 20).date(),
        "genre": "Animation",
        "rating": "8.6",
        "duration_minutes": 125,
        "director": "Hayao Miyazaki",
        "actors": ["Rumi Hiiragi", "Miyu Irino"],
    },
    {
        "title": "The Godfather",
        "description": "Câu chuyện gia tộc mafia Corleone.",
        "release_date": datetime(1972, 3, 24).date(),
        "genre": "Drama",
        "rating": "9.2",
        "duration_minutes": 175,
        "director": "Francis Ford Coppola",
        "actors": ["Marlon Brando", "Al Pacino"],
    },
    {
        "title": "La La Land",
        "description": "Nhạc sĩ và diễn viên theo đuổi giấc mơ ở Los Angeles.",
        "release_date": datetime(2016, 12, 9).date(),
        "genre": "Musical",
        "rating": "8.0",
        "duration_minutes": 128,
        "director": "Damien Chazelle",
        "actors": ["Ryan Gosling", "Emma Stone"],
    },
    {
        "title": "Dune",
        "description": "Paul Atreides đến Arrakis — hành tinh sa mạc đầy gia vị.",
        "release_date": datetime(2021, 10, 22).date(),
        "genre": "Sci-Fi",
        "rating": "8.0",
        "duration_minutes": 155,
        "director": "Denis Villeneuve",
        "actors": ["Timothée Chalamet", "Zendaya", "Rebecca Ferguson"],
    },
    {
        "title": "Everything Everywhere All at Once",
        "description": "Một bà mẹ bị cuốn vào đa vũ trụ để cứu gia đình.",
        "release_date": datetime(2022, 3, 25).date(),
        "genre": "Comedy",
        "rating": "7.8",
        "duration_minutes": 139,
        "director": "Daniels",
        "actors": ["Michelle Yeoh", "Ke Huy Quan"],
    },
    {
        "title": "The Shawshank Redemption",
        "description": "Tình bạn và hy vọng trong nhà tù Shawshank.",
        "release_date": datetime(1994, 9, 23).date(),
        "genre": "Drama",
        "rating": "9.3",
        "duration_minutes": 142,
        "director": "Frank Darabont",
        "actors": ["Tim Robbins", "Morgan Freeman"],
    },
    {
        "title": "Spider-Man: Across the Spider-Verse",
        "description": "Miles Morales gặp các Spider-People từ đa vũ trụ.",
        "release_date": datetime(2023, 6, 2).date(),
        "genre": "Animation",
        "rating": "8.6",
        "duration_minutes": 140,
        "director": "Joaquim Dos Santos",
        "actors": ["Shameik Moore", "Hailee Steinfeld"],
    },
    {
        "title": "Oppenheimer",
        "description": "Câu chuyện về cha đẻ bom nguyên tử.",
        "release_date": datetime(2023, 7, 21).date(),
        "genre": "Biography",
        "rating": "8.3",
        "duration_minutes": 180,
        "director": "Christopher Nolan",
        "actors": ["Cillian Murphy", "Emily Blunt", "Robert Downey Jr."],
    },
    {
        "title": "Coco",
        "description": "Miguel bước vào Land of the Dead trong Día de los Muertos.",
        "release_date": datetime(2017, 11, 22).date(),
        "genre": "Animation",
        "rating": "8.4",
        "duration_minutes": 105,
        "director": "Lee Unkrich",
        "actors": ["Anthony Gonzalez", "Gael García Bernal"],
    },
    {
        "title": "Mad Max: Fury Road",
        "description": "Cuộc rượt đuổi trên sa mạc hậu tận thế.",
        "release_date": datetime(2015, 5, 15).date(),
        "genre": "Action",
        "rating": "8.1",
        "duration_minutes": 120,
        "director": "George Miller",
        "actors": ["Tom Hardy", "Charlize Theron"],
    },
    {
        "title": "Get Out",
        "description": "Chàng trai thăm nhà bạn gái và phát hiện bí mật đáng sợ.",
        "release_date": datetime(2017, 2, 24).date(),
        "genre": "Horror",
        "rating": "7.7",
        "duration_minutes": 104,
        "director": "Jordan Peele",
        "actors": ["Daniel Kaluuya", "Allison Williams"],
    },
    {
        "title": "Mắt Biếc",
        "description": "Chuyện tình Ngạn và Hà Lan ở miền Trung Việt Nam.",
        "release_date": datetime(2019, 12, 20).date(),
        "genre": "Romance",
        "rating": "7.5",
        "duration_minutes": 117,
        "director": "Victor Vũ",
        "actors": ["Trần Nghĩa", "Trúc Anh"],
    },
    {
        "title": "Hai Phượng",
        "description": "Bà mẹ đơn thân truy tìm kẻ bắt cóc con gái.",
        "release_date": datetime(2019, 2, 22).date(),
        "genre": "Action",
        "rating": "6.7",
        "duration_minutes": 98,
        "director": "Lê Văn Kiệt",
        "actors": ["Ngô Thanh Vân", "Phan Thanh Nhiên"],
    },
    {
        "title": "Bố Già",
        "description": "Gia đình Sài Gòn và khoảng cách thế hệ.",
        "release_date": datetime(2021, 3, 5).date(),
        "genre": "Comedy",
        "rating": "7.2",
        "duration_minutes": 128,
        "director": "Vũ Ngọc Đãng",
        "actors": ["Trấn Thành", "Ngọc Giàu"],
    },
    {
        "title": "Avatar: The Way of Water",
        "description": "Gia đình Sully tìm nơi dung thân dưới đại dương Pandora.",
        "release_date": datetime(2022, 12, 16).date(),
        "genre": "Sci-Fi",
        "rating": "7.6",
        "duration_minutes": 192,
        "director": "James Cameron",
        "actors": ["Sam Worthington", "Zoe Saldana"],
    },
]

ROOMS = [
    {"name": "Room 1", "capacity": 80},
    {"name": "Room 2", "capacity": 120},
    {"name": "IMAX", "capacity": 160},
    {"name": "VIP", "capacity": 40},
]

# Giờ chiếu trong ngày (local TZ). Cách nhau đủ để phim dài không đè nhau.
SLOT_TIMES = [time(10, 0), time(14, 0), time(19, 0)]

ACTOR_BIOS = {
    "Christian Bale": "Diễn viên Anh, Batman trong The Dark Knight trilogy.",
    "Heath Ledger": "Diễn viên Úc, Joker đoạt Oscar.",
    "Tom Hardy": "Diễn viên Anh, Bane / Max / Eames.",
}


class Command(BaseCommand):
    help = (
        "Seed dữ liệu rạp: phim, diễn viên, phòng, suất, user demo, vé. "
        "Idempotent (get_or_create). Dùng --clear để xóa cinema data rồi seed lại."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Xóa Ticket/Showtime/MovieActor/Movie/Actor/Room rồi seed lại.",
        )
        parser.add_argument("--movies", type=int, default=len(MOVIES), help="Số phim (max catalog).")
        parser.add_argument("--rooms", type=int, default=len(ROOMS), help="Số phòng (max catalog).")
        parser.add_argument("--days", type=int, default=7, help="Số ngày suất tương lai.")
        parser.add_argument(
            "--slots",
            type=int,
            default=len(SLOT_TIMES),
            help="Số khung giờ/ngày/phòng (max 3: 10:00, 14:00, 19:00).",
        )
        parser.add_argument("--users", type=int, default=5, help="Số customer demo (customer1..N).")
        parser.add_argument("--tickets", type=int, default=40, help="Số vé demo (pending/booked/cancelled).")
        parser.add_argument(
            "--inactive",
            type=int,
            default=2,
            help="Số phim is_active=False (test ẩn khỏi trang khách).",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self._clear()

        n_movies = max(1, min(options["movies"], len(MOVIES)))
        n_rooms = max(1, min(options["rooms"], len(ROOMS)))
        n_slots = max(1, min(options["slots"], len(SLOT_TIMES)))
        n_inactive = max(0, min(options["inactive"], n_movies - 1))

        movies = self._seed_movies(n_movies, n_inactive)
        rooms = self._seed_rooms(n_rooms)
        showtimes = self._seed_showtimes(movies, rooms, options["days"], n_slots)
        users = self._seed_users(options["users"])
        tickets = self._seed_tickets(showtimes, users, options["tickets"])

        self.stdout.write(self.style.SUCCESS(
            f"Done: {len(movies)} movies, {Actor.objects.count()} actors, "
            f"{len(rooms)} rooms, {len(showtimes)} showtimes, "
            f"{len(users)} customers, {len(tickets)} tickets."
        ))
        self.stdout.write("Login demo:")
        self.stdout.write("  admin / admin123  (is_staff)")
        self.stdout.write("  customer1 / pass1234")

    def _clear(self):
        self.stdout.write("Clearing cinema data...")
        Ticket.objects.all().delete()
        Showtime.objects.all().delete()
        MovieActor.objects.all().delete()
        Movie.objects.all().delete()
        Actor.objects.all().delete()
        Room.objects.all().delete()

    def _seed_movies(self, n_movies, n_inactive):
        catalog = MOVIES[:n_movies]
        inactive_titles = {m["title"] for m in catalog[-n_inactive:]} if n_inactive else set()
        movies = []
        for data in catalog:
            actor_names = data.get("actors", [])
            payload = {k: v for k, v in data.items() if k != "actors"}
            is_active = payload["title"] not in inactive_titles
            movie, _ = Movie.objects.get_or_create(
                title=payload["title"],
                defaults={
                    **payload,
                    "rating": Decimal(payload["rating"]),
                    "is_active": is_active,
                },
            )
            for name in actor_names:
                actor, _ = Actor.objects.get_or_create(
                    name=name,
                    defaults={"bio": ACTOR_BIOS.get(name, f"Diễn viên trong {movie.title}.")},
                )
                MovieActor.objects.get_or_create(movie=movie, actor=actor)
            movies.append(movie)
        return movies

    def _seed_rooms(self, n_rooms):
        rooms = []
        for data in ROOMS[:n_rooms]:
            room, _ = Room.objects.get_or_create(
                name=data["name"],
                defaults={"capacity": data["capacity"]},
            )
            rooms.append(room)
        return rooms

    def _seed_showtimes(self, movies, rooms, days, n_slots):
        tz = timezone.get_current_timezone()
        today = timezone.localdate()
        slots = SLOT_TIMES[:n_slots]
        prices = {
            "Room 1": Decimal("90000.00"),
            "Room 2": Decimal("100000.00"),
            "IMAX": Decimal("150000.00"),
            "VIP": Decimal("200000.00"),
        }
        active_movies = [m for m in movies if m.is_active] or movies
        created = []
        movie_i = 0

        # Quá khứ: 1 suất completed + 1 cancelled (test admin / sync status).
        past_start = timezone.make_aware(datetime.combine(today - timedelta(days=2), time(19, 0)), tz)
        past_movie = active_movies[0]
        past_room = rooms[0]
        st, _ = Showtime.objects.get_or_create(
            room=past_room,
            start_at=past_start,
            defaults={
                "movie": past_movie,
                "end_at": past_start + timedelta(minutes=past_movie.duration_minutes),
                "base_price": prices.get(past_room.name, Decimal("90000.00")),
                "status": Showtime.Status.COMPLETED,
            },
        )
        created.append(st)

        cancel_start = timezone.make_aware(datetime.combine(today + timedelta(days=3), time(21, 30)), tz)
        cancel_room = rooms[-1]
        cancel_movie = active_movies[min(1, len(active_movies) - 1)]
        st, _ = Showtime.objects.get_or_create(
            room=cancel_room,
            start_at=cancel_start,
            defaults={
                "movie": cancel_movie,
                "end_at": cancel_start + timedelta(minutes=cancel_movie.duration_minutes),
                "base_price": prices.get(cancel_room.name, Decimal("90000.00")),
                "status": Showtime.Status.CANCELLED,
            },
        )
        created.append(st)

        for day_offset in range(days):
            day = today + timedelta(days=day_offset + 1)
            for room in rooms:
                for slot in slots:
                    movie = active_movies[movie_i % len(active_movies)]
                    movie_i += 1
                    start_at = timezone.make_aware(datetime.combine(day, slot), tz)
                    end_at = start_at + timedelta(minutes=movie.duration_minutes)
                    st, was_created = Showtime.objects.get_or_create(
                        room=room,
                        start_at=start_at,
                        defaults={
                            "movie": movie,
                            "end_at": end_at,
                            "base_price": prices.get(room.name, Decimal("90000.00")),
                            "status": Showtime.Status.SCHEDULED,
                        },
                    )
                    created.append(st)
        return created

    def _seed_users(self, n_users):
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@cinema.local",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("admin123")
            admin.save()
        elif not admin.is_staff:
            admin.is_staff = True
            admin.is_superuser = True
            admin.save(update_fields=["is_staff", "is_superuser"])

        users = []
        for i in range(1, n_users + 1):
            username = f"customer{i}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": f"{username}@cinema.local"},
            )
            if created:
                user.set_password("pass1234")
                user.save()
            users.append(user)
        return users

    def _seed_tickets(self, showtimes, users, n_tickets):
        if not users or n_tickets <= 0:
            return []

        bookable = [
            st for st in showtimes
            if st.status == Showtime.Status.SCHEDULED and st.start_at > timezone.now()
        ]
        if not bookable:
            return []

        statuses = (
            [Ticket.Status.BOOKED] * 5
            + [Ticket.Status.PENDING] * 3
            + [Ticket.Status.CANCELLED] * 2
        )
        created = []
        i = 0
        for st in bookable:
            seats = generate_seats(st.room.capacity)
            # vài ghế đầu mỗi suất, xoay user + status
            take = min(4, len(seats), n_tickets - len(created))
            for seat in seats[:take]:
                user = users[i % len(users)]
                status = statuses[i % len(statuses)]
                ticket, _ = Ticket.objects.get_or_create(
                    showtime=st,
                    seat=seat,
                    defaults={
                        "customer": user,
                        "price": st.base_price,
                        "status": status,
                    },
                )
                created.append(ticket)
                i += 1
                if len(created) >= n_tickets:
                    return created
        return created
