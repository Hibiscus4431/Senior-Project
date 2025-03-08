<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherHome.vue -->
<template>
    <div>
      <div class="center large-heading">
        <h1>Course Selection</h1>
      </div>
      <div class="center large-paragraph">
        Please select or create a course:
        <br>
        <br>
        <!--selecting a course will be a drop down menu with all previous courses-->
        <div class="dropdown" v-if="courses.length">
          <button class="dropbtn">Select Course</button>
          <div class="dropdown-content">
            <a v-for="course in courses" :key="course.id" href="#" @click="redirectToCourse('Teacher_question', course.title)">
              {{ course.title }}
            </a>
          </div>
        </div>
        <div v-else>
          No courses available.
        </div>
        <!--creating a new course will take user to new page-->
        <router-link to="Teacher_newclass">
          <button class="button">Create New Course</button>
        </router-link>
      </div>
      <br>
    </div>
  </template>
  
  <script>
  export default {
    name: 'TeacherHome',
    data() {
      return {
        courses: []
      };
    },
    created() {
      this.fetchCourses();
    },
    methods: {
      fetchCourses() {
        // Simulate an API call to fetch courses
        this.courses = [
          { id: 1, title: 'Course 1' },
          { id: 2, title: 'Course 2' },
          { id: 3, title: 'Course 3' }
        ];
      },
      redirectToCourse(course, courseTitle) {
        localStorage.setItem('selectedCourseTitle', courseTitle);
        this.$router.push({ path: `${course}.html` });
      }
    }
  };
  </script>
  
  
  <style scoped>
  @import '../assets/teacher_styles.css';
  </style>