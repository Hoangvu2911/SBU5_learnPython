import { api } from "./api.js";

const params = new URLSearchParams(window.location.search);
const showtimeId = params.get("id");

const titleEl = document.getElementById("seat-title");
const subEl = document.getElementById("seat-sub");
const grid = document.getElementById("seat-grid");
const errEl = document.getElementById("seat-error");

const POLL_INTERVAL_MS = 5000;
let pollId = null;
let inFlight = false;

if (!showtimeId) {
    titleEl.textContent = "Không tìm thấy lịch chiếu";
    errEl.hidden = false;
    errEl.textContent = "Thêm ?id=... vào URL để xem ghế";
} else {
    startPolling();
}

function formatDate(iso) {
    return iso ? new Date(iso).toLocaleString("vi-VN") : "";
}

function renderSeats(seats) {
    grid.innerHTML = "";
    for (const item of seats) {
        if (item.status === "available") {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.textContent = item.seat;
            btn.addEventListener("click", () => {
                alert(`Chọn ghế ${item.seat} - book sau khi đăng nhập`);
            });
            grid.appendChild(btn);
        } else {
            const span = document.createElement("span");
            span.textContent = item.seat;
            span.className = item.status === "held" ? "seat-held" : "seat-booked";
            grid.appendChild(span);
        }
    }
}

async function fetchAndRender() {
    if (inFlight) return;
    inFlight = true;

    try {
        errEl.hidden = true;
        const data = await api(`/api/showtimes/${showtimeId}/seats/`);
        const st = data.showtime;
        titleEl.textContent = st.movie.title;
        subEl.textContent = `Tên phim: ${st.movie_title} - Lịch chiếu: ${formatDate(st.start_at)} - ${formatDate(st.end_at)} - Phòng: ${st.room_name}`;
        renderSeats(data.seats || []);
    } catch (err) {
        titleEl.textContent = "Lỗi khi tải ghế";
        errEl.hidden = false;
        errEl.textContent = err.message;
    } finally {
        inFlight = false;
    }
}

function startPolling() {
    fetchAndRender();
    pollId = setInterval(fetchAndRender, POLL_INTERVAL_MS);

    window.addEventListener("beforeunload", () => {
        if (pollId) clearInterval(pollId);
    })
}
