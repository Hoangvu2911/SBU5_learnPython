<script setup lang="ts">
import type { SeatStatus } from "@/api/type";

const props = defineProps<{
  seat: string;
  status: SeatStatus;
}>();

const emit = defineEmits<{
  pick: [seat: string];
}>();

function onClick() {
  if (props.status === "available") emit("pick", props.seat);
}
</script>

<template>
  <button
    v-if="status === 'available'"
    type="button"
    class="seat-grid__btn"
    @click="onClick"
  >
    {{ seat }}
  </button>
  <span
    v-else
    :class="status === 'held' ? 'seat-held' : 'seat-booked'"
  >
    {{ seat }}
  </span>
</template>