<!-- filepath: c:\Users\laure\Senior-Project\TestCreationVue\my-vue-app\src\components\PubViewTB.vue -->
<template>
  <div class="theme-publisher">
    <div class="top-banner">
      <div class="banner-title">Draft Pool: {{ selectedTestBank }}</div>

      <div class="banner-actions">
        <router-link to="/PubHome" class="p_banner-btn">Home</router-link>
        <router-link to="/" class="p_banner-btn">Log Out</router-link>
      </div>
    </div>
    <div class="page-wrapper">
      <div class="button-row">
        <!-- Edit Test Bank Info Button -->
        <button class="p_button" @click="showEditForm = true">Edit Draft Pool Info</button>

        <router-link
          :to="{ path: '/PubQuestions', query: { title: this.textbookTitle, textbook_id: this.textbookId } }">
          <button class="p_button">Return to Question Page</button>
        </router-link>

        <router-link
          :to="{ name: 'PubViewFeedback', query: { testbank_id: selectedTestBankId, title: selectedTestBank } }">
          <button class="p_button">View Feedback</button>
        </router-link>

        <button class="p_button" @click="publishTestbank" :disabled="published">
          {{ published ? "Draft Pool Published" : "Publish Draft Pool" }}
        </button>
        <button class="p_button delete" v-if="!published" @click="deleteTestBank">
          Delete Draft Pool
        </button>
      </div>
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
      <div v-if="published" class="publish-warning">
        <strong>Note:</strong> This draft pool has been published. Question details can no longer be
        edited or removed. The draft pool cannot be deleted or modified.
      </div>
      <hr>
      <br>
      <!--Test bank questions will be generated here-->
      <div id="questionsContainer">
        <p v-for="question in selectedQuestions" :key="question">{{ question }}</p>
      </div>

      <!-- Insert the fetched questions display here -->
      <ul>
        <li v-for="(question, index) in questions" :key="index" class="p_question-box"
          :class="{ 'selected': selectedQuestionId === question.id }" @click="toggleQuestionSelection(question.id)">
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

          <div v-if="question.attachment">
            <p><strong>Attached Image:</strong></p>
            <img :src="question.attachment" alt="Question Attachment:"
              style="max-width: 100%; max-height: 400px; margin-bottom: 10px;" />
          </div>

          <span><strong>Grading Instructions:</strong> {{ question.instructions || 'None' }}</span><br>

          <div v-if="question.attachments && question.attachments.length">
            <strong>Attachments:</strong>
            <ul>
              <li v-for="(att, i) in question.attachments" :key="i">
                <a :href="att.url" target="_blank" rel="noopener">{{ att.filename }}</a>
                <div v-if="att.filename && att.filename.match(/\.(jpg|jpeg|png|gif)$/i)">
                  <img :src="att.url" alt="Attachment Image" style="max-width: 200px; margin-top: 10px;" />
                </div>
              </li>
            </ul>
          </div>
          <!-- Buttons shown only if selected -->
          <div v-if="selectedQuestionId === question.id && !published" class="p_button-group">
            <button @click.stop="removeQuestionFromTestBank(question.id)" :disabled="published"
              :title="published ? 'Published — cannot remove question' : 'Remove from Draft Pool'">
              {{ published ? "Published - Cannot Remove" : "Remove from Draft Pool" }}
            </button>
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
      selectedTestBankId: this.$route.query.testbank_id || this.$route.params.testbank_id || null,
      textbookId: this.$route.query.textbook_id || null,
      textbookTitle: this.$route.query.title || null,
      selectedQuestionId: null,
      published: false,
      questions: [],
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

  async mounted() {
    await this.checkPublishedStatus();
    await this.loadQuestions();
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
      } catch (err) {
        console.error('Error updating test bank:', err);
      }
    },

    // ... your existing methods ...
    async loadQuestions() {
      if (this.selectedTestBankId) {
        try {
          const questionsRes = await api.get(`/testbanks/publisher/${this.selectedTestBankId}/questions`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`
            }
          });

          const rawQuestions = questionsRes.data.questions || [];

          // ✅ Transform each question into full display shape
          this.questions = rawQuestions.map((q) => {
            const base = {
              id: q.id,
              text: q.question_text,
              type: q.type,
              chapter: q.chapter_number || 'N/A',
              section: q.section_number || 'N/A',
              points: q.default_points || 'N/A',
              time: q.est_time || 'N/A',
              instructions: q.grading_instructions || 'None',
              attachment: q.attachment && q.attachment.url ? q.attachment.url : ''
            };

            switch (q.type) {
              case 'True/False':
                return { ...base, answer: q.true_false_answer };
              case 'Multiple Choice':
                return {
                  ...base,
                  correctOption: q.correct_option || null,
                  incorrectOptions: q.incorrect_options || []
                };
              case 'Matching':
                return {
                  ...base,
                  pairs: (q.matches || []).map(pair => ({
                    term: pair.prompt_text,
                    definition: pair.match_text
                  }))
                };
              case 'Fill in the Blank':
                return {
                  ...base,
                  blanks: q.blanks || []
                };
              case 'Short Answer':
                return {
                  ...base,
                  answer: q.answer || ''
                };
              case 'Essay':
                return base;
              default:
                return base;
            }
          });

        } catch (error) {
          console.error('Error loading test bank questions:', error);
        }
      }
    },

    toggleQuestionSelection(id) {
      if (this.selectedQuestionId === id) {
        this.selectedQuestionId = null; // Deselect if already selected
      } else {
        this.selectedQuestionId = id; // Select the clicked question
      }
    },
    async removeQuestionFromTestBank(questionId) {

      if (!confirm('Are you sure you want to remove this question from the test bank?')) return;

      try {
        // 👉 Force the DELETE to use the publisher-specific version
        await api.delete(`/testbanks/${this.selectedTestBankId}/questions/${questionId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        this.questions = this.questions.filter(q => q.id !== questionId);
        this.selectedQuestionId = null;
      } catch (err) {
        console.error('Error removing question:', err);
      }
    },
    async publishTestbank() {
      if (!this.selectedTestBankId) return;

      try {
        const response = await api.post(`/testbanks/${this.selectedTestBankId}/publish`, {}, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });

        this.published = true;
      } catch (error) {
        console.error("Error publishing test bank:", error);
      }
    },
    async deleteTestBank() {
      if (this.published) {
        return;
      }

      if (!confirm('Are you sure you want to delete this entire draft pool? This action cannot be undone.')) return;

      try {
        await api.delete(`/testbanks/${this.selectedTestBankId}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });

        this.$router.push({
          path: '/PubQuestions',
          query: {
            title: this.textbookTitle,
            textbook_id: this.textbookId
          }
        });
      } catch (err) {
        console.error('Error deleting draft pool:', err);
      }
    },
    async checkPublishedStatus() {
      try {
        const res = await api.get('/testbanks/publisher', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
          params: { textbook_id: this.textbookId }
        });

        const testbanks = res.data.testbanks || [];
        const found = testbanks.find(tb => tb.testbank_id == this.selectedTestBankId);

        if (found) {
          this.published = found.is_published === true;
        } else {
          console.warn("Testbank not found in returned list");
        }
      } catch (err) {
        console.error("Failed to fetch testbank status:", err);
      }
    }


  }
};
</script>

<style scoped>
@import '../assets/publisher_styles.css';

ul {
  list-style-type: none;
  padding-left: 0;
}
</style>