<template>
  <div class="theme-teacher">
    <div class="top-banner">
      <div class="banner-title">Testbank Selection</div>
      <div class="t_banner-actions">
        <router-link to="/TeacherHome" class="t_banner-btn">Home</router-link>
        <router-link to="/" class="t_banner-btn">Log Out</router-link>
      </div>
    </div>

    <div class="center large-paragraph" style="color:#222;">
      Please select an option to view:
      <div class="button-row">
        <button class="t_button" @click="viewPublishedTests">Published Tests</button>
        <button class="t_button" @click="fetchFeedback">Publisher Feedback</button>
      </div>

      <div v-if="viewing === 'publisher'" class="center large-paragraph" style="color:#222;">
        <h3>Questions from Published Testbanks</h3>
        <ul>
          <li v-for="(q, index) in publisherQuestions" :key="index">
            <strong>Question {{ index + 1 }}:</strong> {{ q.question_text }}<br>
            <em>Type:</em> {{ q.type }}<br>
            <em>Chapter:</em> {{ q.chapter_number }}, Section: {{ q.section_number }}
          </li>
        </ul>
      </div>

    </div>
  </div>
</template>

<script>
import api from '@/api';

export default {
  name: 'TeacherPubQ',
  data() {
    return {
      textbookId: '',
      viewing: '',
      publisherQuestions: []
    };
  },
  mounted() {
    this.textbookId = this.$route.query.textbook_id;
    console.log("Viewing feedback for textbook ID:", this.textbookId);
  },
  methods: {
    async fetchFeedback() {
      this.viewing = 'publisher';
      this.publisherQuestions = [];

      try {
        // Step 1: Get published testbanks
        const bankRes = await api.get(`/testbanks/published?textbook_id=${this.textbookId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        const testbanks = bankRes.data.testbanks || [];

        // Step 2: For each testbank, get its questions
        for (const tb of testbanks) {
          const qRes = await api.get(`/testbanks/${tb.testbank_id}/questions`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`
            }
          });

          const questions = qRes.data.questions || [];
          this.publisherQuestions.push(...questions);
        }

      } catch (error) {
        console.error('Failed to load questions from published testbanks:', error);
        alert('Failed to load questions.');
      }
    }
  }
};
</script>

<style scoped>
@import '../assets/teacher_styles.css';
</style>
