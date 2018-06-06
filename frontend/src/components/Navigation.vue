<template>
  <div>
      <router-link to="/">Home</router-link> |
      <router-link to="/about">About</router-link> |
      <router-link to="/users">Users</router-link> |
      <router-link to="/todo">Todo</router-link> |
      <router-link to="/login">Login</router-link> |
      <a @click="logout()">Logout</a> 
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';

@Component
export default class Navigation extends Vue {

  logout() {
    localStorage.removeItem("token");
    this.$router.push("/login");
  }
}
</script>
