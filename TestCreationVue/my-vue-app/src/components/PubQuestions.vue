<template>
  <div class="pub-questions-container">
    <div class="center large-heading sticky">
      <h1 id="textbook-title">{{ textbookTitle }}</h1>
    </div>
    <!-- Test Bank Selector -->
    <div class="dropdown">
      <button class="dropbtn">
        {{ selectedTestBank ? selectedTestBank.name : 'Select Test Bank' }}
      </button>
      <div class="dropdown-content">
        <a v-for="tb in testBanks" :key="tb.testbank_id" href="#" @click.prevent="selectTestBank(tb)">
          {{ tb.name }}
        </a>
      </div>

      <router-link :to="{ path: 'PubNewTB', query: { title: textbookTitle, textbook_id: textbookId } }">
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
            <label><b>Correct Answer</b></label>
            <input type="text" v-model="questionData.answer" />
            <label><b>Incorrect Answer Choices (comma-separated)</b></label>
            <input type="text" v-model="questionData.answerChoices" />
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
      testBanks: [],
      selectedTestBank: null,
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
        image: null
      }
    };
  },
  methods: {
    async fetchTestBanks() {
      try {
        const response = await api.get('/testbanks/publisher', {
          params: { textbook_id: this.textbookId },
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        this.testBanks = response.data.testbanks;
      } catch (error) {
        console.error('Error loading test banks:', error);
      }
    },


    selectTestBank(tb) {
      this.$router.push({
        name: 'PubViewTB',
        query: {
          testbank_id: tb.testbank_id,
          name: tb.name,
          textbook_id: this.textbookId,
          title: this.textbookTitle
        }
      });
    },


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
        this.questionData.imageFile = file;

        const reader = new FileReader();
        reader.onload = (e) => {
          this.imagePreview = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    }
    ,

    //function to reset the form after saved question posts
    resetForm() {
      this.questionData = {
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
      };
      this.selectedQuestionType = '';
      this.matchingPairs = [];
      this.imagePreview = '';
    },
    //function to post the question to the server
    async handleQuestionSave() {
      try {
        let postData;
        let config;

        if (this.questionData.imageFile) {
          // Use FormData for file + data
          postData = new FormData();

          postData.append('file', this.questionData.imageFile);
          postData.append('question_text', this.questionData.question);
          postData.append('default_points', this.questionData.points);
          postData.append('est_time', this.questionData.time);
          postData.append('chapter_number', this.questionData.chapter);
          postData.append('section_number', this.questionData.section);
          postData.append('grading_instructions', this.questionData.instructions);
          postData.append('type', this.selectedQuestionType);
          postData.append('source', 'manual');
          postData.append('textbook_id', this.textbookId);

          if (this.selectedQuestionType === 'True/False') {
            postData.append('true_false_answer', this.questionData.answer === 'True');
          } else if (this.selectedQuestionType === 'Multiple Choice') {
            const incorrectChoices = this.questionData.answerChoices
              .split(',')
              .map(c => c.trim())
              .filter(c => c.length > 0);

            const options = [
              { option_text: this.questionData.answer.trim(), is_correct: true },
              ...incorrectChoices.map(choice => ({
                option_text: choice,
                is_correct: false
              }))
            ];
            postData.append('options', JSON.stringify(options));
          } else if (this.selectedQuestionType === 'Matching') {
            postData.append('matches', JSON.stringify(this.matchingPairs));
          } else if (this.selectedQuestionType === 'Fill in the Blank') {
            postData.append('blanks', JSON.stringify([{ correct_text: this.questionData.answer }]));
          } else if (this.selectedQuestionType === 'Short Answer') {
            postData.append('answer', this.questionData.answer);
          } else if (this.selectedQuestionType === 'Essay') {
            postData.append('grading_instructions', this.questionData.instructions);
          }

          config = {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`,
              'Content-Type': 'multipart/form-data'
            }
          };
        } else {
          // fallback: standard JSON if no file
          postData = {
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
            postData.true_false_answer = this.questionData.answer === 'True';
          } else if (this.selectedQuestionType === 'Multiple Choice') {
            const incorrectChoices = this.questionData.answerChoices
              .split(',')
              .map(c => c.trim())
              .filter(c => c.length > 0);

            postData.options = [
              { option_text: this.questionData.answer.trim(), is_correct: true },
              ...incorrectChoices.map(choice => ({
                option_text: choice,
                is_correct: false
              }))
            ];
          } else if (this.selectedQuestionType === 'Matching') {
            postData.matches = this.matchingPairs;
          } else if (this.selectedQuestionType === 'Fill in the Blank') {
            postData.blanks = [{ correct_text: this.questionData.answer }];
          } else if (this.selectedQuestionType === 'Short Answer') {
            postData.answer = this.questionData.answer;
          } else if (this.selectedQuestionType === 'Essay') {
            postData.grading_instructions = this.questionData.instructions;
          }

          config = {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
          };
        }

        await api.post('/questions', postData, config);


        alert('Question saved successfully!');
        this.closeForm();
        this.resetForm();


      } catch (err) {
        console.error('Error saving question:', err);
        alert('Failed to save question.');
      }
    }
  },
  mounted() {
    this.textbookTitle = this.$route.query.title || 'Book Title';
    this.textbookId = this.$route.query.textbook_id || '';
    if (this.textbookId) {
      this.fetchTestBanks();
    }
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
