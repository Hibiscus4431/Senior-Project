<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherQuestions.vue -->
<template>
  <div class="teacher-questions-container">
    <div class="center large-heading sticky">
      <h1>{{ courseTitle }}</h1>
    </div>
    <div class="center large-paragraph">
      <!--Button to go to view test bank page-->
      <router-link to="/TeacherViewTB">
        <button class="t_button">View Test Banks</button>
      </router-link>
      <router-link to="/TeacherNewTB">
        <button class="t_button">New Test Bank</button>
      </router-link>
      <button class="t_button" @click="importTest">Import Test</button>
      <br>
      <div class="dropdown">
        <button class="dropbtn">Question Type</button>
        <div class="dropdown-content">
          <a href="#" @click="displayQuestionType('True/False')">True/False</a>
          <a href="#" @click="displayQuestionType('Multiple Choice')">Multiple Choice</a>
          <a href="#" @click="displayQuestionType('Matching')">Matching</a>
          <a href="#" @click="displayQuestionType('Fill in the Blank')">Fill in the Blank</a>
          <a href="#" @click="displayQuestionType('Short Answer')">Short Answer</a>
          <a href="#" @click="displayQuestionType('Essay')">Essay</a>
        </div>
      </div>
      <button class="t_button" @click="edit">New Question</button>
      <router-link to="/TeacherPubQ">
        <button class="t_button">Publisher Textbook Page</button>
      </router-link>
      <div id="selectedQuestionType" class="center large-paragraph">{{ selectedQuestionType }}</div>
    </div>
    <!--file input element -->
    <input type="file" id="fileInput" style="display: none;" @change="handleFileUpload">
    <!-- contents of popup-->
    <div class="form-popup" id="q_edit">
      <form class="form-container" @submit.prevent="handleQuestionSave">
        <h1>New Question</h1>
        <label for="ch"><b>Chapter Number</b></label><br>
        <input type="text" id="ch" v-model="chapter" required><br>

        <label for="sec"><b>Section Number</b></label><br>
        <input type="text" id="sec" v-model="section" required><br>

        <label for="question_t"><b>Question Type</b></label><br>
        <input type="text" id="question_t" v-model="question" required><br>


        <label for="question"><b>Question</b></label><br>
        <input type="text" id="question" v-model="question" required><br>

        <label for="ref"><b>Text Reference</b></label><br>
        <input type="text" id="ref" v-model="reference" required><br>

        <label for="ans"><b>Answer</b></label><br>
        <input type="text" id="ans" v-model="answer" required><br>

        <label for="ans_c"><b>Answer Choices</b></label><br>
        <input type="text" id="ans_c" v-model="answerChoices"><br>

        <label for="points"><b>Points Worth</b></label><br>
        <input type="text" id="points" v-model="points" required><br>

        <label for="time"><b>Est Time</b></label><br>
        <input type="text" id="time" v-model="time" required><br>

        <label for="ins"><b>Grading Instructions</b></label><br>
        <input type="text" id="ins" v-model="instructions" required><br>

        <label for="image"><b>Upload Image</b></label><br>
        <input type="file" id="image" @change="handleImageUpload" accept="image/*"><br>
        <img id="imagePreview" :src="imagePreview" alt="Image preview" v-if="imagePreview"
          style="max-width: 100%; max-height: 100%;"><br>
          
        <button type="submit" class="btn">Save</button>
        <button type="t_button" class="btn cancel" @click="closeForm">Close</button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TeacherQuestions',
  data() {
    return {
      courseTitle: this.$route.params.courseTitle || '',
      chapter: '',
      section: '',
      question: '',
      reference: '',
      answer: '',
      answerChoices: '',
      points: '',
      time: '',
      instructions: '',
      image: '',
      imagePreview: '',
      selectedQuestionType: ''
    };
  },
  methods: {
    importTest() {
      document.getElementById('fileInput').click();
    },
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        console.log('File selected:', file.name);
        // Code that connects file to the database will go here
      } else {
        console.error('No file selected.');
      }
    },
    handleQuestionSave() {
      const questionData = {
        chapter: this.chapter,
        section: this.section,
        question: this.question,
        reference: this.reference,
        answer: this.answer,
        answerChoices: this.answerChoices,
        points: this.points,
        time: this.time,
        instructions: this.instructions,
        image: this.image
      };

      localStorage.setItem('questionData', JSON.stringify(questionData));
      this.closeForm();
    },
    displayQuestionType(type) {
      this.selectedQuestionType = `Selected Question Type: ${type}`;
    },
    handleImageUpload(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.image = e.target.result;
          this.imagePreview = e.target.result;
        };
        reader.readAsDataURL(file);
      } else {
        console.error('No image selected.');
      }
    },
    edit() {
      document.getElementById('q_edit').style.display = 'block';
    },
    closeForm() {
      document.getElementById('q_edit').style.display = 'none';
    }
  }
};
</script>

<style scoped>
@import '../assets/teacher_styles.css';
.teacher-questions-container {
  background-color: #43215a;
  font-family: Arial, sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}


</style>