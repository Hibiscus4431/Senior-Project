<template>
  <div class="theme-publisher">
    <div class="top-banner">
      <div class="banner-title">Draft Pool: {{ selectedTestBank }}</div>
      <div class="banner-actions">
        <router-link to="/PubHome" class="banner-btn">Home</router-link>
        <router-link to="/" class="banner-btn">Log Out</router-link>
      </div>
    </div>

    <div class="center large-paragraph" style="color:#222">
      <router-link
        :to="{ path: '/PubViewTB', query: { title: this.$route.query.title, textbook_id: this.$route.query.textbook_id } }">
        <button class="p_button">Return to Test Banks</button>
      </router-link>

      <hr />

      <div id="feedbackContainer">
        <p v-if="loading">Loading feedback...</p>
        <p v-else-if="feedbackList.length === 0">No feedback available.</p>

        <div v-else>
          <div v-for="(entry, index) in feedbackList" :key="index" style="margin-bottom: 1.5em;">
            <p><strong>Question:</strong> {{ entry.question }}</p>
            <ul v-if="entry.feedbacks">
              <li v-for="(fb, i) in entry.feedbacks" :key="i">
                {{ fb.comment }} — <em>{{ fb.username }} ({{ fb.role }})</em>
              </li>
            </ul>
            <p v-else><em>No feedback has been submitted for this question.</em></p>
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
    async fetchQuestionsAndFeedback() {
  try {
    const res = await api.get(`/questions`, {
      params: { textbook_id: this.testbankId }
    });
    console.log('Question API response:', res.data);

    this.questions = res.data.questions;
    console.log('Extracted questions:', this.questions);

    for (const q of this.questions) {
      const feedbackRes = await api.get(`/feedback/question/${q.id}`);
      console.log(`Feedback for question ${q.id}:`, feedbackRes.data);

      if (feedbackRes.data.length > 0) {
        this.feedbackList.push({
          question: q.question_text,
          feedbacks: feedbackRes.data
        });
      }
    }
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
