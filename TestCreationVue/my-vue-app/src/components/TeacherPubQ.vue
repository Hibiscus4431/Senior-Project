<!-- filepath: c:\Users\laure\Senior-Project\TestCreationVue\my-vue-app\src\components\TeacherPubQ.vue -->
<template>
  <div class="teacher-PubQ-container">
    <div class="center large-heading">
      <h1>Testbank Selection</h1>
    </div>
    <div class="center large-paragraph">
      Please select an option to view:
      <br><br>

      <button class="t_button" @click="viewPublishedTests">Published Tests</button>
      <br><br>
      <button class="t_button" @click="viewPublisherQuestions">Publisher Testbank Questions</button>
    </div>

    
  </div>
</template>


<script>
import api from '@/api';

export default {
  name: 'TeacherPubQ',
  data() {
    return {
      publishedTests: [],
      viewing: '', // 'published' or 'publisher'
    };
  },
  methods: {
    async viewPublishedTests() {
      // REPLACE THIS
      //
      // this.viewing = 'published';
      // console.log('Published questions view triggered');
      // console.log('viewing =', this.viewing);
      // try {
      //   const response = await api.get('/get_tests', {
      //     headers: {
      //       Authorization: `Bearer ${localStorage.getItem('token')}`
      //     }
      //   });
      //   this.publishedTests = response.data.tests || [];
      // } catch (error) {
      //   console.error('Error fetching published tests:', error);
      //   alert('Failed to load published tests.');
      // }
    },

    viewPublisherQuestions() {
      // REPLACE THIS
      //
      // this.viewing = 'publisher';
      // console.log('viewing =', this.viewing);
      // // Add fetch call here when your publisher questions endpoint is ready
      // console.log('Publisher questions view triggered');
    }
  }
};
</script>


<style scoped>
@import '../assets/teacher_styles.css';
.teacher-PubQ-container {
  background-color: #43215a;
  font-family: Arial, sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>