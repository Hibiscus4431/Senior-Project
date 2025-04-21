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
      <router-link :to="{
        path: '/PubViewTB',
        query: {
          name: selectedTestBank,
          textbook_id: textbookId,
          testbank_id: $route.query.testbank_id,  // ✅ Add this!
          title: $route.query.title
        }
      }">
        <button class="p_button">Return to Draft Pools</button>
      </router-link>


      <hr />

      <div id="feedbackContainer">
        <p v-if="loading">Loading feedback...</p>
        <p v-else-if="feedbackList.length === 0">No questions in this draft pool have feedback yet.</p>

        <div v-else>
          <div v-for="(entry, index) in feedbackList" :key="index"
            :class="['p_question-box', { selected: selectedQuestionId === entry.question_id }]"
            @click="toggleQuestionSelection(entry.question_id)">
            <strong>Question {{ index + 1 }}:</strong> {{ entry.question_text }}

            <!-- Always show feedback -->
            <div v-if="entry.feedback && entry.feedback.length" class="feedback-section">
              <p><strong>Feedback:</strong></p>
              
              <ul>
                <li v-for="(fb, i) in entry.feedback" :key="i">
                  "{{ fb.comment }}" — <em>{{ fb.username }} ({{ fb.role }})</em>
                </li>
              </ul>
            </div>
            <div v-else>
              <p>No feedback yet.</p>
            </div>

            <!-- ✅ Button shows only if question is selected -->
            <div v-if="selectedQuestionId === entry.question_id" class="p_button-group">
              <button @click.stop="openFeedbackForm(entry.question_id)">Leave Feedback</button>
            </div>
          </div>

          <!-- ✅ Feedback popup -->
          <div v-if="showFeedbackForm" class="popup-overlay">
            <div class="form-popup-modal">
              <h2>Leave Feedback</h2>
              <textarea v-model="feedbackText" rows="5" placeholder="Enter your comment here..."></textarea>
              <br /><br />
              <button class="btn" @click="submitFeedback">Submit</button>
              <button class="btn cancel" @click="closeFeedbackForm">Cancel</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/api';

export default {
  name: 'PubViewFeedback',
  data() {
    return {
      testbankId: null,
      textbookId: this.$route.query.textbook_id || null,
      selectedTestBank: '',
      feedbackList: [],
      loading: true,
      userRole: '',
      selectedQuestionId: null,
      showFeedbackForm: false,
      selectedQuestionIdForFeedback: null,
      feedbackText: ''
    };
  },
  async mounted() {
    const query = this.$route.query;
    this.testbankId = parseInt(query.testbank_id);
    this.selectedTestBank = query.title || 'No Draft Pool Selected';

    const token = localStorage.getItem('token');
    if (token) {
      const payload = JSON.parse(atob(token.split('.')[1]));
      this.userRole = payload.role;
    }

    this.fetchFeedbackByTestbank();
  },
  methods: {
    async fetchFeedbackByTestbank() {
      try {
        const res = await api.get(`/feedback/${this.testbankId}/questions-with-feedback`);
        this.feedbackList = res.data;
        console.log('Feedback loaded:', this.feedbackList);
      } catch (err) {
        console.error('Error loading feedback:', err);
      } finally {
        this.loading = false;
      }
    },

    toggleQuestionSelection(questionId) {
      this.selectedQuestionId = this.selectedQuestionId === questionId ? null : questionId;
    },

    openFeedbackForm(questionId) {
      this.selectedQuestionIdForFeedback = questionId;
      this.feedbackText = '';
      this.showFeedbackForm = true;
    },

    closeFeedbackForm() {
      this.selectedQuestionIdForFeedback = null;
      this.feedbackText = '';
      this.showFeedbackForm = false;
    },

    async submitFeedback() {
      try {
        await api.post('/feedback/create', {
          question_id: this.selectedQuestionIdForFeedback,
          comment_field: this.feedbackText
        }, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        this.closeFeedbackForm();

        const entry = this.feedbackList.find(q => q.question_id === this.selectedQuestionIdForFeedback);
        if (entry) {
          if (!entry.feedback) entry.feedback = [];
          entry.feedback.push({
            comment: this.feedbackText,
            username: 'You',
            role: this.userRole
          });
        }

      } catch (error) {
        console.error('Error submitting feedback:', error);
      }
    }
  }
};
</script>


<style scoped>
@import '../assets/publisher_styles.css';
</style>
