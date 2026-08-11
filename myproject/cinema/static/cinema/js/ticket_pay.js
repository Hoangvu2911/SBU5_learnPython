(function () {
  const ticketId = window.TICKET_ID;
  const subEl = document.getElementById("tp-sub");
  const statusEl = document.getElementById("tp-status");
  const actionsEl = document.getElementById("tp-actions");

  function renderActions(status) {
    actionsEl.innerHTML = "";

    if (status === "pending") {
      const btn = document.createElement("button");
      btn.className = "btn";
      btn.type = "button";
      btn.textContent = "Xác nhận thanh toán";
      btn.onclick = async () => {
        await cinemaApi("/api/tickets/" + ticketId + "/pay/", {
          method: "POST",
          body: {},
        });
        window.location.href = "/tickets/mine/";
      };
      actionsEl.appendChild(btn);
      return;
    }
  }

  async function load() {
    const t = await cinemaApi("/api/tickets/" + ticketId + "/");
    subEl.textContent = t.movie_title + " · ghế " + t.seat + " · " + t.price;
    statusEl.textContent = t.status;
    renderActions(t.status);
  }

  load().catch((err) => {
    subEl.textContent = "Không tải được vé";
    statusEl.textContent = "-";
    actionsEl.innerHTML = "";
    const p = document.createElement("p");
    p.className = "helptext";
    p.textContent = err.message || "Lỗi";
    actionsEl.appendChild(p);
  });
})();

