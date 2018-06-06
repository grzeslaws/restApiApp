<template>
  <div>
    <table border=1>
      <tr>
        <td>name</td>
        <td>public_id</td>
        <td>admin</td>
      </tr>
      <tr v-for="user in users">
        <td>{{ user.username }}</td>
        <td>{{ user.public_id }}</td>
        <td>{{ user.admin}}</td>
      </tr>
    </table>
    <form>
      <div>
        <label>user name </label>
        <input v-model="username">
      </div>
      <div>
        <label>password </label>
        <input v-model="password">
      </div>
      <div>
        <label>admin </label>
        <input type="checkbox" v-model="admin">
      </div>
      <button type="submit" @click="createUse()">Create User</button>
    </form>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import userService from "@/services/UserService.vue";
import { log } from 'util';

@Component
export default class Users extends Vue {
  users: string[] = [];
  username = "";
  password = "";
  admin = false;

  created() {
    this.getUsers();
  }

  getUsers() {
    userService.getUsers()
      .then(response => {
        this.users = [...response.users];
      })
  }

  createUse() {
    const payload = {
     username: this.username,
     password: this.password,
     admin: this.admin 
    }

    this.$http.post("user", payload)
      .then(console.log);
  }
}
</script>
