(function () {
    const grid = document.getElementById("movie-grid");
    const empty = document.getElementById("movie-empty");
    const pager = document.getElementById("movie-pagination");
    const form = document.getElementById("movie-filter");

    const params = new URLSearchParams(window.location.search);

    form.q.value = params.get("q") || "";
    form.genre.value = params.get("genre") || "";
    let page = params.get("page") || "1";

    function syncUrl(q, genre, pageNum) {
        const p = new URLSearchParams();
        if (q) p.set("q", q);
        if (genre) p.set("genre", genre);
        if (pageNum && pageNum !== "1") p.set("page", pageNum);
        const qs = p.toString();
        history.replaceState(null, "", qs ? "?" + qs : window.location.pathname);
    }

    function renderMovies(results) {
        grid.innerHTML = "";
        empty.hidden = results.length > 0;
        for (const m of results) {
            const li = document.createElement("li");
            li.className = "card";
            const a = document.createElement("a");
            a.href = "/movies/" + m.id + "/";
            a.style.cssText = "text-decoration: none; color: inherit;";
            a.innerHTML = 
            `<h2 class="title"></h2>` +
            `<div class="meta">` +
            `<span class="chip"></span><span></span><span></span></div>` +
            `<p class="meta-director"></p>`;

            a.querySelector(".title").textContent = m.title;
            const spans = a.querySelectorAll(".meta span");
            spans[0].textContent = m.genre;
            spans[1].textContent = m.duration_minutes + " phút";
            spans[2].textContent = m.rating + "★";
            a.querySelector(".meta-director").textContent = m.director;
            li.appendChild(a);      // ← thiếu
            grid.appendChild(li);
        }
    }
    
    function renderPager(data) {
        pager.innerHTML = "";
        const pageSize = 12;
        const total = Math.ceil((data.count || 0) / pageSize);
        if (total <= 1) return;
        const cur = parseInt(page, 12) || 1;

        function addLink(label, target) {
            const a = document.createElement("a");
            a.href = "#";
            a.textContent = label;
            a.onclick = (e) => { e.preventDefault(); load(String(target)); };
            pager.appendChild(a);
        }
        if (cur > 1) addLink("«", cur - 1);
        const span = document.createElement("span");
        span.className = "current";
        span.textContent = cur + " / " + total;
        pager.appendChild(span);
        if (cur < total) addLink("»", cur + 1);
    }

    async function load(pageNum) {
        page = pageNum || "1";
        const q = form.q.value.trim();
        const genre = form.genre.value;
        const p = new URLSearchParams();
        if (q) p.set("q", q);
        if (genre) p.set("genre", genre);
        p.set("page", page);
        syncUrl(q, genre, page);

        try {
            const data = await cinemaApi("/api/movies/?" + p.toString());
            renderMovies(data.results || []);
            renderPager(data);
        } catch (err) {
            grid.innerHTML = "";
            empty.hidden = false;
            empty.textContent = err.message;
        }
    }
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        load("1");
    });
    load(page);
})();