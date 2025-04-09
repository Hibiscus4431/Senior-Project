<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherViewTB.vue -->
<template>
  <div class="teacher-viewTB-container">
    <!-- This is the page where the teacher can see all of their test banks-->
    <div class="center large-heading sticky">
      <h1 id="pageTitle">Test Draft: {{ testBankName }}</h1>
    </div>
    <div class="center large-paragraph">
      <!-- Edit Test Bank Info Button -->
      <button class="t_button" @click="showEditForm = true">Edit Draft Pool Info</button>

      <!-- Edit Test Bank Info Popup Form -->
      <div class="form-popup" v-if="showEditForm">
        <form class="form-container" @submit.prevent="updateTestBank">
          <label><strong>Test Bank Name:</strong></label>
          <input type="text" v-model="editForm.name" required />

          <label><strong>Chapter Number:</strong></label>
          <input type="number" v-model="editForm.chapter" required />

          <label><strong>Section Number:</strong></label>
          <input type="number" v-model="editForm.section" required />

          <button type="submit" class="btn">Save Changes</button>
          <button type="button" class="btn cancel" @click="showEditForm = false">Cancel</button>
        </form>
      </div>


      <router-link :to="{ path: '/TeacherQuestions', query: { courseTitle: courseTitle, courseId: courseId } }">
        <button class="t_button">Return to Question Page</button>
      </router-link><br>

      <router-link to="TeacherNewTest">
        <button class="t_button">Create New Test</button>
      </router-link>

      <button class="t_button" @click="viewPrevious">View Previous Tests</button>
      <br>
      <hr>

      <!--Test bank questions will be generated here-->
      <div v-for="(q, index) in selectedQuestions" :key="q.id"
        :class="['question-box', { selected: selectedQuestionId === q.id }]" @click="toggleQuestionSelection(q.id)">
        <strong>Question {{ index + 1 }}:</strong> {{ q.question_text }}<br>
        <span><strong>Type:</strong> {{ q.type }}</span><br>
        <span><strong>Points:</strong> {{ q.default_points }}</span><br>
        <span><strong>Chapter:</strong> {{ q.chapter_number }}</span><br>
        <span><strong>Section:</strong> {{ q.section_number }}</span><br>
        <span><strong>Estimated Time:</strong> {{ q.est_time }} minutes</span><br>
        <span><strong>Grading Instructions:</strong> {{ q.grading_instructions }}</span><br>

        <!-- Action buttons shown only when this question is selected -->
        <div v-if="selectedQuestionId === q.id" class="button-group">
          <button @click.stop="editQuestion(q)">Edit</button>
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
      editForm: {           // ← and this
        name: this.$route.query.testBankName || '',
        chapter: '',
        section: ''
      }
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

    editQuestion(q) {
      alert(`Edit feature is not implemented on this page yet.\nPlease go to "Return to Question Page" to edit the question.`);
    },
    async updateTestBank() {
      try {
        await api.put(`/teacher/${this.testBankId}`, {
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

    }  // ✅ no comma here — last method in the block
  }  // ✅ closes methods
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
</style>