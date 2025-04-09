<!-- filepath: c:\Users\laure\Senior-Project\TestCreationVue\my-vue-app\src\components\PubViewTB.vue -->
<template>
  <div class="pub-viewTB-container">
    <div class="center large-heading sticky">
      <h1 id="pageTitle">Test Draft: {{ selectedTestBank }}</h1>
    </div>
    <div class="center large-paragraph">
      <!-- Dropdown to select question type -->
      <div class="dropdown">
        <button class="dropbtn">Question Type</button>
        <div class="dropdown-content">
          <a href="#" @click="fetchQuestions('True/False')">True/False</a>
          <a href="#" @click="fetchQuestions('Multiple Choice')">Multiple Choice</a>
          <a href="#" @click="fetchQuestions('Matching')">Matching</a>
          <a href="#" @click="fetchQuestions('Fill in the Blank')">Fill in the Blank</a>
          <a href="#" @click="fetchQuestions('Short Answer')">Short Answer</a>
          <a href="#" @click="fetchQuestions('Essay')">Essay</a>
        </div>
      </div>

      <!-- Edit Test Bank Info Button -->
      <button class="p_button" @click="showEditForm = true">Edit Test Bank Info</button>

      <!-- Modal Popup -->
      <div class="popup-overlay" v-if="showEditForm">
        <div class="form-popup-modal">
          <form class="form-container" @submit.prevent="updateTestBank">
            <label><strong>Test Bank Name:</strong></label>
            <input type="text" v-model="editForm.name" required />

            <label><strong>Chapter Number:</strong></label>
            <input type="text" v-model="editForm.chapter" required />

            <label><strong>Section Number:</strong></label>
            <input type="text" v-model="editForm.section" required />

            <button type="submit" class="btn">Save Changes</button>
            <button type="button" class="btn cancel" @click="showEditForm = false">Cancel</button>
          </form>
        </div>
      </div>


      <router-link :to="{ path: '/PubQuestions', query: { title: this.textbookTitle, textbook_id: this.textbookId } }">
        <button class="p_button">Return to Question Page</button>
      </router-link><br>

      <router-link :to="{ name: 'PubViewFeedback', params: { testbank_id: selectedTestBankId } }">
        <button class="p_button">View Feedback</button>
      </router-link>

      <hr>
      <!--Test bank questions will be generated here-->
      <div id="questionsContainer">
        <p v-for="question in selectedQuestions" :key="question">{{ question }}</p>
      </div>

      <!-- Insert the fetched questions display here -->
      <ul>
        <li v-for="(question, index) in questions" :key="index" class="question-box"
          @click="toggleQuestionSelection(question.id)">
          <strong>Question {{ index + 1 }}:</strong> {{ question.text }}<br>
          <span><strong>Type:</strong> {{ question.type }}</span><br>
          <span><strong>Chapter:</strong> {{ question.chapter || 'N/A' }}</span><br>
          <span><strong>Section:</strong> {{ question.section || 'N/A' }}</span><br>
          <span><strong>Points:</strong> {{ question.points }}</span><br>
          <span><strong>Estimated Time:</strong> {{ question.time }} minutes</span><br>

          <!-- Answer types -->
          <div v-if="question.type === 'True/False'">
            <strong>Answer:</strong> {{ question.answer ? 'True' : 'False' }}
          </div>

          <div v-if="question.type === 'Multiple Choice'">
            <strong>Correct Answer:</strong> {{ (question.correctOption && question.correctOption.option_text) ||
              'Not specified' }}<br>
            <p><strong>Other Options:</strong></p>
            <ul>
              <li v-for="(option, i) in question.incorrectOptions" :key="i" class="incorrect-answer">
                {{ option.option_text }}
              </li>
            </ul>
          </div>

          <div v-if="question.type === 'Short Answer'">
            <strong>Answer:</strong> {{ question.answer || 'Not provided' }}
          </div>

          <div v-if="question.type === 'Fill in the Blank'">
            <strong>Correct Answer(s):</strong>
            <ul>
              <li v-for="(blank, i) in question.blanks" :key="i">{{ blank.correct_text }}</li>
            </ul>
          </div>

          <div v-if="question.type === 'Matching'">
            <strong>Pairs:</strong>
            <ul>
              <li v-for="(pair, i) in question.pairs" :key="i">{{ pair.term }} - {{ pair.definition }}</li>
            </ul>
          </div>

          <div v-if="question.type === 'Essay'">
            <strong>Essay Instructions:</strong> {{ question.instructions || 'None' }}
          </div>

          <span><strong>Grading Instructions:</strong> {{ question.instructions || 'None' }}</span><br>

          <!-- Buttons shown only if selected -->
          <div v-if="selectedQuestionId === question.id" class="button-group">
            <button @click.stop="editQuestion(question)">Edit</button>
            <button @click.stop="deleteQuestion(question.id)">Delete</button>
          </div>
        </li>
      </ul>




      <!--file input element -->
      <input type="file" id="fileInput" style="display: none;" @change="handleFileUpload">


    </div>
  </div>
</template>

<script>
import api from '@/api';

export default {
  name: 'PublisherViewTB',
  data() {
    return {
      showPopup: false,
      showEditForm: false,
      selectedTestBank: this.$route.query.name || 'No Test Bank Selected',
      selectedTestBankId: this.$route.query.testbank_id || null,
      textbookId: this.$route.query.textbook_id || null,
      textbookTitle: this.$route.query.title || null,
      questions: {},
      editForm: {
        name: this.$route.query.name || '',
        chapter: this.$route.query.chapter || '',
        section: this.$route.query.section || ''
      }
    };
  },

  computed: {
    selectedQuestions() {
      return this.questions[this.selectedTestBank] || [];
    }
  },

  methods: {
    selectTestBank(testBank) {
      this.selectedTestBank = testBank;
    },
    edit() {
      this.showPopup = true;
    },
    closeForm() {
      this.showPopup = false;
      this.showEditForm = false;
    },
    async updateTestBank() {
      try {
        await api.put(`/testbanks/publisher/${this.selectedTestBankId}`, {
          name: this.editForm.name,
          chapter_number: this.editForm.chapter,
          section_number: this.editForm.section
        }, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        this.selectedTestBank = this.editForm.name;
        this.showEditForm = false;
        alert('Test bank updated successfully.');
      } catch (err) {
        console.error('Error updating test bank:', err);
        alert('Failed to update test bank.');
      }
    },



    async mounted() {
  if (this.selectedTestBankId) {
    try {
      const questionsRes = await api.get(`/testbanks/publisher/${this.selectedTestBankId}/questions`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      this.questions = questionsRes.data.questions || [];
    } catch (error) {
      console.error('Error loading test bank questions:', error);
    }
  }
},
  }
};
</script>

<style scoped>
@import '../assets/publisher_styles.css';


.pub-viewTB-container {
  background-color: #17552a;
  font-family: Arial, sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.dropbtn {
  background-color: rgb(48, 191, 223);
  color: black;
  padding: 10px;
  font-size: 20px;
  border: none;
}

.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-content {
  display: none;
  position: absolute;
  background-color: #f1f1f1;
  min-width: 160px;
  box-shadow: 0px 8px 16px 0px rgba(0, 0, 0, 0.2);
  z-index: 1;
}

.dropdown-content a {
  color: black;
  padding: 10px 15px;
  text-decoration: none;
  display: block;
}

.dropdown-content a:hover {
  background-color: rgb(48, 191, 223);
}

.dropdown:hover .dropdown-content {
  display: block;
}

.dropdown:hover .dropbtn {
  background-color: rgb(40, 151, 176);
}
</style>