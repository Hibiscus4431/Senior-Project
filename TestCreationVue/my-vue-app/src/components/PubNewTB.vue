<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/PubNewTB.vue -->
<template>
    <div class = "pub-newTB-container">
      <div class="center large-heading sticky">
        <h1>Create New Test Bank</h1>
      </div>
      <div class="center large-paragraph">
        <!-- This is the page where the publisher can create a new test bank-->
        <form @submit.prevent="handleSubmit">
          <!-- create TB Name text box-->
          <label for="bankName">Name of Test Bank:</label>
          <input type="text" id="bankName" v-model="bankName" style="height: 20px;"><br>
          <br>
  
          <!-- create Chapter text box-->
          <label for="bankCh">Textbook Chapter:</label>
          <input type="text" id="bankCh" v-model="bankChapter" style="height: 20px;"><br>
          <br>
  
          <!-- create section text box-->
          <label for="bankSec">Textbook Section:</label>
          <input type="text" id="bankSec" v-model="bankSection" style="height: 20px;"><br>
          <br>
  
          <!-- submit button, when pressed it takes user to url specified-->
          <input type="submit" value="Submit">
        </form>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'PublisherNewTB',
    data() {
      return {
        bankName: '',
        bankChapter: '',
        bankSection: ''
      };
    },
    methods: {
      handleSubmit() {
        if (this.bankName && this.bankChapter && this.bankSection) {
          try {
            // Save the values to local storage
            localStorage.setItem('bankName', this.bankName);
            localStorage.setItem('bankChapter', this.bankChapter);
            localStorage.setItem('bankSection', this.bankSection);
  
            // Redirect to the next page
            this.$router.push({ path: 'TeacherViewTB' });
          } catch (error) {
            console.error('Error saving test bank data:', error);
          }
        } else {
          alert('Please fill out all fields.');
        }
      }
    }
  };
  </script>
  
  <style scoped>
  @import '../assets/publisher_styles.css';
  .pub-newTB-container {
    background-color: #17552a;
    font-family: Arial, sans-serif;
    height: 100vh;
  display: flex;
  flex-direction: column;
  }
    /* Larger submit button */
input[type="submit"] {
  background-color: rgb(48, 191, 223);
  color: black;
  font-size: 20px;
  padding: 10px 20px;
}
  </style>