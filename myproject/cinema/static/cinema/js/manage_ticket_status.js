(function () {
  const ticketId = window.TICKET_ID;
  const form = document.querySelector("form.form-stack");
  const errorBox = document.createElement("p");
  errorBox.className = "helptext";
  errorBox.style.display = "none";
  form?.appendChild(errorBox);

  function showError(message) {
    if (!errorBox) return;
    if (!message) {
      errorBox.textContent = "";
      errorBox.style.display = "none";
      return;
    }
    errorBox.textContent = message;
    errorBox.style.display = "block";
  }

  function getSelectedStatus() {
    const el =
      document.querySelector('select[name="status"]') ||
      document.querySelector('input[name="status"]:checked') ||
      document.querySelector('input[name="status"]');
    return el ? (el.value || "") : "";
  }

  form?.addEventListener("submit", async (e) => {
    e.preventDefault();
    showError(null);
    const status = getSelectedStatus();
    if (!status) {
      showError("Bạn cần chọn trạng thái.");
      return;
    }

    try {
      await cinemaApi("/api/tickets/" + ticketId + "/", {
        method: "PATCH",
        body: { status: status },
      });
      window.location.href = "/manage/tickets/";
    } catch (err) {
      showError(err.message || "Không thể cập nhật status.");
    }
  });
})();

