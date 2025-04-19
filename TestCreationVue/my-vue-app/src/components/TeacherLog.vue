<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherLog.vue -->

<template>
  <div class="theme-teacher">
    <div class="top-banner">
      <div class="banner-title">Teacher Login</div>
    </div>

    <div class="center large-paragraph" style="color: #222">
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
import api from '@/api'; // <-- your custom Axios instance with token handling
import { default as jwtDecode } from 'jwt-decode';

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
    // Optional: Check if token exists and redirect if still valid
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const decoded = jwtDecode(token);
        const currentTime = Date.now() / 1000;
        console.log('Decoded token:', decoded);


        if (decoded.exp > currentTime && decoded.role === 'teacher') {
          this.$router.push('/TeacherHome');
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

      if (this.username.trim().length < 3 || this.password.trim().length < 6) {
        this.errorMessage = "Username must be at least 3 characters and password at least 6 characters.";
        return;
      }

      this.loading = true;
      this.errorMessage = "";

      try {
        const res = await api.post('/auth/login', {
          username: this.username.toLowerCase(),
          password: this.password
        });

        const { token, user_id, role } = res.data;

        // Store token and identity in localStorage
        localStorage.setItem('token', token);
        localStorage.setItem('user_id', user_id);
        localStorage.setItem('role', role);

        // Redirect based on role
        if (role === 'teacher') {
          this.$router.push('/TeacherHome');
        } else {
          this.errorMessage = "Only teachers can log in here.";
          localStorage.clear(); // Clear stored data for non-teachers
        }
      } catch (error) {
        if (!error.response) {
          this.errorMessage = "Network error. Please check your connection.";
        } else if (error.response.status === 401) {
          this.errorMessage = "Invalid username or password.";
        } else {
          this.errorMessage = (error.response && error.response.data && error.response.data.message) || "An error occurred during login.";
        }
      } finally {
        this.loading = false;
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
</style>
