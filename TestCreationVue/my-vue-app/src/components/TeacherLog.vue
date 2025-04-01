<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherLog.vue -->

<template>
  <div class="teacher-log-container">
    <div class="center large-heading">
      <h1>Teacher Login</h1>
    </div>

    <div class="center large-paragraph">
      Please enter your teacher username and password:
      <br />
      <br />
      <form @submit.prevent="submitForm">
        <!-- create username text box-->
        <label for="uname">Username:</label><br />
        <input type="text" id="uname" v-model="username" /><br />
        <br />
        <!-- create password textbox-->
        <label for="pass">Password:</label><br />
        <input type="password" id="pass" v-model="password" /><br /><br />
        <!-- submit button, when pressed it takes user to url specified-->
        <input type="submit" value="Submit" :disabled="loading" />
      </form>

      <!-- Show error message if user and password are entered incorrectly -->
      <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
      
      <!-- Show loading spinner if the form is submitting -->
      <div v-if="loading" class="loading-message">Logging in...</div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';


export default {
  data() {
    return {
      username: '',
      password: '',
      errorMessage: '',
      loading: false
    };
  },
  mounted() {
    // Check if token exists and is valid
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const decodedToken = jwtDecode(token);
        const currentTime = Date.now() / 1000;
        if (decodedToken.exp < currentTime) {
          // Token expired
          localStorage.removeItem('token');
          this.$router.push('/login');
        }
      } catch (error) {
        console.error('Invalid token', error);
      }
    }
  },
  methods: {
    async submitForm() {
      if (!this.username || !this.password) {
        this.errorMessage = "Please enter both username and password.";
        return;
      }

      this.loading = true; // Show loading spinner

      try {
        const response = await axios.post(
          'http://localhost:5000/auth/login',
          {
            username: this.username,
            password: this.password
          },
          {
            headers: {
              'Content-Type': 'application/json'
            }
          }
        );

        this.loading = false; // Hide loading spinner

        if (response.data.message === "Login successful") {
          // Save token to localStorage
          localStorage.setItem('token', response.data.token);
          this.$router.push('/TeacherHome'); // Redirect to TeacherHome page
        } else {
          this.errorMessage = "Invalid username or password";
        }
      } catch (error) {
        this.loading = false; // Hide loading spinner
        if (error.response && error.response.status === 401) {
          this.errorMessage = "Invalid username or password"; // Better error message for 401
        } else {
          this.errorMessage = "An error occurred during login";
        }
      }
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
  justify-content: center;
  align-items: center;
}

.error-message {
  color: rgb(174, 38, 38);
  margin-top: 10px;
}

.loading-message {
  color: #ffffff;
  margin-top: 10px;
}

input[type="submit"] {
  background-color: rgb(84, 178, 150);
  color: black;
  font-size: 20px;
  padding: 10px 20px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

input[type="submit"]:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

input[type="text"], input[type="password"] {
  padding: 10px;
  font-size: 16px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.center {
  text-align: center;
}

.large-heading {
  font-size: 2em;
}

.large-paragraph {
  font-size: 1.2em;
}
</style>
