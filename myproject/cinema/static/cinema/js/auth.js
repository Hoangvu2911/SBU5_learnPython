(function () {
    function getNext() {
      const p = new URLSearchParams(window.location.search);
      return p.get("next") || "/";
    }
  
    function getVal(form, name) {
      const el = form.querySelector(`[name="${name}"]`);
      return el ? el.value : "";
    }
  
    async function handleLogin(form) {
      const username = getVal(form, "username");
      const password = getVal(form, "password");
  
      const next = getNext();
      await window.cinemaApi("/api/auth/login/", {
        method: "POST",
        body: { username, password },
      });
  
      window.location.href = next;
    }
  
    async function handleRegister(form) {
      const username = getVal(form, "username");
      const password1 = getVal(form, "password1");
      const password2 = getVal(form, "password2");
  
      const next = getNext();
      await window.cinemaApi("/api/auth/register/", {
        method: "POST",
        body: {
          username,
          password: password1,
          password_confirm: password2,
        },
      });
  
      window.location.href = next;
    }
  
    window.addEventListener("DOMContentLoaded", () => {
      const loginForm = document.getElementById("login-form");
      if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
          e.preventDefault();
          await handleLogin(loginForm);
        });
        return;
      }
  
      const registerForm = document.getElementById("register-form");
      if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
          e.preventDefault();
          await handleRegister(registerForm);
        });
      }
    });
  })();