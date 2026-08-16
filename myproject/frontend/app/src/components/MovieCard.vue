<script setup lang="ts">
defineProps<{
  id: number;
  title: string;
  genre: string;
  rating: number;
  durationMinutes: number;
}>();
</script>

<template>
  <li class="movie-card">
    <router-link :to="{ name: 'movie-detail', params: { id } }">
      <h2 class="movie-card__title">{{ title }}</h2>
      <p class="movie-card__meta">
        {{ genre }} · {{ durationMinutes }} phút · ★ {{ rating }}
      </p>
    </router-link>
  </li>
</template>