<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherNewTB.vue -->
<template>
  <div class="theme-teacher">
    <div class="top-banner">
      <div class="banner-title">Create New Draft Pool</div>

      <div class="t_banner-actions">
        <router-link to="/TeacherHome" class="t_banner-btn">Home</router-link>
        <router-link to="/" class="t_banner-btn">Log Out</router-link>
      </div>
    </div>
    <div class="center large-paragraph" style="color:#222">
      <!-- This is the page where the teacher can create a new test bank-->
      <form @submit.prevent="saveTestBank">
        <!-- create TB Name text box-->
        <label for="bankName">Name of Draft Pool:</label>
        <input type="text" id="bankName" v-model="bankName" style="height: 20px;"><br>
        <br>

        <!-- create Chapter text box-->
        <label for="bankCh">Textbook Chapter:</label>
        <input type="text" id="bankCh" v-model="bankChapter" style="height: 20px;"><br>
        <br>

        <!-- create section text box-->
        <label for="bankSec">Textbook Section:</label>
        <input type="text" id="bankSec" v-model="bankSection" style="height: 20px;"><br>
        <br>

        <!-- submit button, when pressed it takes user to url specified-->
        <input type="submit" value="Submit">
      </form>
    </div>
  </div>
</template>

<script>
import api from '@/api';

export default {
  name: 'TeacherNewTB',
  data() {
    return {
      courseId: this.$route.query.courseId || '',
      courseTitle: this.$route.query.courseTitle || '',
      bankName: '',
      bankChapter: '',
      bankSection: ''
    };
  },
  methods: {
    async saveTestBank() {
      if (this.bankName && this.bankChapter && this.bankSection && this.courseId) {
        const testBankData = {
          testbank_name: this.bankName,
          chapter_number: this.bankChapter,
          section_number: this.bankSection,
          course_id: this.courseId
        };

        try {
          const response = await api.post('/testbanks/teacher', testBankData, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`
            }
          });
          console.log('Test bank saved successfully:', response.data);
          alert('Test bank saved successfully!');
          this.$router.push({ path: '/TeacherQuestions', query: { courseTitle: this.courseTitle, courseId: this.courseId } });

        } catch (error) {
          console.error('Error saving test bank:', error);
          alert('Failed to save the test bank. Please try again.');
        }
      } else {
        alert('Please fill out all fields.');
      }
    }
  }
};
</script>

<style scoped>
@import '../assets/teacher_styles.css';

.teacher-newTB-container {
  background-color: #43215a;
  font-family: Arial, sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

input[type="submit"] {
  background-color: rgb(84, 178, 150);
  color: black;
  font-size: 20px;
  padding: 10px 20px;
}
</style>