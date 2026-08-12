(function () {
    const showtimeId = window.SHOWTIME_ID;
    const titleEl = document.getElementById("seat-title");
    const subEl = document.getElementById("seat-sub");
    const grid = document.getElementById("seat-grid");
    const errEl = document.getElementById("seat-error");

    const POLL_INTERVAL_MS = 3000;
    let pollId = null;
    let inFlight = false;
  
    function formatDate(iso) {
      return iso ? new Date(iso).toLocaleString("vi-VN") : "";
    }
  
    function renderSeats(seats, onPick) {
      grid.innerHTML = "";
      for (const item of seats) {
        if (item.status === "available") {
          const btn = document.createElement("button");
          btn.type = "button";
          btn.textContent = item.seat;
          btn.onclick = () => onPick(item.seat);
          grid.appendChild(btn);
        } else {
          const span = document.createElement("span");
          span.textContent = item.seat;
          span.className = item.status === "held" ? "seat-held" : "seat-booked";
          grid.appendChild(span);
        }
      }
    }
  
    async function bookSeat(seat) {
      errEl.hidden = true;
      try {
        await cinemaApi("/api/showtimes/" + showtimeId + "/book/", {
          method: "POST",
          body: { seat: seat },
        });
        if (pollId) clearInterval(pollId);
        window.location.href = "/tickets/mine/";
      } catch (err) {
        errEl.hidden = false;
        errEl.textContent = err.message;
      }
    }
  
    async function fetchAndRender() {
      if (inFlight) return;
      inFlight = true;

      try {
        const data = await cinemaApi("/api/showtimes/" + showtimeId + "/seats/", {
          cache: "no-store",
        });
        const st = data.showtime;
        titleEl.textContent = st.movie_title;
        subEl.textContent =
          st.room_name +  " · Lịch chiếu: " + formatDate(st.start_at) + " · Giá: " + st.base_price;
        renderSeats(data.seats || [], bookSeat);
      } catch (err) {
        titleEl.textContent = "Không tải được suất";
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
      });
    }

    startPolling();
  })();