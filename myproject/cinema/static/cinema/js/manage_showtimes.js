(function () {
  const grid = document.getElementById("showtime-grid");
  const empty = document.getElementById("showtime-empty");
  const pager = document.getElementById("showtime-pagination");

  const form = document.querySelector("form.form-stack");
  const movieSelect = form?.querySelector('select[name="movie"]');
  const statusSelect = form?.querySelector('select[name="status"]');

  const params = new URLSearchParams(window.location.search);
  let page = params.get("page") || "1";

  function formatDate(iso) {
    return iso ? new Date(iso).toLocaleString("vi-VN") : "";
  }

  function renderPager(data) {
    pager.innerHTML = "";
    const pageSize = 12;
    const total = Math.ceil((data.count || 0) / pageSize);
    if (total <= 1) return;

    const cur = parseInt(page, 10) || 1;

    function addLink(label, targetPage) {
      const a = document.createElement("a");
      a.href = "#";
      a.textContent = label;
      a.onclick = (e) => {
        e.preventDefault();
        load(String(targetPage));
      };
      pager.appendChild(a);
    }

    if (cur > 1) addLink("«", cur - 1);

    const span = document.createElement("span");
    span.className = "current";
    span.textContent = cur + " / " + total;
    pager.appendChild(span);

    if (cur < total) addLink("»", cur + 1);
  }

  function getFilters() {
    const movie = movieSelect?.value || "";
    const status = statusSelect?.value || "";
    return { movie, status };
  }

  async function load(pageNum) {
    page = pageNum || "1";
    const { movie, status } = getFilters();

    const p = new URLSearchParams();
    p.set("page", page);
    if (movie) p.set("movie", movie);
    if (status) p.set("status", status);

    try {
      const data = await cinemaApi("/api/showtimes/?" + p.toString());
      const results = data.results || [];

      grid.innerHTML = "";
      empty.hidden = results.length > 0;

      for (const s of results) {
        const li = document.createElement("li");
        li.className = "card";

        li.innerHTML =
          "<h2 class='title'></h2>" +
          "<div class='meta'>" +
          "<span></span>" +
          "<span></span>" +
          "<span></span>" +
          "<span class='chip meta-status'></span>" +
          "</div>" +
          "<a href=''>Sửa</a>" +
          "<div class='ticket-actions'></div>";

        li.querySelector(".title").textContent = s.movie_title;
        const spans = li.querySelectorAll(".meta span");
        spans[0].textContent = s.room_name;
        spans[1].textContent = formatDate(s.start_at);
        spans[2].textContent = s.base_price;
        li.querySelector(".meta-status").textContent = s.status;

        if (s.is_bookable) {
          const meta = document.createElement("span");
          meta.textContent = "Bookable";
          li.querySelector(".meta").appendChild(meta);
        }

        li.querySelector("a").href = "/manage/showtimes/" + s.id + "/edit/";

        const actions = li.querySelector(".ticket-actions");
        if (s.status === "scheduled" || s.status === "ongoing") {
          const btn = document.createElement("button");
          btn.className = "btn btn-outline";
          btn.type = "button";
          btn.textContent = "Hủy suất";
          btn.onclick = async () => {
            if (!confirm("Hủy suất và vé active?")) return;
            await cinemaApi("/api/showtimes/" + s.id + "/cancel/", {
              method: "POST",
              body: {},
            });
            load(page);
          };
          actions.appendChild(btn);
        }

        grid.appendChild(li);
      }

      renderPager(data);
    } catch (err) {
      grid.innerHTML = "";
      empty.hidden = false;
      empty.textContent = err.message || "Không tải được suất";
    }
  }

  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      load("1");
    });
  }

  load(page);
})();

