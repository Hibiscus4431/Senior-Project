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
  
        <router-link to="PubViewTB">
          <button class="p_button">Return to Test Banks</button>
        </router-link>
  
        <hr>
  
        <div id="feedbackContainer">
          <p v-if="feedbackList.length === 0">No feedback available.</p>
          <ul v-else>
            <li v-for="(item, index) in feedbackList" :key="index">
              <strong>{{ item.testBank }}:</strong> {{ item.comment }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
  name: 'PubViewFeedback',
  data() {
    return {
      feedbackList: [],
      testbankId: null,
      selectedTestBank: this.$route.query.name || 'No Test Bank Selected'
    };
  },
  mounted() {
  this.testbankId = this.$route.params.testbank_id;
  console.log('Viewing feedback for Test Bank ID:', this.testbankId);

  // Fetch feedback
  fetch(`/api/feedback?testbank_id=${this.testbankId}`)
    .then(res => res.json())
    .then(data => {
      this.feedbackList = data;
    });

  // Fetch testbank name
  fetch(`/api/testbank/${this.testbankId}`)
    .then(res => res.json())
    .then(data => {
      this.selectedTestBank = data.name;
    });
}
};

  </script>
  
  <style scoped>
  @import '../assets/publisher_styles.css';
  
  .pub-feedback-container {
    background-color: #17552a;
    font-family: Arial, sans-serif;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }
  </style>
  