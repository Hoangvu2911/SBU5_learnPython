<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api } from "@/api/client";
import type { Seat, SeatMapResponse } from "@/api/type";
import SeatButton from "@/components/SeatButton.vue";

const route = useRoute();
const router = useRouter();
const showtimeId = computed(() => route.params.id as string);

const title = ref("Đang tải...");
const sub = ref("");
const seats = ref<Seat[]>([]);
const error = ref("");
const inFlight = ref(false);

const POLL_MS = 3000;
let pollId: ReturnType<typeof setInterval> | null = null;

async function fetchSeats() {
  if (inFlight.value) return;
  inFlight.value = true;
  try {
    error.value = "";
    const data = await api<SeatMapResponse>(
      `/api/showtimes/${showtimeId.value}/seats/`,
    );
    const st = data.showtime;
    title.value = st.movie_title;
    sub.value = `${st.room_name} · ${new Date(st.start_at).toLocaleString("vi-VN")}`;
    seats.value = data.seats;
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Lỗi tải ghế";
  } finally {
    inFlight.value = false;
  }
}

async function onPick(seat: string) {
  try {
    await api(`/api/showtimes/${showtimeId.value}/book/`, {
      method: "POST",
      body: JSON.stringify({ seat }),
    });
    await fetchSeats();
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Book thất bại";
    if (msg.includes("401") || msg.includes("Authentication") || msg.includes("credentials")) {
      router.push({ name: "login", query: { next: route.fullPath } });
      return;
    }
    error.value = msg;
  }
}

onMounted(() => {
  fetchSeats();
  pollId = setInterval(fetchSeats, POLL_MS);
});

onUnmounted(() => {
  if (pollId) clearInterval(pollId);
});
</script>

<template>
  <div class="wrap">
    <p><router-link to="/">← Danh sách phim</router-link></p>
    <header class="header">
      <h1 class="header__title">{{ title }}</h1>
      <p class="header__sub">{{ sub }}</p>
    </header>
    <p v-if="error" class="empty">{{ error }}</p>
    <div class="seat-grid">
      <SeatButton
        v-for="s in seats"
        :key="s.seat"
        :seat="s.seat"
        :status="s.status"
        @pick="onPick"
      />
    </div>
  </div>
</template>