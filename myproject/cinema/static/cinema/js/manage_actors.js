(function () {
  const grid = document.getElementById("actor-grid");
  const empty = document.getElementById("actor-empty");

  async function load() {
    try {
      const data = await cinemaApi("/api/actors/?page=1");
      const results = data.results || [];

      grid.innerHTML = "";
      empty.hidden = results.length > 0;

      for (const a of results) {
        const li = document.createElement("li");
        li.className = "card";
        li.innerHTML =
          "<h2 class='title'></h2>" +
          "<div class='meta'><span class='chip'>Diễn viên</span><span></span></div>" +
          "<a href=''>Sửa</a>";

        li.querySelector(".title").textContent = a.name;
        li.querySelectorAll(".meta span")[1].textContent = a.bio || "Không có bio";
        li.querySelector("a").href = "/manage/actors/" + a.id + "/edit/";

        grid.appendChild(li);
      }
    } catch (err) {
      grid.innerHTML = "";
      empty.hidden = false;
      empty.textContent = err.message || "Không tải được diễn viên";
    }
  }

  load();
})();
