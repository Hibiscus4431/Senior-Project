<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/PubHome.vue -->
<template>
  <div class = "pub-home-container">
    <div class="center large-heading">
      <h1>Textbook Selection</h1>
    </div>
    <div class="center large-paragraph">
      Please select or add a textbook:
      <br>
      <br>
      <!--selecting a course will be a drop down menu with all previous courses-->
      <!--If else that ensures there are courses to select from-->
        <div class="dropdown" v-if="textbooks.length">
        <button class="dropbtn">Select Course</button>
        <div class="dropdown-content">
          <router-link v-for="textbook in textbooks" :key="textbook.id" :to="{ path: 'PubQuestions', query: { title: textbook.title } }">
            {{ textbook.title }}
          </router-link>
        </div>
      </div>
      <div v-else>
        No courses available.
      </div>
      <!--creating a new course will take user to new page-->
      <router-link to="PubNewBook">
        <button class="button">Add New Textbook</button>
      </router-link>
      <br>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PublisherHome',
  data() {
    return {
      textbooks: []
    };
  },
  created() {
    this.fetchTextbooks();
  },
  methods: {
    fetchTextbooks() {
      // Simulate an API call to fetch courses
      this.textbooks = [
        { id: 1, title: 'Textbook 1' },
        { id: 2, title: 'Textbook 2' },
        { id: 3, title: 'Textbook 3' }
      ];
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
    height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  }
</style>