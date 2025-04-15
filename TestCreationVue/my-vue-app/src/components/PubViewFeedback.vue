<template>
  <div class="theme-publisher">
    <div class="top-banner">
      <div class="banner-title">Draft Pool: {{ selectedTestBank }}</div>
      <div class="banner-actions">
        <router-link to="/PubHome" class="p_banner-btn">Home</router-link>
        <router-link to="/" class="p_banner-btn">Log Out</router-link>
      </div>
    </div>

    <div class="center large-paragraph" style="color:#222">
      <router-link
        :to="{ path: '/PubViewTB', query: { title: $route.query.title, textbook_id: $route.query.textbook_id } }">
        <button class="p_button">Return to Test Banks</button>
      </router-link>

      <hr />

      <div id="feedbackContainer">
        <p v-if="loading">Loading feedback...</p>
        <p v-else-if="feedbackList.length === 0">No questions in this test bank have feedback yet.</p>

        <div v-else>
          <div v-for="(entry, index) in feedbackList" :key="index" class="question-box">
            <p><strong>Question Type:</strong> {{ entry.type || 'Unknown' }}</p>
            <p><strong>Question:</strong> {{ entry.question }}</p>
            <p><strong>Correct Answer:</strong> <span class="correct-answer">{{ entry.correct_answer }}</span></p>

            <div v-if="entry.feedbacks && entry.feedbacks.length">
              <p><strong>Feedback:</strong></p>
              <ul>
                <li v-for="(fb, i) in entry.feedbacks" :key="i">
                  "{{ fb.comment }}" — <em>{{ fb.username }} ({{ fb.role }})</em>
                </li>
              </ul>
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
      selectedTestBank: this.$route.query.title || 'No Test Bank Selected',
      feedbackList: [],
      questions: [],
      loading: true
    };
  },
  mounted() {
    const query = this.$route.query;
    this.testbankId = parseInt(query.testbank_id);
    this.selectedTestBank = query.title || 'No Test Bank Selected';

    console.log('Parsed testbankId:', this.testbankId);
    this.fetchQuestionsAndFeedback();
  },
  methods: {
    getCorrectAnswer(q) {
      switch (q.type) {
        case 'True/False':
          return q.true_false_answer ? 'True' : 'False';
        case 'Multiple Choice':
          return q.correct_option ? q.correct_option.option_text : 'N/A';
        case 'Fill in the Blank':
          return q.blanks ? q.blanks.map(b => b.correct_text).join(', ') : 'N/A';
        case 'Matching':
          return q.matches ? q.matches.map(m => `${m.prompt_text} → ${m.match_text}`).join('; ') : 'N/A';
        default:
          return 'N/A';
      }
    },

    async fetchQuestionsAndFeedback() {
      try {
        const res = await api.get(`/questions`, {
          params: { testbank_id: this.testbankId }
        });
        this.questions = res.data.questions;
        console.log('Raw question objects:', this.questions);

        const feedbacks = [];

        for (const q of this.questions) {
          try {
            const feedbackRes = await api.get(`/feedback/question/${q.id}`);
            if (feedbackRes.data.length > 0) {
              feedbacks.push({
                question: q.question_text,
                type: q.type,
                correct_answer: this.getCorrectAnswer(q),
                feedbacks: feedbackRes.data
              });
            }
          } catch (err) {
            console.warn(`Failed to fetch feedback for question ${q.id}`, err);
          }
        }

        this.feedbackList = feedbacks;
      } catch (err) {
        console.error('Error loading feedback:', err);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
@import '../assets/publisher_styles.css';
</style>
