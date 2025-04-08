<template>
    <div class="pub-feedback-container">
      <div class="center large-heading sticky">
        <h1 id="pageTitle">Test Bank Feedback</h1>
      </div>
  
      <div class="center large-paragraph">
        <router-link to="PubQuestions">
          <button class="p_button">Return to Question Page</button>
        </router-link>
  
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
      testbankId: null
    };
  },
  mounted() {
    this.testbankId = this.$route.params.testbank_id;
    console.log('Viewing feedback for Test Bank ID:', this.testbankId);

    // You can now use this.testbankId to fetch data from your backend
    // Example:
    // api.get(`/feedback?testbank_id=${this.testbankId}`).then(...)
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
  