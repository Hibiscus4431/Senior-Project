<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherViewTB.vue -->
<template>
  <div class="theme-teacher">
    <div class="top-banner">
      <div class="banner-title">Test Draft: {{ testBankName }}</div>

      <div class="t_banner-actions">
        <router-link to="/TeacherHome" class="t_banner-btn">Home</router-link>
        <router-link to="/" class="t_banner-btn">Log Out</router-link>
      </div>
    </div>
    <div class="center large-paragraph" style ="color:#222">
      <div class="button-row">
      <!-- Edit Test Bank Info Button -->
      <button class="t_button" @click="showEditForm = true">Edit Draft Pool Info</button>

   


        <router-link :to="{ path: '/TeacherQuestions', query: { courseTitle: courseTitle, courseId: courseId } }">
          <button class="t_button">Return to Question Page</button>
        </router-link><br>

        <!-- <router-link to="TeacherNewTest">
          <button class="t_button">Create New Test</button>
        </router-link> -->

        <button class="t_button" @click="showCreateTestWarning = true">Create New Test</button>
        <!--  -->

        <button class="t_button" @click="viewPrevious">View Previous Tests</button>
        <br>
        </div>
        <hr>

           <!-- Edit Test Bank Info Popup Form -->
      <!-- Modal Popup -->
      <div class="popup-overlay" v-if="showEditForm">
        <div class="form-popup-modal">
          <form class="form-container" @submit.prevent="updateTestBank">
            <label><strong>Draft Pool Name:</strong></label>
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

        <!--Test bank questions will be generated here-->
        <div v-for="(q, index) in selectedQuestions" :key="q.id"
          class="question-box" :class="{ selected: selectedQuestionId === q.id }" @click="toggleQuestionSelection(q.id)">
          <strong>Question {{ index + 1 }}:</strong> {{ q.question_text }}<br>
          <span><strong>Type:</strong> {{ q.type }}</span><br>
          <span><strong>Chapter:</strong> {{ q.chapter_number || 'N/A' }}</span><br>
          <span><strong>Section:</strong> {{ q.section_number || 'N/A' }}</span><br>
          <span><strong>Points:</strong> {{ q.default_points }}</span><br>
          <span><strong>Estimated Time:</strong> {{ q.est_time }} minutes</span><br>

          <!-- Conditional content by type -->
          <div v-if="q.type === 'True/False'">
            <strong>Answer:</strong> {{ q.true_false_answer ? 'True' : 'False' }}
          </div>

          <div v-if="q.type === 'Multiple Choice'">
            <strong>Correct Answer:</strong> {{ q.correct_option && q.correct_option.option_text || 'Not specified' }}<br>
            <strong>Other Options:</strong>
            <ul>
              <li v-for="(option, i) in q.incorrect_options || []" :key="i">{{ option.option_text }}</li>
            </ul>
          </div>

          <div v-if="q.type === 'Matching'">
            <strong>Pairs:</strong>
            <ul>
              <li v-for="(pair, i) in q.matches || []" :key="i">{{ pair.prompt_text }} - {{ pair.match_text }}</li>
            </ul>
          </div>

          <div v-if="q.type === 'Fill in the Blank'">
            <strong>Correct Answer(s):</strong>
            <ul>
              <li v-for="(blank, i) in q.blanks || []" :key="i">{{ blank.correct_text }}</li>
            </ul>
          </div>

          <div v-if="q.type === 'Short Answer'">
            <strong>Answer:</strong> {{ q.answer || 'Not provided' }}
          </div>

          <div v-if="q.type === 'Essay'">
            <strong>Essay Instructions:</strong> {{ q.grading_instructions || 'None' }}
          </div>

          <span><strong>Grading Instructions:</strong> {{ q.grading_instructions || 'None' }}</span>

          <!-- Action buttons -->
          <div v-if="selectedQuestionId === q.id" class="button-group">
            <!-- <button @click.stop="editQuestion(q)">Edit</button> -->
            <button @click.stop="removeQuestionFromTestBank(q.id)">Remove</button>
          </div>
          <hr>
        </div>




        <!-- contents of popup-->
        <div class="form-popup" id="test_view">
          <form action="#" class="form-container">
            Please select draft version to view:
            <!--Figure out how to list the old test versions-->
            <!--When version is clicked it will send them to test view page-->
            <button type="submit" class="btn">Save</button>
            <button type="button" class="btn cancel" @click="closeForm">Close</button>
          </form>
        </div>
      </div>
    </div>


    <!-- Edit Modal Form -->
    <div class="popup-overlay" v-if="showEditQuestionForm" @click.self="showEditQuestionForm = false">
  <div class="form-popup-modal">
    <form class="form-container" @submit.prevent="saveEditedQuestion">
      <h2>Edit Question</h2>

      <label><b>Question Text</b></label>
      <input v-model="editingQuestionData.question" required />

      <label><b>Points</b></label>
      <input v-model="editingQuestionData.points" required />

      <label><b>Time (min)</b></label>
      <input v-model="editingQuestionData.time" required />

      <label><b>Grading Instructions</b></label>
      <input v-model="editingQuestionData.instructions" />

      <!-- Add type-specific edits if needed -->

      <button type="submit" class="btn">Save</button>
      <button type="button" class="btn cancel" @click="showEditQuestionForm = false">Cancel</button>
    </form>
  </div>
</div>
  
      <!-- Popup for viewing previous tests -->
      <!-- <div class="popup-overlay" v-if="showPopup" @click.self="closeForm">
        <div class="form-popup-modal">
          <h2>Previous Tests</h2>
          <ul>
            <li v-for="test in testFiles" :key="test.id">
              <strong>Test ID:</strong> {{ test.id }}<br>
              <strong>Test Name:</strong> {{ test.name }}<br>
              <strong>Date Created:</strong> {{ test.created_at }}<br>
              <button @click="viewTest(test.id)">View Test</button>
            </li>
          </ul>
          <button class="btn cancel" @click="closeForm">Close</button>
        </div>
      </div> -->

      <div class="popup-overlay" v-if="showCreateTestWarning" @click.self="showCreateTestWarning = false">
        <div class="form-popup-modal">
          <form class="form-container" @submit.prevent="goToCreateTest">
            <h2 style="text-align: center; margin-bottom: 20px;">Create New Test</h2>
            <p style="text-align: center; font-size: 16px; margin-bottom: 20px;">
              Are you sure you want to start creating a new test?<br>
              <strong>Unsaved changes to this test bank may be lost.</strong>
            </p>
            <button type="submit" class="btn">Yes, Continue</button>
            <button type="button" class="btn cancel" @click="showCreateTestWarning = false">Cancel</button>
          </form>
        </div>
      </div>
      

</template>

<script>
import api from '@/api';

export default {
  name: 'TeacherViewTB',
  data() {
    return {
      showPopup: false,
      showEditForm: false,  // ← you need this
      testFiles: [],
      courseId: this.$route.query.courseId || '',
      courseTitle: this.$route.query.courseTitle || '',
      testBankId: this.$route.params.id || '',
      testBankName: this.$route.query.testBankName || '', // will fetch it below
      selectedQuestions: [],
      selectedQuestionId: null,
      editForm: {           // ← and this
        name: this.$route.query.testBankName || '',
        chapter: '',
        section: ''
      },
      //////////
      showEditQuestionForm: false,
      editingQuestionData: {},
      editingQuestionId: null,
      //////////
      showCreateTestWarning: false
      /////////
    };
  },
  mounted() {
    this.initialize();
  },
  methods: {
    async viewPrevious() {
      try {
        const response = await api.get('/tests', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          },
          params: {
            course_id: this.courseId,
            testbank_id: this.testBankId
          }
        });
        this.testFiles = response.data.tests || [];
        this.showPopup = true;
      } catch (err) {
        console.error('Failed to fetch tests:', err);
        alert('Could not load previous tests.');
      }
    },
    closeForm() {
      this.showPopup = false;
    },
    async fetchQuestions() {
      if (!this.testBankId) return;
      try {
        const response = await api.get(`/testbanks/${this.testBankId}/questions`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        console.log("Fetched questions:", response.data.questions);
        this.selectedQuestions = response.data.questions || [];
      } catch (err) {
        console.error('Error fetching questions for test bank:', err);
        this.selectedQuestions = [];
      }
    },

    //helper functions for generated questions
    toggleQuestionSelection(questionId) {
      this.selectedQuestionId = this.selectedQuestionId === questionId ? null : questionId;
    },

    async removeQuestionFromTestBank(questionId) {
      if (!confirm('Are you sure you want to remove this question from the test bank?')) return;

      try {
        await api.delete(`/testbanks/${this.testBankId}/questions/${questionId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        this.selectedQuestions = this.selectedQuestions.filter(q => q.id !== questionId);
        alert('Question removed from test bank.');
      } catch (err) {
        console.error('Error removing question:', err);
        alert('Failed to remove question from test bank.');
      }
    },

    // editQuestion(q) {
    //   this.editingQuestionId = q.id;
    //   this.editingQuestionData = {
    //     chapter: q.chapter_number || '',
    //     section: q.section_number || '',
    //     question: q.question_text,
    //     points: q.default_points,
    //     time: q.est_time,
    //     instructions: q.grading_instructions || '',
    //     type: q.type,
    //     answer: q.answer || '', // optional
    //     correctOption: (q.correct_option && q.correct_option.option_text) || '',
    //     incorrectOptions: (q.incorrect_options || []).map(o => o.option_text),
    //     blanks: q.blanks || [],
    //     matches: q.matches || []
    //   };
    //   this.showEditQuestionForm = true;
    // },
    async updateTestBank() {
      try {
        await api.put(`/testbanks/teacher/${this.testBankId}`, {
          name: this.editForm.name,
          chapter_number: this.editForm.chapter,
          section_number: this.editForm.section
        }, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });


        this.testBankName = this.editForm.name; // update title
        this.showEditForm = false;
        alert('Test bank updated successfully.');
      } catch (err) {
        console.error('Error updating test bank:', err);
        alert('Failed to update test bank.');
      }
    },

    async initialize() {
      await this.fetchQuestions();
      try {
        const res = await api.get(`/testbanks/${this.testBankId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        this.testBankName = res.data.name;
        this.editForm.name = res.data.name;
        this.editForm.chapter = res.data.chapter_number;
        this.editForm.section = res.data.section_number;
      } catch (err) {
        console.warn("Couldn't load testbank details:", err);
      }

    },

    async saveEditedQuestion() {
      try {
        await api.put(`/questions/${this.editingQuestionId}`, {
          question_text: this.editingQuestionData.question,
          default_points: this.editingQuestionData.points,
          est_time: this.editingQuestionData.time,
          grading_instructions: this.editingQuestionData.instructions,
          chapter_number: this.editingQuestionData.chapter,
          section_number: this.editingQuestionData.section
        }, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });

        alert('Question updated.');
        this.showEditQuestionForm = false;
        await this.fetchQuestions();
      } catch (err) {
        console.error('Failed to update question:', err);
        alert('Failed to update.');
      }
    },

    goToCreateTest() {
      this.$router.push('TeacherNewTest');
    }

  } 
};

</script>

<style scoped>
@import '../assets/teacher_styles.css';

.teacher-viewTB-container {
  background-color: #43215a;
  font-family: Arial, sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.form-popup {
  width: 300px;
}

.question-box {
  background-color: #ffffff;
  /* or a soft color */
  color: #000000;
  /* black text */
  padding: 16px;
  margin-bottom: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  font-size: 15px;
  line-height: 1.5;
  text-align: left;
  text-align: left;
}
</style>