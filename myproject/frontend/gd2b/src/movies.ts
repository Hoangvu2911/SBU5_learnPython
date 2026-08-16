import { api } from "./api.ts";
import type { Movie, Paginated } from "./type.ts";

function requireEl<T extends HTMLElement>(id: string, ctor: new () => T): T {
  const el = document.getElementById(id);
  if (!(el instanceof ctor)) throw new Error(`missing #${id}`);
  return el;
}

const grid = requireEl("movie-grid", HTMLUListElement);
const empty = requireEl("movie-empty", HTMLParagraphElement);
const pager = requireEl("movie-pagination", HTMLDivElement);
const form = requireEl("movie-filter", HTMLFormElement);

const PAGE_SIZE = 12;

function renderMovies(results: Movie[]): void {
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

function renderPager(data: Paginated<Movie>, currentPage: string): void {
  pager.innerHTML = "";
  const total = Math.ceil((data.count || 0 ) / PAGE_SIZE);
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
    const qEl = form.elements.namedItem("q");
    const genreEl = form.elements.namedItem("genre");
    if (!(qEl instanceof HTMLInputElement) || !(genreEl instanceof HTMLSelectElement)) {
      throw new Error("filter fields missing");
    }
    const q = qEl.value.trim();
    const genre = genreEl.value;
  
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (genre) params.set("genre", genre);
    params.set("page", page);
  
    try {
      const data = await api<Paginated<Movie>>("/api/movies/?" + params.toString());
      renderMovies(data.results);
      renderPager(data, page);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Không tải được phim";
      empty.textContent = msg;
      empty.hidden = false;
    }
}

form.addEventListener("submit", (e) => {
    e.preventDefault();
    load("1");
});
  
load("1");