<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherNewClass.vue -->
<template>
  <div class="teacher-newClass-container">
    <div class="center large-heading">
      <h1>Create New Class</h1>
    </div>
    <div class="center large-paragraph">
      <!-- form that redirects after clicking save -->
      <form @submit.prevent="saveCourse">
        <label for="courseTitle">Course Title:</label>
        <input type="text" id="courseTitle" v-model="courseTitle" style="height:20px"><br><br>

        <label for="courseNumber">Course Number:</label>
        <input type="text" id="courseNumber" v-model="courseNumber" style="height:20px"><br><br>

        <label for="textbookTitle">Textbook Title:</label>
        <select id="textbookTitle" v-model="textbookTitle" style="height:30px; width:200px" required>
          <option v-for="textbook in textbooks" :key="textbook.id" :value="textbook.id">
            {{ textbook.title }}
          </option>
        </select>
        <div v-if="!textbooks.length" style="color: red; margin-top: 10px;">
          No textbooks available.
        </div><br><br>

        <div class="center large-heading">
          <input type="submit" value="Save">
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import api from '@/api'

export default {
  name: 'TeacherNewClass',
  data() {
    return {
      courseTitle: '',
      courseNumber: '',
      textbookTitle: '',
      textbooks: [],
      error: null
    };
  },
  //created lifecycle hook to fetch textbooks when component is created
  //this will populate the dropdown menu with textbooks from the database
  created() {
    this.fetchTextbooks();
  },

  methods: {
    //function to populate textbooks to dropdown menu
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
  },



 async Course() {
    if (this.courseTitle && this.courseNumber && this.textbookTitle) {
      const courseData = {
        //replaced with titles of database fields
        course_name: this.courseTitle,
        course_number: this.courseNumber,
        textbook_id: this.textbookTitle
      };

      try {
        const response = await api.post('/courses', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        console.log('Course saved successfully:', response.data);
        alert('Course saved successfully!');
        this.$router.push({ path: 'TeacherQuestions' });
      } catch (error) {
        console.error('Error saving course:', error);
        alert('Failed to save the course. Please try again.');
      }
    } else {
      alert('Please fill out all fields.');
    }
  }
};
</script>

<style scoped>
@import '../assets/teacher_styles.css';

.teacher-newClass-container {
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