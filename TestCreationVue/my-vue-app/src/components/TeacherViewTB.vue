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
    <div class="center large-paragraph" style="color:#222">
      <router-link :to="{ path: '/TeacherQuestions', query: { courseTitle: courseTitle, courseId: courseId } }">
          <button class="t_button">Return to Question Page</button>
        </router-link><br>
      <div class="button-row">
        <!-- Edit Test Bank Info Button -->
        <button class="t_button" @click="showEditForm = true">Edit Draft Pool Info</button>




        <button class="t_button" @click="showCreateTestWarning = true">Create New Test</button>


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

      <!-- Create New Test Popup -->
      <div class="popup-overlay" v-if="showCreateTestWarning" @click.self="showCreateTestWarning = false">
        <div class="form-popup-modal">
          <form class="form-container" @submit.prevent="goToCreateTest">
            <label><strong>Test Name:</strong></label>
            <input type="text" v-model="testOptions.testName" placeholder="Enter a name for this test" required />

            <!-- Cover Page Checkbox -->
            <label class="checkbox-label">
              <input type="checkbox" v-model="testOptions.coverPage" />
              Add a cover page
            </label>
            <label><strong>Select Template:</strong></label>
            <div class="button-group">
              <button type="button" :class="{ active: testOptions.selectedTemplate === 'All Questions' }"
                @click="testOptions.selectedTemplate = 'All Questions'">
                All Questions
              </button>
              <button type="button" :class="{ active: testOptions.selectedTemplate === 'Multiple Choice' }"
                @click="testOptions.selectedTemplate = 'Multiple Choice'">
                Multiple Choice
              </button>
              <button type="button" :class="{ active: testOptions.selectedTemplate === 'Short Answer/Essay' }"
                @click="testOptions.selectedTemplate = 'Short Answer/Essay'">
                Short Answer/Essay
              </button>
            </div>

            <label><strong>Embedded Graphic:</strong></label>
            <input type="file" accept="image/*" @change="handleGraphicUpload" />
            <div v-if="testOptions.graphicPreview" style="margin-top: 10px;">
              <p><strong>Preview:</strong></p>
              <img :src="testOptions.graphicPreview" alt="Uploaded Graphic Preview"
                style="max-width: 100%; max-height: 200px; border: 1px solid #ccc;" />
            </div>



            <button type="submit" class="btn">Yes, Continue</button>
            <button type="button" class="btn cancel" @click="showCreateTestWarning = false">Cancel</button>
          </form>
        </div>
      </div>

      <!--Test bank questions will be generated here-->
      <div v-for="(q, index) in selectedQuestions" :key="q.id" class="question-box"
        :class="{ selected: selectedQuestionId === q.id }" @click="toggleQuestionSelection(q.id)">
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
      showEditForm: false,
      showEditQuestionForm: false,
      showCreateTestWarning: false,
      testFiles: [],
      selectedQuestions: [],
      selectedQuestionId: null,
      editingQuestionData: {},
      editingQuestionId: null,
      courseId: this.$route.query.courseId || '',
      courseTitle: this.$route.query.courseTitle || '',
      testBankId: this.$route.params.id || '',
      testBankName: this.$route.query.testBankName || '',
      editForm: {
        name: this.$route.query.testBankName || '',
        chapter: '',
        section: ''
      },
      testOptions: {
        testName: '',
        coverPage: false,
        selectedTemplate: '',
        graphicFile: null,
        graphicFileName: '',
        graphicPreview: ''
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
    handleGraphicUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        this.testOptions.graphicFile = file;
        this.testOptions.graphicFileName = file.name;
        this.testOptions.graphicPreview = e.target.result;
      };
      reader.readAsDataURL(file);
    },

    goToCreateTest() {
      const payload = {
        testName: this.testOptions.testName,
        selectedTemplate: this.testOptions.selectedTemplate,
        uploadedImage: this.testOptions.graphicFileName || '',
        coverPage: this.testOptions.coverPage || false,
        graphicPreview: this.testOptions.graphicPreview || ''
      };

      localStorage.setItem('testOptions', JSON.stringify(payload));

      this.$router.push({
        path: '/TeacherTemplate',
        query: {
          courseId: this.courseId,
          courseTitle: this.courseTitle,
          testBankId: this.testBankId,
          testBankName: this.testBankName
        }
      });
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

/* Ensure popup form labels are left-aligned */
.form-container label {
  text-align: left;
  display: block;
  font-size: 18px;
  font-weight: bold;
  margin-top: 10px;
  margin-bottom: 6px;
}
</style>