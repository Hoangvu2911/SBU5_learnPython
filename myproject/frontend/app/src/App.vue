<script setup lang="ts">
import { useAuthStore } from "@/stores/auth";
const auth = useAuthStore();
</script>

<template>
  <header class="wrap">
    <router-link to="/">Cinema</router-link>
    <nav>
      <template v-if="auth.isLoggedIn">
        <span>{{ auth.user?.username }}</span>
        <router-link to="/tickets">Vé của tôi</router-link>
        <router-link v-if="auth.isStaff" to="/manage">Manage</router-link>
        <button type="button" @click="auth.logout()">Logout</button>
      </template>
      <router-link v-else to="/login">Đăng nhập</router-link>
    </nav>
  </header>
  <router-view />
</template>