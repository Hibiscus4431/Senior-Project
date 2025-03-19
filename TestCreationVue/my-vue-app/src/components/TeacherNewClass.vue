<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherNewClass.vue -->
<template>
  <div class = "teacher-newClass-container">
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
        <input type="text" id="textbookTitle" v-model="textbookTitle" style="height:20px"><br><br>

        <label for="author">Author:</label>
        <input type="text" id="author" v-model="author" style="height:20px"><br><br>

        <label for="ISBN">ISBN:</label>
        <input type="text" id="ISBN" v-model="ISBN" style="height:20px"><br><br>

        <label for="version">Version:</label>
        <input type="text" id="version" v-model="version" style="height:20px"><br><br>

        <label for="websiteLink">Website Link:</label>
        <input type="text" id="websiteLink" v-model="websiteLink" style="height:20px"><br><br>

        <div class="center large-heading">
          <input type="submit" value="Save">
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TeacherNewClass',
  data() {
    return {
      courseTitle: '',
      courseNumber: '',
      textbookTitle: '',
      author: '',
      ISBN: '',
      version: '',
      websiteLink: ''
    };
  },
  methods: {
    saveCourse() {
      if (this.courseTitle && this.courseNumber && this.textbookTitle && this.author && this.ISBN && this.version && this.websiteLink) {
        const courseData = {
          courseTitle: this.courseTitle,
          courseNumber: this.courseNumber,
          textbookTitle: this.textbookTitle,
          author: this.author,
          ISBN: this.ISBN,
          version: this.version,
          websiteLink: this.websiteLink
        };

        try {
          localStorage.setItem('courseData', JSON.stringify(courseData));
          localStorage.setItem('selectedCourseTitle', this.courseTitle); // Store the course title separately
          this.$router.push({ path: 'TeacherQuestions' });
        } catch (error) {
          console.error('Error saving course data:', error);
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
.teacher-newClass-container {
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