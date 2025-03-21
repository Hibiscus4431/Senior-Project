<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherPubTB.vue -->
<template>
    <div class = "teacher-pubTB-container">
      <div class="center large-heading">
        <h1>Testbank Name</h1>
      </div>
      <div class="center large-paragraph">
        <button class="t_button" @click="edit">Rate Textbook</button>
        <br>
        <hr>
        Questions are generated here<br>
        <button class="t_button" @click="edit">Rate Question</button>
      </div>
  
      <!-- contents of popup-->
      <div class="form-popup" v-if="showRating">
        <form class="form-container" @submit.prevent="saveRating">
          <h1>Rating</h1>
          <label for="star"><b>Enter whole number 1-5</b></label><br>
          <input type="number" v-model.number="rating.star" min="1" max="5" required><br>
  
          <label for="comm"><b>Enter Comment</b></label><br>
          <input type="text" v-model="rating.comment" required><br>
  
          <button type="submit" class="btn">Save</button>
          <button type="t_button" class="btn cancel" @click="closeForm">Close</button>
        </form>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'TeacherPubTB',
    data() {
      return {
        showRating: false,
        rating: {
          star: '',
          comment: ''
        }
      };
    },
    methods: {
      edit() {
        this.showRating = true;
      },
      closeForm() {
        this.showRating = false;
      },
      saveRating() {
        // Handle the rating save logic here
        console.log('Rating saved:', this.rating);
        this.closeForm();
      }
    }
  };
  </script>
  
  <style scoped>
  @import '../assets/teacher_styles.css';
  .teacher-pubTB-container {
  background-color: #43215a;
  font-family: Arial, sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}
  </style>