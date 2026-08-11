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

  function getFieldValue(name) {
    const el = form.querySelector(`[name="${CSS.escape(name)}"]`);
    if (!el) return undefined;
    if (el.type === "checkbox") return el.checked;
    return el.value;
  }

  function getActorIdsFromFormset() {
    const actorEls = form.querySelectorAll('[name$="-actor"]');
    const ids = new Set();

    actorEls.forEach((actorEl) => {
      const actorName = actorEl.name;
      const actorId = parseInt(actorEl.value, 10);
      if (!actorId) return;

      const deleteName = actorName.replace(/-actor$/, "-DELETE");
      const deleteEl = form.querySelector(`[name="${CSS.escape(deleteName)}"]`);
      if (deleteEl && deleteEl.checked) return;

      ids.add(actorId);
    });

    return Array.from(ids);
  }

  function buildPayload() {
    const payload = {};

    // Whitelist movie form fields (match MovieForm in forms.py)
    const movieFields = [
      "title",
      "description",
      "release_date",
      "genre",
      "rating",
      "duration_minutes",
      "director",
      "is_active",
    ];

    movieFields.forEach((f) => {
      const val = getFieldValue(f);
      if (val !== undefined) payload[f] = val;
    });

    payload.actor_ids = getActorIdsFromFormset();
    return payload;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    showError(null);

    const payload = buildPayload();
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

