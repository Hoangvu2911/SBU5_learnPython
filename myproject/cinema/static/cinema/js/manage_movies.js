(function () {
  const grid = document.getElementById("movie-grid");
  const empty = document.getElementById("movie-empty");
  const pager = document.getElementById("movie-pagination");

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

  async function load(pageNum) {
    page = pageNum || "1";
    const p = new URLSearchParams();
    p.set("page", page);

    try {
      const data = await cinemaApi("/api/movies/?" + p.toString());
      const results = data.results || [];

      grid.innerHTML = "";
      empty.hidden = results.length > 0;

      for (const m of results) {
        const li = document.createElement("li");
        li.className = "card";

        li.innerHTML =
          "<h2 class='title'></h2>" +
          "<div class='meta'>" +
          "<span class='chip'></span>" + // active status
          "<span></span>" + // duration
          "<span></span>" + // rating
          "</div>" +
          "<p class='meta-director'></p>" +
          "<a href=''>Sửa</a>" +
          "<div class='ticket-actions'></div>";

        li.querySelector(".title").textContent = m.title;
        const spans = li.querySelectorAll(".meta span");
        spans[0].textContent = m.is_active ? "Đang chiếu" : "Tạm ẩn";
        spans[1].textContent = m.duration_minutes + " phút";
        spans[2].textContent = (m.rating ?? 0) + "★";
        li.querySelector(".meta-director").textContent = m.director || "";

        li.querySelector("a").href = "/manage/movies/" + m.id + "/edit/";

        const actions = li.querySelector(".ticket-actions");
        const btn = document.createElement("button");
        btn.className = "btn btn-outline";
        btn.type = "button";
        btn.textContent = m.is_active ? "Ẩn" : "Hiện";
        btn.disabled = false;
        btn.onclick = async () => {
          btn.disabled = true;
          btn.textContent = "Đang cập nhật...";
          await cinemaApi("/api/movies/" + m.id + "/toggle/", {
            method: "POST",
            body: {},
          });
          load(page);
        };
        actions.appendChild(btn);

        grid.appendChild(li);
      }

      renderPager(data);
    } catch (err) {
      grid.innerHTML = "";
      empty.hidden = false;
      empty.textContent = err.message || "Không tải được phim";
    }
  }

  load(page);
})();

