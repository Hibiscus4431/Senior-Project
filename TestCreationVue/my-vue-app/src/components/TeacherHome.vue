<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherHome.vue -->
<template>
  <div class="teacher-home-container">
    <div class="center large-heading">
      <h1>Course Selection</h1>
    </div>
    <div class="center large-paragraph">
      Please select or create a course:
      <br>
      <br>
      <!-- Conditionally render the dropdown or the no courses message -->
      <div class="dropdown" v-if="courses.length">
        <button class="dropbtn">Select Course</button>
        <div class="dropdown-content">
          <router-link v-for="course in courses" :key="course.id"
            :to="{ name: 'TeacherQuestions', query: { courseId: course.id, courseTitle: course.title } }">
            {{ course.title }}
          </router-link>
        </div>
      </div>
      <div v-else>
        No courses available.
      </div>
      <!-- Button to create a new course will always be shown -->
      <router-link to="TeacherNewClass">
        <button class="t_button">Create New Course</button>
      </router-link>
    </div>
    <br>
  </div>
</template>


<script>
import api from '@/api'; // <-- your custom Axios instance with token handling
import jwtDecode from 'jwt-decode';
export default {
  name: 'TeacherHome',
  data() {
    return {
      courses: [],
      error: null,
    };
  },
  created () {
    this.fetchCourses();
  },
  methods: {
    async fetchCourses() {
      try {
        console.log('Fetching courses...'); // Debugging

        const response = await api.get('/courses', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        console.log('Courses fetched:', response.data); // Debugging
        if (response.data && response.data.courses) {
          this.courses = response.data.map(course => ({
            id: course.course_id,
            title: course.course_name
          }));
        } else {
          this.error = 'Failed to fetch course data.';
        }
      } catch (error) {
        console.error('Error fetching course:', error);

        // Check if error has a response from the backend
        if (error.response) {
          this.error = error.response.data.error || error.response.statusText;
        } else {
          this.error = 'Network error or server is not responding.';
        }
      }
    }
  }
};
</script>

<style scoped>
@import '../assets/teacher_styles.css';

.teacher-home-container {
  background-color: #43215a;
  font-family: Arial, sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>