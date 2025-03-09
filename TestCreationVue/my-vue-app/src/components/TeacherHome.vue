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
      <!--If else that ensures there are courses to select from-->
      <div class="dropdown" v-if="courses.length">
        <button class="dropbtn">Select Course</button>
        <div class="dropdown-content">
          <router-link v-for="course in courses" :key="course.id" :to="{ path: 'TeacherQuestions', query: { title: course.title } }">
            {{ course.title }}
          </router-link>
        </div>
      </div>
      <div v-else>
        No courses available.
      </div>
      <!--creating a new course will take user to new page-->
      <router-link to="TeacherNewClass">
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
    }
  }
};
</script>

<style scoped>
@import '../assets/teacher_styles.css';
</style>