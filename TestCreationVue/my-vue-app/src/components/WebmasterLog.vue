<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/WebmasterLog.vue -->
<template>
  <div class="webmaster-log-container">
    <div class="center large-heading">
      <h1>Webmaster Login</h1>
    </div>

    <div class="center large-paragraph">
      Please enter your webmaster username and password:
      <br>
      <br>
      <form @submit.prevent="submitForm">
        <!-- create username text box-->
        <label for="uname">Username:</label><br>
        <input type="text" id="uname" v-model="username"><br>
        <br>
        <!-- create password textbox-->
        <label for="pass">Password:</label><br>
        <input type="password" id="pass" v-model="password"><br><br>
        <!-- submit button, when pressed it takes user to url specified-->
        <input type="submit" value="Submit">
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      username: '',
      password: ''
    };
  },
  methods: {
    async submitForm() {
      try {
        const response = await axios.post('http://localhost:5000/login', {
          username: this.username,
          password: this.password
        });
        console.log(response.data);
        if (response.data.message === "Login successful") {
          // Store the token in localStorage or Vuex
          localStorage.setItem('token', response.data.token);
          // Redirect to Webmaster home page
          this.$router.push('/WebmasterHome');
        } else {
          alert("Invalid username or password");
        }
      } catch (error) {
        console.error(error);
        alert("An error occurred during login");
      }
    }
  }
};
</script>

<style scoped>
@import '../assets/webmaster_styles.css';

.webmaster-log-container {
  background-color: #082e75;
  font-family: Arial, sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>