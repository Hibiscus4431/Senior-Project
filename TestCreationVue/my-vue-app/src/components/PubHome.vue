<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/PubHome.vue -->
<template>
 <div class="theme-publisher">
  <div class="top-banner">
  <div class="banner-title">Textbook Selection</div>

  <div class="banner-actions">
    <router-link to="/" class="p_banner-btn">Log Out</router-link>
  </div>
</div>
    <div class="center large-paragraph" style = "color:#222">
      <div class="page-wrapper">

      Please select or add a textbook:

      <div class="button-row">
      <!--selecting a course will be a drop down menu with all previous courses-->
      <!--If else that ensures there are courses to select from-->
      <div class="p_dropdown" v-if="textbooks.length">
        <button class="p_dropbtn">Select Textbook</button>
        <div class="p_dropdown-content">
          <router-link v-for="textbook in textbooks" :key="textbook.id"
          :to="{ path: 'PubQuestions', query: { title: textbook.title, textbook_id: textbook.id } }">
            {{ textbook.title }}
          </router-link>
        </div>
      </div>
      <div v-else>
        No courses available.
      </div>
      <!--creating a new course will take user to new page-->
      <router-link to="PubNewBook">
        <button class="p_button">Add New Textbook</button>
      </router-link>
      <br>
    </div>
  </div>
  </div>
  </div>
</template>

<script>
import api from '@/api'; // <-- your custom Axios instance with token handling
import jwtDecode from 'jwt-decode';
export default {
  name: 'PublisherHome',
  data() {
    return {
      textbooks: [],
      error: null,
    };
  },
  created() {
    this.fetchTextbooks();
  },
  methods: {
    async fetchTextbooks() {
      try {
        console.log('Fetching textbooks...'); // Debugging

        const response = await api.get('/textbooks', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        console.log('Textbooks fetched:', response.data); // Debugging

        if (response.data && response.data.textbooks) {
          this.textbooks = response.data.textbooks;
        } else {
          this.error = 'Failed to fetch textbooks data.';
        }
      } catch (error) {
        console.error('Error fetching textbooks:', error);

        // Check if error has a response from the backend
        if (error.response) {
          this.error = `Error: ${error.response.status} - ${error.response.data.message || error.response.statusText}`;
        } else {
          this.error = 'Network error or server is not responding.';
        }
      }
    }
  }
};
</script>

<style scoped>
@import '../assets/publisher_styles.css';

.pub-home-container {
  background-color: #17552a;
  font-family: Arial, sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.dropbtn {
  background-color: rgb(48, 191, 223);
  color: black;
  padding: 10px;
  font-size: 20px;
  border: none;
}

.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-content {
  display: none;
  position: absolute;
  background-color: #f1f1f1;
  min-width: 160px;
  box-shadow: 0px 8px 16px 0px rgba(0, 0, 0, 0.2);
  z-index: 1;
}

.dropdown-content a {
  color: black;
  padding: 10px 15px;
  text-decoration: none;
  display: block;
}

.dropdown-content a:hover {
  background-color: rgb(48, 191, 223);
}

.dropdown:hover .dropdown-content {
  display: block;
}

.dropdown:hover .dropbtn {
  background-color: rgb(40, 151, 176);
}
</style>