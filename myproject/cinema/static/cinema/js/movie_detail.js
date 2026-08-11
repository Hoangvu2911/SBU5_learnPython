(function () {
    const movieId = window.MOVIE_ID;
    const loggedIn = window.USER_AUTHENTICATED;

    const titleEl = document.getElementById("movie-title");
    const subEl = document.getElementById("movie-sub");
    const descEl = document.getElementById("movie-desc");
    const castEl = document.getElementById("movie-cast");
    const grid = document.getElementById("showtime-grid");
    const empty = document.getElementById("showtime-empty");

    function formatDate(iso) {
        if (!iso) return "";
        const d = new Date(iso);
        return d.toLocaleString("vi-VN");
    }

    function renderMovie(m) {
        document.title = m.title;
        titleEl.textContent = m.title;
        subEl.textContent =
          m.genre + " · " + m.duration_minutes + " phút · ★ " + m.rating + " · " + m.director;
        descEl.textContent = m.description || "";
        castEl.innerHTML = (m.cast || [])
          .map((a) => '<span class="chip">' + a.name + "</span>")
          .join("");
    }

    function renderShowtimes(list) {
        grid.innerHTML = "";
        empty.hidden = list.length > 0;
        for (const s of list) {
          const li = document.createElement("li");
          li.className = "card";
          const bookHref = loggedIn
            ? "/showtimes/" + s.id + "/seats/"
            : "/accounts/login/?next=/showtimes/" + s.id + "/seats/";
          const btnLabel = loggedIn ? "Chọn ghế" : "Đăng nhập để đặt";
          li.innerHTML =
            '<h2 class="title"></h2><div class="meta">' +
            "<span></span><span></span></div>" +
            '<a class="btn" href="' + bookHref + '">' + btnLabel + "</a>";
          li.querySelector(".title").textContent = s.room_name;
          const spans = li.querySelectorAll(".meta span");
          spans[0].textContent = "Lịch chiếu: " + formatDate(s.start_at);
          spans[1].textContent = "Giá: " + s.base_price;
          grid.appendChild(li);
        }
    }

    async function load() {
        try {
          const [movie, showtimes] = await Promise.all([
            cinemaApi("/api/movies/" + movieId + "/"),
            cinemaApi("/api/showtimes/?movie=" + movieId),
          ]);
          renderMovie(movie);
          renderShowtimes(showtimes.results || []);
        } catch (err) {
          titleEl.textContent = "Không tải được phim";
          descEl.textContent = err.message;
        }
    }
    load();
})();