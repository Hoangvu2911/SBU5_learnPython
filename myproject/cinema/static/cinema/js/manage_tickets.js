(function () {
  const grid = document.getElementById("ticket-grid");
  const empty = document.getElementById("ticket-empty");
  const pager = document.getElementById("ticket-pagination");

  const form = document.querySelector("form.form-stack");
  const showtimeSelect = form?.querySelector('select[name="showtime"]');
  const statusSelect = form?.querySelector('select[name="status"]');

  const params = new URLSearchParams(window.location.search);
  let page = params.get("page") || "1";

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
    const showtime = showtimeSelect?.value || "";
    const status = statusSelect?.value || "";
    return { showtime, status };
  }

  async function load(pageNum) {
    page = pageNum || "1";
    const { showtime, status } = getFilters();

    const p = new URLSearchParams();
    p.set("page", page);
    if (showtime) p.set("showtime", showtime);
    if (status) p.set("status", status);

    try {
      const data = await cinemaApi("/api/tickets/?" + p.toString());
      const results = data.results || [];

      grid.innerHTML = "";
      empty.hidden = results.length > 0;

      for (const t of results) {
        const li = document.createElement("li");
        li.className = "card";

        li.innerHTML =
          "<h2 class='title'></h2>" +
          "<div class='meta'>" +
          "<span></span>" + // customer
          "<span></span>" + // movie
          "<span></span>" + // time
          "<span></span>" + // price
          "<span class='chip'></span>" + // status
          "</div>" +
          "<a href=''>Đổi status</a>";

        li.querySelector(".title").textContent = "#" + t.id + " · " + t.seat;
        const spans = li.querySelectorAll(".meta span");
        spans[0].textContent = t.customer;
        spans[1].textContent = t.movie_title;
        spans[2].textContent = t.start_at ? new Date(t.start_at).toLocaleString("vi-VN") : "";
        spans[3].textContent = t.price;
        spans[4].textContent = t.status;

        li.querySelector("a").href = "/manage/tickets/" + t.id + "/edit/";

        grid.appendChild(li);
      }

      renderPager(data);
    } catch (err) {
      grid.innerHTML = "";
      empty.hidden = false;
      empty.textContent = err.message || "Không tải được vé";
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

