<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/WebmasterLog.vue -->
<template>
    <div class = "webmaster-log-container">
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
  export default {
    data() {
      return {
        username: '',
        password: ''
      };
    },
    methods: {
      submitForm() {
        // Handle form submission
        console.log('Username:', this.username);
        console.log('Password:', this.password);
        // Redirect to Webmaster home page
        this.$router.push ('/WebmasterHome');
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
    height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
  </style>