(function () {
  const form = document.querySelector("form.form-stack");
  if (!form) return;

  const apiUrl = form.dataset.apiUrl;
  const apiMethod = (form.dataset.apiMethod || "POST").toUpperCase();
  const cancelUrl = form.dataset.cancelUrl;

  if (!apiUrl) return;

  const errorBox = document.createElement("p");
  errorBox.className = "helptext";
  errorBox.style.display = "none";
  form.appendChild(errorBox);

  function showError(message) {
    if (!message) {
      errorBox.style.display = "none";
      errorBox.textContent = "";
      return;
    }
    errorBox.textContent = message;
    errorBox.style.display = "block";
  }

  function toPayload() {
    const payload = {};
    const elements = form.querySelectorAll("input, select, textarea");
    elements.forEach((el) => {
      const name = el.name;
      if (!name) return;
      if (el.type === "submit" || el.type === "button") return;
      if (name === "csrfmiddlewaretoken") return;

      if (el.type === "checkbox") {
        payload[name] = el.checked;
        return;
      }

      if (el.value === undefined) return;
      payload[name] = el.value;
    });
    return payload;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    showError(null);

    const payload = toPayload();
    try {
      await cinemaApi(apiUrl, {
        method: apiMethod,
        body: payload,
      });
      window.location.href = cancelUrl;
    } catch (err) {
      showError(err.message || "Không thể lưu.");
    }
  });
})();

