const toggle = document.querySelector(".header__toggle");
const nav = document.querySelector("#main-nav");
toggle?.addEventListener("click", () => {
  const open = nav.classList.toggle("is-open");
  toggle.setAttribute("aria-expanded", String(open));
});