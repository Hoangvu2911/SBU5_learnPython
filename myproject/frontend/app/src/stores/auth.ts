import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { api } from "@/api/client";
import type { AuthResponse, AuthUser } from "@/api/type";

const TOKEN_KEY = "auth-token";
const USER_KEY = "auth-user";

export const useAuthStore = defineStore("auth", () => {
    const token = ref(localStorage.getItem(TOKEN_KEY) ?? "");
    const user = ref<AuthUser | null>(JSON.parse(localStorage.getItem(USER_KEY) ?? "null"));

    const isLoggedIn = computed(() => Boolean(token.value));
    const isStaff = computed(() => Boolean(user.value?.is_staff));

    function persist(t: string, u: AuthUser) {
        token.value = t;
        user.value = u;
        localStorage.setItem(TOKEN_KEY, t);
        localStorage.setItem(USER_KEY, JSON.stringify(u));
    }

    function clear() {
        token.value = "";
        user.value = null;
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
    }

    async function login(username: string, password: string) {
        const data = await api<AuthResponse>("/api/auth/login/", {
          method: "POST",
          body: JSON.stringify({ username, password }),
        });
        persist(data.token, data.user);
    }
    
    async function register(username: string, password: string, passwordConfirm: string) {
        const data = await api<AuthResponse>("/api/auth/register/", {
          method: "POST",
          body: JSON.stringify({
            username,
            password,
            password_confirm: passwordConfirm,
          }),
        });
        persist(data.token, data.user);
    }

    async function logout() {
        try {
          await api("/api/auth/logout/", { method: "POST" });
        } finally {
          clear();
        }
    }

    return { token, user, isLoggedIn, isStaff, login, register, logout };
});