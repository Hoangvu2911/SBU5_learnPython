<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const username = ref("");
const password = ref("");
const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const error = ref("");

async function submit() {
  try {
    error.value = "";
    await auth.login(username.value, password.value);
    const next = typeof route.query.next === "string" ? route.query.next : "/";
    await router.replace(next);
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Login thất bại";
  }
}
</script>

<template>
  <div class="wrap">
    <h1>Đăng nhập</h1>
    <form @submit.prevent="submit">
      <input type="text" v-model="username" placeholder="Tên đăng nhập" required>
      <input type="password" v-model="password" placeholder="Mật khẩu" required>
      <button type="submit">Đăng nhập</button>
    </form>
  </div>
</template>