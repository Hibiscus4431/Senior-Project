<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/PubNewBook.vue -->
<template>
    <div class = "pub-newBook-container">
      <div class="center large-heading">
        <h1>Add New Textbook</h1>
      </div>
      <div class="center large-paragraph">
        <form @submit.prevent="saveBook">
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
    name: 'PublisherNewBook',
    data() {
      return {
        textbookTitle: '',
        author: '',
        ISBN: '',
        version: '',
        websiteLink: ''
      };
    },
    methods: {
      saveBook() {
      if (this.textbookTitle && this.author && this.ISBN && this.version && this.websiteLink) {
        const courseData = {
          textbookTitle: this.textbookTitle,
          author: this.author,
          ISBN: this.ISBN,
          version: this.version,
          websiteLink: this.websiteLink
        };
        
        try{
        localStorage.setItem('textbookData', JSON.stringify(courseData));
        localStorage.setItem('selectedTextbookTitle', this.textbookTitle); // Store the book title separately
        this.$router.push({ path: 'Pub_question.html' });
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
  @import '../assets/publisher_styles.css';
  .pub-newBook-container {
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