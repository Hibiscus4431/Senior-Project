<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherLog.vue -->

<template>
    <div class = "teacher-log-container">
      <div class="center large-heading">
        <h1>Teacher Login</h1>
      </div>
  
      <div class="center large-paragraph">
        Please enter your teacher username and password:
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
        <!--Show error message if user and password are entered incorrectly-->
        <div v-if="errorMessage" class="error-message">{{ errorMessage }}
        </div>
      </div>
    </div>
  </template>
  
  <script>
export default {
  data() {
    return {
      username: '',
      password: '',
      errorMessage: ''
    };
  },
  methods: {
    submitForm() {
      if (this.username === '' || this.password === '') {
        this.errorMessage = 'Username and password are required.';
        return;
      }

      // Handle form submission
      // Simulate an API call for login
      this.login(this.username, this.password)
        .then(() => {
          // Redirect to Teacher home page
          this.$router.push('/TeacherHome');
        })
        .catch((error) => {
          this.errorMessage = 'Invalid username or password.';
        });
    },
    login(username, password) {
      // Simulate an API call with a promise
      return new Promise((resolve, reject) => {
        if (username === 'teacher' && password === 'password') {
          resolve();
        } else {
          reject();
        }
      });
    }
  }
};
</script>

<style scoped>
@import '../assets/teacher_styles.css';

.teacher-log-container {
  background-color: #43215a;
  font-family: Arial, sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.error-message {
  color: red;
  margin-top: 10px;
}

input[type="submit"] {
  background-color: rgb(84, 178, 150);
  color: black;
  font-size: 20px;
  padding: 10px 20px;
}
</style>