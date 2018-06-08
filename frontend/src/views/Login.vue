<template>
  <div>
    <form>
      <div>
        <label>Login </label>
        <input v-model="username">
      </div>
      <div>
        <label>Password </label>
        <input v-model="password">
      </div>
      <div>
        <label>Repeat password </label>
        <input v-model="passwordRepeat">
      </div>
      <button @click="login()" type="submit">Login</button>
    </form>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch } from "vue-property-decorator";

@Component
export default class Login extends Vue {
  username: string = "";
  password: string = "";
  passwordRepeat: string = "";

  login() {
    const payload = {
      username: this.username,
      password: this.password
    };

    this.$http
      .post("login", payload)
      .then(response => response.json())
      .then(response => {
        localStorage.setItem("token", response.token);
        this.$router.push("/users");
      });
  }
}
</script>
