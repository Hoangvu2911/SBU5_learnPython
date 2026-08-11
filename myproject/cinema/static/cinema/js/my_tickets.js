(function () {
    const grid = document.getElementById("ticket-grid");
    const empty = document.getElementById("ticket-empty");
    const pager = document.getElementById("ticket-pagination");
    const form = document.getElementById("ticket-filter");
  
    const params = new URLSearchParams(window.location.search);
    const pageSize = 12;
  
    form.q.value = params.get("q") || "";
    form.status.value = params.get("status") || "";
  
    let page = params.get("page") || "1";
  
    function formatDate(iso) {
      return iso ? new Date(iso).toLocaleString("vi-VN") : "";
    }
  
    async function renderTickets(list) {
      grid.innerHTML = "";
      empty.hidden = list.length > 0;
  
      for (const t of list) {
        const li = document.createElement("li");
        li.className = "card";
  
        li.innerHTML =
          "<h2 class='title'></h2>" +
          "<div class='meta'>" +
          "<span class='meta-room'></span>" +
          "<span class='meta-time'></span>" +
          "<span class='meta-price'></span>" +
          "<span class='chip meta-status'></span>" +
          "</div>" +
          "<div class='ticket-actions'></div>";
  
        li.querySelector(".title").textContent = t.movie_title + " · " + t.seat;
        li.querySelector(".meta-room").textContent = t.room_name;
        li.querySelector(".meta-time").textContent = formatDate(t.start_at);
        li.querySelector(".meta-price").textContent = t.price;
        li.querySelector(".meta-status").textContent = t.status;
  
        const actions = li.querySelector(".ticket-actions");
  
        // pending -> pay
        if (t.status === "pending") {
          const payBtn = document.createElement("button");
          payBtn.className = "btn";
          payBtn.textContent = "Thanh toán";
          payBtn.onclick = () => {
            window.location.href = "/tickets/" + t.id + "/pay/";
          };
          actions.appendChild(payBtn);
        }
  
        if (t.status === "pending" || t.status === "booked") {
          const cancelBtn = document.createElement("button");
          cancelBtn.className = "btn btn-outline";
          cancelBtn.textContent = "Hủy vé";
          cancelBtn.onclick = async () => {
            if (!confirm("Hủy vé này?")) return;
            await cinemaApi("/api/tickets/" + t.id + "/cancel/", {
              method: "POST",
              body: {},
            });
            load(page);
          };
          actions.appendChild(cancelBtn);
        }
  
        grid.appendChild(li);
      }
    }
  
    function renderPager(data) {
      pager.innerHTML = "";
  
      const total = Math.ceil((data.count || 0) / pageSize);
      if (total <= 1) return;
  
      const cur = parseInt(page, 10) || 1;
  
      if (cur > 1) {
        const prev = document.createElement("a");
        prev.href = "#";
        prev.textContent = "«";
        prev.onclick = (e) => { e.preventDefault(); load(String(cur - 1)); };
        pager.appendChild(prev);
      }
  
      const span = document.createElement("span");
      span.className = "current";
      span.textContent = cur + " / " + total;
      pager.appendChild(span);
  
      if (cur < total) {
        const next = document.createElement("a");
        next.href = "#";
        next.textContent = "»";
        next.onclick = (e) => { e.preventDefault(); load(String(cur + 1)); };
        pager.appendChild(next);
      }
    }
  
    async function load(pageNum) {
      page = pageNum || "1";
  
      const q = form.q.value.trim();
      const status = form.status.value;
  
      const p = new URLSearchParams();
      p.set("mine", "1");
      if (q) p.set("q", q);
      if (status) p.set("status", status);
      p.set("page", page);
  
      try {
        const data = await cinemaApi("/api/tickets/?" + p.toString());
        renderTickets(data.results || []);
        renderPager(data);
      } catch (e) {
        grid.innerHTML = "";
        empty.hidden = false;
        empty.textContent = e.message;
      }
    }
  
    form.addEventListener("submit", () => {
    });
  
    load(page);
  })();