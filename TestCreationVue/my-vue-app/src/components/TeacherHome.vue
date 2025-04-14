<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherHome.vue -->
<template>
  <div class="theme-teacher">
    <div class="top-banner">
      <div class="banner-title">Course Selection</div>

      <div class="t_banner-actions">
        <router-link to="/" class="t_banner-btn">Log Out</router-link>
      </div>
    </div>
    <div class="center large-paragraph" style="color:#222">
      <div class="page-wrapper">
        Please select or create a course:

        <div class="button-row">
          <!-- Conditionally render the dropdown or the no courses message -->
          <div class="t_dropdown" v-if="courses.length">
            <button class="t_dropbtn">Select Course</button>
            <div class="t_dropdown-content">
              <!-- Display all course titles in the dropdown -->
              <a v-for="course in courses" :key="course.id" @click="selectCourse(course)">
                {{ course.title }}
              </a>
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
      </div>
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
  created() {
    this.fetchCourses();
  },
  methods: {
    // fetch courses from the database
    async fetchCourses() {
      try {
        console.log('Fetching courses...'); // Debugging

        const response = await api.get('/courses', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        console.log('Courses fetched:', response.data); // Debugging
        if (Array.isArray(response.data)) {
          this.courses = response.data.map(course => ({
            id: course.course_id,
            title: course.course_name,
            textbook_id: course.textbook_id
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
    },
    // Handle course selection
    selectCourse(course) {
      // Navigate to the TeacherQuestions page with the selected course's ID and title
      this.$router.push({
        name: 'TeacherQuestions',
        query: {
          courseId: course.id,
          courseTitle: course.title,
          textbook_id: course.textbook_id
        }
      });
    }
  }
};
</script>

<style scoped>
@import '../assets/teacher_styles.css';

</style>