<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/PubQuestions.vue -->
<template>
    <div class ="pub-questions-container">
      <div class="center large-heading sticky">
        <h1 id="textbook-title">{{ textbookTitle }}</h1>
      </div>
      <div class="center large-paragraph">
        <!--Button to go to view test bank page-->
        <router-link to="PubViewTB">
          <button class="button">View Test Banks</button>
        </router-link>
  
        <router-link to="PubNewTB">
          <button class="button">New Test Bank</button>
        </router-link>
        <button class="button" @click="edit">New Question</button>
        <br><br>
  
        Questions will be generated here
      </div>
  
      <!-- contents of popup-->
      <div class="form-popup" v-if="showForm">
        <form class="form-container" @submit.prevent="handleQuestionSave">
          <h1>New Question</h1>
  
          <label for="ch"><b>Chapter Number</b></label><br>
          <input type="text" id="ch" v-model="questionData.chapter" required><br>
  
          <label for="sec"><b>Section Number</b></label><br>
          <input type="text" id="sec" v-model="questionData.section" required><br>
  
          <label for="question"><b>Question</b></label><br>
          <input type="text" id="question" v-model="questionData.question" required><br>
  
          <label for="ref"><b>Text Reference</b></label><br>
          <input type="text" id="ref" v-model="questionData.reference" required><br>
  
          <label for="ans"><b>Answer</b></label><br>
          <input type="text" id="ans" v-model="questionData.answer" required><br>
  
          <label for="ans_c"><b>Answer Choices</b></label><br>
          <input type="text" id="ans_c" v-model="questionData.answerChoices"><br>
  
          <label for="points"><b>Points Worth</b></label><br>
          <input type="text" id="points" v-model="questionData.points" required><br>
  
          <label for="time"><b>Est Time</b></label><br>
          <input type="text" id="time" v-model="questionData.time" required><br>
  
          <label for="ins"><b>Grading Instructions</b></label><br>
          <input type="text" id="ins" v-model="questionData.instructions" required><br>
  
          <label for="image"><b>Upload Image</b></label><br>
          <input type="file" id="image" @change="handleImageUpload" accept="image/*"><br>
          <img id="imagePreview" :src="imagePreview" alt="Image preview" v-if="imagePreview" style="max-width: 100%; max-height: 100%;"><br>
  
          <button type="submit" class="btn">Save</button>
          <button type="button" class="btn cancel" @click="closeForm">Close</button>
        </form>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'PubQuestions',
    data() {
      return {
        textbookTitle: '',
        showForm: false,
        questionData: {
          chapter: '',
          section: '',
          question: '',
          reference: '',
          answer: '',
          answerChoices: '',
          points: '',
          time: '',
          instructions: '',
          image: ''
        },
        imagePreview: ''
      };
    },
    methods: {
      edit() {
        this.showForm = true;
      },
      closeForm() {
        this.showForm = false;
      },
      handleQuestionSave() {
        localStorage.setItem('questionData', JSON.stringify(this.questionData));
        this.closeForm();
      },
      handleImageUpload(event) {
        const file = event.target.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = (e) => {
            this.questionData.image = e.target.result;
            this.imagePreview = e.target.result;
          };
          reader.readAsDataURL(file);
        }
      }
    },
    mounted() {
      this.textbookTitle = localStorage.getItem('selectedTextbookTitle') || 'Book Title';
      
    }
  };
  </script>
  
  <style scoped>
  @import '../assets/publisher_styles.css';
  .pub-questions-container {
    background-color: #17552a;
    font-family: Arial, sans-serif;
    height: 100vh;
    height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  }
  </style>