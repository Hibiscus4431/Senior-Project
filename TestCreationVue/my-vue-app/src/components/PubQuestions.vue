<template>
  <div class="pub-questions-container">
    <div class="center large-heading sticky">
      <h1 id="textbook-title">{{ textbookTitle }}</h1>
    </div>

    <div class="center large-paragraph">
      <router-link to="PubViewTB">
        <button class="p_button">View Test Banks</button>
      </router-link>

      <router-link :to="{ path: 'PubNewTB', query: { textbook_id: textbookId } }">
        <button class="p_button">New Test Bank</button>
      </router-link>

      <button class="p_button" @click="edit">New Question</button>
    </div>

    <!-- Popup Overlay -->
    <div class="popup-overlay" v-show="showForm" @click.self="closeForm">
      <div class="form-popup-modal">
        <form class="form-container" @submit.prevent="handleQuestionSave">
          <h1>New Question</h1>

          <label><b>Chapter Number</b></label>
          <input type="text" v-model="questionData.chapter" required />

          <label><b>Section Number</b></label>
          <input type="text" v-model="questionData.section" required />

          <label><b>Question Type</b><br /></label>
          
          <select v-model="selectedQuestionType" required>
            <option disabled value="">Select a type</option>
            <option>True/False</option>
            <option>Multiple Choice</option>
            <option>Matching</option>
            <option>Fill in the Blank</option>
            <option>Short Answer</option>
            <option>Essay</option>
          </select>

          <br /><br />
          <label><b>Question Text</b></label>
          <input type="text" v-model="questionData.question" required />

          <!-- Conditional Fields -->
          <div v-if="selectedQuestionType === 'True/False'">
            <label><b>Answer</b></label>
            <select v-model="questionData.answer">
              <option value="True">True</option>
              <option value="False">False</option>
            </select>
          </div>

          <div v-if="selectedQuestionType === 'Multiple Choice'">
            <label><b>Answer Choices (comma-separated)</b></label>
            <input type="text" v-model="questionData.answerChoices" />
            <label><b>Correct Answer</b></label>
            <input type="text" v-model="questionData.answer" />
          </div>

          <div v-if="selectedQuestionType === 'Matching'">
            <label><b>Matching Pairs</b></label>
            <div v-for="(pair, index) in matchingPairs" :key="index">
              <input type="text" v-model="pair.term" placeholder="Term" />
              <input type="text" v-model="pair.definition" placeholder="Definition" />
              <button type="button" @click="removePair(index)">Remove</button>
            </div>
            <button type="button" @click="addPair">Add Pair</button>
          </div>

          <div v-if="selectedQuestionType === 'Fill in the Blank'">
            <label><b>Correct Answer</b></label>
            <input type="text" v-model="questionData.answer" />
          </div>

          <div v-if="selectedQuestionType === 'Short Answer'">
            <label><b>Answer</b></label>
            <input type="text" v-model="questionData.answer" />
          </div>

          <div v-if="selectedQuestionType === 'Essay'">
            <label><b>Grading Instructions</b></label>
            <textarea v-model="questionData.instructions" placeholder="Instructions"></textarea>
          </div>

          <br />
          <label><b>Points Worth</b></label>
          <input type="text" v-model="questionData.points" required />

          <label><b>Estimated Time (in minutes)</b></label>
          <input type="text" v-model="questionData.time" required />

          <label><b>Grading Instructions</b></label>
          <input type="text" v-model="questionData.instructions" required />

          <label><b>Upload Image</b></label>
          <input type="file" @change="handleImageUpload" accept="image/*" />
          <img v-if="imagePreview" :src="imagePreview" alt="Preview" style="max-width: 100%;" />
          <br /><br />
          
          <button type="submit" class="btn">Save</button>
          <button type="button" class="btn cancel" @click="closeForm">Close</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/api';

export default {
  name: 'PubQuestions',
  data() {
    return {
      textbookTitle: '',
      textbookId: '',
      showForm: false,
      selectedQuestionType: '',
      matchingPairs: [],
      imagePreview: '',
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
      }
    };
  },
  methods: {
    selectQuestionType(type) {
      this.selectedQuestionType = type;
      this.edit();
    },
    edit() {
      this.showForm = true;
    },
    closeForm() {
      this.showForm = false;
    },
    addPair() {
      this.matchingPairs.push({ term: '', definition: '' });
    },
    removePair(index) {
      this.matchingPairs.splice(index, 1);
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
    },
    async handleQuestionSave() {
      try {
        const payload = {
          question_text: this.questionData.question,
          default_points: parseInt(this.questionData.points),
          est_time: parseInt(this.questionData.time),
          chapter_number: this.questionData.chapter,
          section_number: this.questionData.section,
          grading_instructions: this.questionData.instructions,
          type: this.selectedQuestionType,
          source: 'manual',
          textbook_id: this.textbookId
        };

        if (this.selectedQuestionType === 'True/False') {
          payload.true_false_answer = this.questionData.answer === 'True';
        } else if (this.selectedQuestionType === 'Multiple Choice') {
          const choices = this.questionData.answerChoices.split(',').map(c => c.trim());
          payload.options = choices.map(choice => ({
            option_text: choice,
            is_correct: choice.toLowerCase() === this.questionData.answer.toLowerCase()
          }));
        } else if (this.selectedQuestionType === 'Matching') {
          payload.matches = this.matchingPairs.map(pair => ({
            prompt_text: pair.term,
            match_text: pair.definition
          }));
        } else if (this.selectedQuestionType === 'Fill in the Blank') {
          payload.blanks = [{ correct_text: this.questionData.answer }];
        } else if (this.selectedQuestionType === 'Short Answer') {
          payload.answer = this.questionData.answer;
        } else if (this.selectedQuestionType === 'Essay') {
          payload.grading_instructions = this.questionData.instructions;
        }

        await api.post('/questions', payload, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });

        alert('Question saved successfully!');
        this.closeForm();

      } catch (err) {
        console.error('Error saving question:', err);
        alert('Failed to save question.');
      }
    }
  },
  mounted() {
    this.textbookTitle = this.$route.query.title || 'Book Title';
    this.textbookId = this.$route.query.textbook_id || '';
  }
};
</script>

<style scoped>
@import '../assets/publisher_styles.css';

.pub-questions-container {
  background-color: #17552a;
  font-family: Arial, sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>
