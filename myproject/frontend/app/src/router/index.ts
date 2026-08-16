import { createRouter, createWebHistory } from "vue-router";
import HomeView from "@/views/HomeView.vue";
import MovieDetailView from "@/views/MovieDetailView.vue";
import SeatMapView from "@/views/SeatMapView.vue";
import LoginView from "@/views/LoginView.vue";
import RegisterView from "@/views/RegisterView.vue";
import { useAuthStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: "/", name: "home", component: HomeView },
    { path: "/login", name: "login", component: LoginView },
    { path: "/register", name: "register", component: RegisterView },
    { path: "/movies/:id", name: "movie-detail", component: MovieDetailView },
    { path: "/seats/:id", name: "seats", component: SeatMapView },
  ],
});

router.beforeEach((to) => {
    const auth = useAuthStore();
    if (to.meta.requiresAuth && !auth.isLoggedIn) {
      return { name: "login", query: { next: to.fullPath } };
    }
    if (to.meta.requiresStaff && !auth.isStaff) {
      return { name: "home" };
    }
  });

export default router;