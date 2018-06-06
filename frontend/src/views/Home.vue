<template>
  <div class="home">
    <!-- <img src="../assets/logo.png"> -->
    <!-- <HelloWorld msg="Welcome to Your Vue.js + TypeScript App"/> -->
    <h2>Send email</h2>
    <h3>{{ message.message }}</h3>
    <form>
      <input name="email" v-model="email">
      <button @click="sendEmail()" type="submit">Send</button>
    </form>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import HelloWorld from '@/components/HelloWorld.vue'; // @ is an alias to /src

@Component({
  components: {
    HelloWorld,
  },
})
export default class Home extends Vue {

  email = "";
  message = "";

  sendEmail() {
    this.$http.post("send_email", {email: this.email}).then(response => response.json()).then(response => this.message = response)
  }
  
}
</script>
