<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/PubLog.vue -->
<template>
  <div class="theme-publisher">
  <div class="top-banner">
  <div class="banner-title">Publisher Login</div>
</div>
    <!-- This is the page where publishers log in-->
    <div class="center large-paragraph" style ="color: #222">
      Please enter your publisher username and password:
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
import jwtDecode from 'jwt-decode';

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

        if (decoded.exp > currentTime && decoded.role === 'publisher') {
          this.$router.push('/PubHome');
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
    if (role === 'publisher') {
      this.$router.push('/PubHome');
    } else {
      this.errorMessage = "Only publishers can log in here.";
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
@import '../assets/publisher_styles.css';

.pub-log-container {
  background-color: #17552a;
  font-family: Arial, sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Larger submit button */
input[type="submit"] {
  background-color: rgb(48, 191, 223);
  color: black;
  font-size: 20px;
  padding: 10px 20px;
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