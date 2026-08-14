import { api } from "./api.js";

const grid = document.getElementById("movie-grid");
const empty = document.getElementById("movie-empty");
const pager = document.getElementById("movie-pagination");
const form = document.getElementById("movie-filter");

const PAGE_SIZE = 12;

function renderMovies(results) {
    grid.innerHTML = "";
    empty.hidden = results.length > 0;
  
    for (const m of results) {
      const li = document.createElement("li");
      li.className = "movie-card";
  
      const title = document.createElement("h2");
      title.className = "movie-card__title";
      title.textContent = m.title;
      const meta = document.createElement("p");
      meta.className = "movie-card__meta";
      meta.textContent = `${m.genre} · ${m.duration_minutes} phút · ★ ${m.rating}`;
  
      li.append(title, meta);
      grid.appendChild(li);
    }
}

function renderPager(data, currentPage) {
    pager.innerHTML = "";
    const total = Math.ceil((data.count || 0) / PAGE_SIZE);
    if (total <= 1) return;
  
    const cur = parseInt(currentPage, 10) || 1;
  
    if (cur > 1) {
      const prev = document.createElement("a");
      prev.href = "#";
      prev.textContent = "«";
      prev.addEventListener("click", (e) => {
        e.preventDefault();
        load(String(cur - 1));
      });
      pager.appendChild(prev);
    }
  
    const span = document.createElement("span");
    span.className = "current";
    span.textContent = `${cur} / ${total}`;
    pager.appendChild(span);
  
    if (cur < total) {
      const next = document.createElement("a");
      next.href = "#";
      next.textContent = "»";
      next.addEventListener("click", (e) => {
        e.preventDefault();
        load(String(cur + 1));
      });
      pager.appendChild(next);
    }
}

async function load(page = "1") {
    const q = form.q.value.trim();
    const genre = form.genre.value;
  
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (genre) params.set("genre", genre);
    params.set("page", page);
  
    try {
      const data = await api("/api/movies/?" + params.toString());
      // data = { count, next, previous, results: [...] }
      renderMovies(data.results || []);
      renderPager(data, page);
    } catch (err) {
      grid.innerHTML = "";
      empty.hidden = false;
      empty.textContent = err.message || "Không tải được phim";
    }
}

form.addEventListener("submit", (e) => {
    e.preventDefault(); // không reload trang
    load("1");
});
  
load("1");