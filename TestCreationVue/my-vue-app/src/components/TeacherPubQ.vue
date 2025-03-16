<!-- filepath: c:\Users\laure\Senior-Project\TestCreationVue\my-vue-app\src\components\TeacherPubQ.vue -->
<template>
  <div class = "teacher-PubQ-container">
    <div class="center large-heading">
      <h1>Testbank Selection</h1>
    </div>
    <div class="center large-paragraph">
      Please select a Publisher Testbank to view:
      <br>
      <br>
      <!--selecting a testbank to view-->
      <div class="dropdown">
        <button class="dropbtn" @click="toggleDropdown">Testbank</button>
        <div class="dropdown-content" v-if="dropdownOpen">
          <a href="#" v-for="course in courses" :key="course" @click="selectCourse(course)">{{ course }}</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TeacherPubQ',
  data() {
    return {
      courses: ['Course 1', 'Course 2', 'Course 3'],
      dropdownOpen: false
    };
  },
  methods: {
    toggleDropdown() {
      this.dropdownOpen = !this.dropdownOpen;
    },
    selectCourse(course) {
      console.log(`Selected course: ${course}`);
      this.dropdownOpen = false;
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
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
</style>