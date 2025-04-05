<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/PubNewBook.vue -->
<template>
  <div class="pub-newBook-container">
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
import api from '@/api'

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
    async saveBook() {
      //&& this.websiteLink include in condition when table updated
      if (this.textbookTitle && this.author && this.ISBN && this.version) {
        const bookData = {
          //replaced with titles of database fields
          textbook_title: this.textbookTitle,
          textbook_author: this.author,
          textbook_isbn: this.ISBN,
          textbook_version: this.version,
          websiteLink: this.websiteLink
        };

        try {

          const response = await api.post('/textbooks', bookData, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`,
            },
          });
          console.log('Book saved successfully:', response.data);
          alert('Book saved successfully!');
          this.$router.push({ path: '/PubQuestions' });
        }
        catch (error) {
          console.error('Error saving book:', error);
          alert('Failed to save the book. Please try again.');
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