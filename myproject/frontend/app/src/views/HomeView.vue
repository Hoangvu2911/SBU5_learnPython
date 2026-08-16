<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import MovieCard from "@/components/MovieCard.vue";
import { api } from "@/api/client";
import type { Movie, Paginated } from "@/api/type";

const movies = ref<Movie[]>([]);
const count = ref(0);
const page = ref(1);
const q = ref("");
const genre = ref("");
const error = ref("");
const PAGE_SIZE = 12;

const totalPages = computed(() => Math.ceil(count.value / PAGE_SIZE) || 0);

async function load(p = 1) {
  page.value = p;
  const params = new URLSearchParams();
  if (q.value.trim()) params.set("q", q.value.trim());
  if (genre.value) params.set("genre", genre.value);
  params.set("page", String(p));
  try {
    error.value = "";
    const data = await api<Paginated<Movie>>("/api/movies/?" + params.toString());
    movies.value = data.results;
    count.value = data.count;
  } catch (e) {
    movies.value = [];
    error.value = e instanceof Error ? e.message : "Không tải được phim";
  }
}

onMounted(() => load(1));
</script>

<template>
  <div class="wrap">
    <header class="header">
      <h1 class="header__title">Cinema</h1>
    </header>

    <form class="filter" @submit.prevent="load(1)">
      <input v-model="q" class="filter__input" type="search" placeholder="Tìm phim..." />
      <select v-model="genre" class="filter__select">
        <option value="">Tất cả thể loại</option>
        <option value="action">Hành động</option>
        <option value="Drama">Tình cảm</option>
        <option value="horror">Kinh dị</option>
        <option value="animation">Hoạt hình</option>
      </select>
      <button class="filter__btn" type="submit">Lọc</button>
    </form>

    <p v-if="error" class="empty">{{ error }}</p>
    <p v-else-if="count === 0" class="empty">Không có phim</p>

    <ul class="movie-grid">
      <MovieCard
        v-for="m in movies"
        :key="m.id"
        :id="m.id"
        :title="m.title"
        :genre="m.genre"
        :rating="m.rating"
        :duration-minutes="m.duration_minutes"
      />
    </ul>

    <div v-if="totalPages > 1" class="pager">
      <a v-if="page > 1" href="#" @click.prevent="load(page - 1)">«</a>
      <span class="current">{{ page }} / {{ totalPages }}</span>
      <a v-if="page < totalPages" href="#" @click.prevent="load(page + 1)">»</a>
    </div>
  </div>
</template>