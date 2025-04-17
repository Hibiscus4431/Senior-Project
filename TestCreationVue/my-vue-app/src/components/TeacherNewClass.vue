<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherNewClass.vue -->
<template>
  <div class="theme-teacher">
  <div class="top-banner">
  <div class="banner-title">Create New Class</div>

  <div class="t_banner-actions">
    <router-link to="/TeacherHome" class="t_banner-btn">Home</router-link>
    <router-link to="/" class="t_banner-btn">Log Out</router-link>
  </div>
</div>
    <div class="center large-paragraph" style = "color:#222">
      <!-- form that redirects after clicking save -->
      <form @submit.prevent="saveCourse">
        <label for="courseTitle">Course Title:</label>
        <input type="text" id="courseTitle" v-model="courseTitle" style="height:20px"><br>

        <label for="courseNumber">Course Number:</label>
        <input type="text" id="courseNumber" v-model="courseNumber" style="height:20px"><br>

        <label for="textbookTitle">Textbook Title:</label>
        <select id="textbookTitle" v-model="selectedTextbookId" style="height:50px; width:200px" required>
          <option v-for="textbook in textbooks" :key="textbook.id" :value="textbook.id">
            {{ textbook.title }}
          </option>
        </select>
        <div v-if="!textbooks.length" style="color: red; margin-top: 10px;">
          No textbooks available.
        </div><br>

        <div class="center large-heading">
          <input type="submit" value="Save">
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import api from '@/api';

export default {
  name: 'TeacherNewClass',
  data() {
    return {
      courseTitle: '',
      courseNumber: '',
      selectedTextbookId: null, // Stores the selected textbook's ID
      textbooks: [], // Array to store textbook data
      error: null
    };
  },
  created() {
    this.fetchTextbooks(); // Fetch textbooks when the component is created
  },

  methods: {
    // Method to fetch textbooks from the database
    async fetchTextbooks() {
      try {
        console.log('Fetching textbooks...'); // Debugging

        const response = await api.get('/textbooks/all', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        console.log('Textbooks fetched:', response.data); // Debugging

        if (response.data && response.data.textbooks) {
          this.textbooks = response.data.textbooks; // Populate the textbooks array
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
    },

    // Method to select a textbook from the dropdown
    selectTextbook(textbook) {
      this.selectedTextbookId = textbook.id;
      this.selectedTextbookTitle = textbook.title;
    },

    // Method to save the course to the database
    async saveCourse() {
      if (this.courseTitle && this.courseNumber && this.selectedTextbookId) {
        const courseData = {
          course_name: this.courseTitle,
          course_number: this.courseNumber,
          textbook_id: this.selectedTextbookId // Only send the textbook_id
        };

        try {
          const response = await api.post('/courses', courseData, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`
            }
          });
          console.log('Course saved successfully:', response.data);
          this.$router.push({ path: '/TeacherHome' });
        } catch (error) {
          console.error('Error saving course:', error);
        }
      }
    }
  }
};
</script>

<style scoped>
@import '../assets/teacher_styles.css';

select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;

  background-color: #e9dbf7; /* Light green, feel free to change */
  border: 2px solid #cda9f1;
  color: #222;
  padding: 10px 14px;
  font-size: 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: border-color 0.3s ease;
  width: 250px;
}

select:focus {
  outline: none;
  border-color: #cda9f1;
}

select:hover {
  border-color: #b985ec;
}

/* Optional: style the label to match */
label {
  font-weight: bold;
  font-size: 20px;
  margin-bottom: 8px;
  display: block;
}

</style>