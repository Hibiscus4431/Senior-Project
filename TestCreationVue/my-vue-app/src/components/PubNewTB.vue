<template>
  <div class="pub-newTB-container">
    <div class="center large-heading sticky">
      <h1>Create New Test Bank</h1>
    </div>
    <div class="center large-paragraph">
      <form @submit.prevent="saveTestBank">
        <div class="form-row">
          <label for="bankName">Name of Test Bank:</label>
          <input type="text" id="bankName" v-model="bankName" required />
        </div>

        <div class="form-row">
          <label for="bankCh">Textbook Chapter:</label>
          <input type="text" id="bankCh" v-model="bankChapter" />
        </div>

        <div class="form-row">
          <label for="bankSec">Textbook Section:</label>
          <input type="text" id="bankSec" v-model="bankSection" />
        </div>

        <input type="submit" value="Submit" />
      </form>

      <div v-if="error" style="color: red; margin-top: 10px;">{{ error }}</div>
    </div>
  </div>
</template>

<script>
import api from '@/api';

export default {
  name: 'PublisherNewTB',
  data() {
    return {
      bankName: '',
      bankChapter: '',
      bankSection: '',
      textbookId: this.$route.query.textbook_id || '',
      textbookTitle: this.$route.query.title || '',
      error: null
    };
  },
  methods: {
    /*
    async handleSubmit() {
      if (!this.bankName || !this.textbookId) {
        alert('Please fill out all required fields (bank name and textbook ID).');
        return;
      }

      try {
        const token = localStorage.getItem('token');

        const payload = {
          testbank_name: this.bankName,
          textbook_id: this.textbookId
        };

        console.log('Submitting new testbank:', payload);

        const response = await api.post('/testbank/publisher', payload, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        console.log('Testbank created:', response.data);
        alert('Testbank created successfully!');
        this.$router.push({ path: 'PubQuestions', query: { textbook_id: this.textbookId } });

      } catch (error) {
        console.error('Error creating testbank:', error.response ? error.response.data : error.message);
        this.error = (error.response && error.response.data && error.response.data.error)
          ? error.response.data.error
          : 'Failed to create testbank. Please try again.';
      }
    }
      */
    async saveTestBank() {
      if (this.bankName && this.bankChapter && this.bankSection && this.textbookId) {
        const testBankData = {
          testbank_name: this.bankName,
          chapter_number: this.bankChapter,
          section_number: this.bankSection,
          textbook_id: this.textbookId
        };

        try {
          const response = await api.post('/testbanks/publisher', testBankData, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`
            }
          });
          console.log('Test bank saved successfully:', response.data);
          alert('Test bank saved successfully!');
          this.$router.push({ path: 'PubNewTB', query: { title: textbookTitle, textbook_id: textbookId } });
        } catch (error) {
          console.error('Error saving test bank:', error);
          alert('Failed to save the test bank. Please try again.');
        }
      } else {
        alert('Please fill out all fields.');
      }
    }
      ////////

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

input[type="submit"] {
  background-color: rgb(48, 191, 223);
  color: black;
  font-size: 20px;
  padding: 10px 20px;
}

.form-row {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 15px;
}

input[type="text"] {
  width: 300px;
  padding: 10px 12px;
  font-size: 18px;
  border: 2px solid #ccc;
  border-radius: 8px;
  background-color: #f9f9f9;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
  margin-left: 10px;
}

input[type="text"]:focus {
  border-color: rgb(48, 191, 223);
  box-shadow: 0 0 5px rgba(48, 191, 223, 0.5);
  outline: none;
}
</style>
