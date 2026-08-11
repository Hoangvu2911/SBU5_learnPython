(function () {
  const grid = document.getElementById("room-grid");
  const empty = document.getElementById("room-empty");

  async function load() {
    try {
      const data = await cinemaApi("/api/rooms/?page=1");
      const results = data.results || [];

      grid.innerHTML = "";
      empty.hidden = results.length > 0;

      for (const r of results) {
        const li = document.createElement("li");
        li.className = "card";
        li.innerHTML =
          "<h2 class='title'></h2>" +
          "<div class='meta'>" +
          "<span class='chip'>Phòng</span>" +
          "<span></span>" +
          "</div>" +
          "<a href=''>Sửa</a>";

        li.querySelector(".title").textContent = r.name;
        const spans = li.querySelectorAll(".meta span");
        spans[1].textContent = r.capacity + " chỗ";
        li.querySelector("a").href = "/manage/rooms/" + r.id + "/edit/";

        grid.appendChild(li);
      }
    } catch (err) {
      grid.innerHTML = "";
      empty.hidden = false;
      empty.textContent = err.message || "Không tải được phòng";
    }
  }

  load();
})();

