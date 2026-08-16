<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { api } from "@/api/client";
import type { Movie, Paginated, Showtime } from "@/api/type";

const route = useRoute();
const movieId = computed(() => Number(route.params.id));

const movie = ref<Movie | null>(null);
const showtimes = ref<Showtime[]>([]);
const error = ref("");

async function load() {
  if (!Number.isFinite(movieId.value)) {
    error.value = "ID phim không hợp lệ";
    return;
  }
  try {
    error.value = "";
    const [m, st] = await Promise.all([
      api<Movie>(`/api/movies/${movieId.value}/`),
      api<Paginated<Showtime>>(`/api/showtimes/?movie=${movieId.value}`),
    ]);
    movie.value = m;
    showtimes.value = st.results;
  } catch (e) {
    movie.value = null;
    showtimes.value = [];
    error.value = e instanceof Error ? e.message : "Không tải được phim";
  }
}

onMounted(load);
watch(movieId, load);

function formatDate(iso: string) {
  return iso ? new Date(iso).toLocaleString("vi-VN") : "";
}
</script>

<template>
  <div class="wrap">
    <p><router-link to="/">← Danh sách phim</router-link></p>

    <p v-if="error" class="empty">{{ error }}</p>

    <template v-else-if="movie">
      <header class="header">
        <h1 class="header__title">{{ movie.title }}</h1>
        <p class="header__sub">
          {{ movie.genre }} · {{ movie.duration_minutes }} phút · ★ {{ movie.rating }} ·
          {{ movie.director }}
        </p>
      </header>
      <p>{{ movie.description }}</p>
      <p>
        <span v-for="a in movie.cast" :key="a.id">{{ a.name }} </span>
      </p>

      <h2>Lịch chiếu</h2>
      <p v-if="showtimes.length === 0" class="empty">Chưa có suất.</p>
      <ul class="movie-grid">
        <li v-for="s in showtimes" :key="s.id" class="movie-card">
          <h2 class="movie-card__title">{{ s.room_name }}</h2>
          <p class="movie-card__meta">{{ formatDate(s.start_at) }} · {{ s.base_price }}</p>
          <router-link :to="{ name: 'seats', params: { id: s.id } }">Chọn ghế</router-link>
        </li>
      </ul>
    </template>
  </div>
</template>