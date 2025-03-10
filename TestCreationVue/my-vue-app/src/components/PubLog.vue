<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/PubLog.vue -->
<template>
  <div>
    <div class="center large-heading">
      <h1>Publisher Login</h1>
    </div>
    <!-- This is the page where publishers log in-->
    <div class="center large-paragraph">
      Please enter your publisher username and password:
      <br>
      <br>
      <form @submit.prevent="submitForm">
        <!-- create username text box-->
        <label for="uname">Username:</label><br>
        <input type="text" id="uname" v-model="username" style="height: 20px;"><br>
        <!-- create password textbox-->
        <br>
        <label for="pass">Password:</label><br>
        <input type="password" id="pass" v-model="password" style="height: 20px;"><br><br>
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
  name: 'PublisherLogin',
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
@import '../assets/publisher_styles.css';
</style>