<!-- filepath: c:\Users\laure\Senior-Project\TestCreationVue\my-vue-app\src\components\PubViewTB.vue -->
<template>
  <div>
    <div class="center large-heading sticky">
      <h1 id="pageTitle">View Test Banks</h1>
    </div>
    <div class="center large-paragraph">
      <!--It might be easier to make this a drop down option in question page-->
      <div class="dropdown">
        <button class="dropbtn">Select Test Bank</button>
        <div class="dropdown-content">
          <a href="#" @click="selectTestBank('Bank 1')">Bank 1</a>
          <a href="#" @click="selectTestBank('Bank 2')">Bank 2</a>
          <a href="#" @click="selectTestBank('Bank 3')">Bank 3</a>
        </div>
      </div>

      <router-link to="PubQuestions">
        <button class="button">Return to Question Page</button>
      </router-link><br>

      <hr>

      <!--Test bank questions will be generated here-->
      <div id="questionsContainer">
        <p v-for="question in selectedQuestions" :key="question">{{ question }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PublisherViewTB',
  data() {
    return {
      showPopup: false,
      selectedTestBank: '',
      questions: {
        'Bank 1': ['Question 1 from Bank 1', 'Question 2 from Bank 1', 'Question 3 from Bank 1'],
        'Bank 2': ['Question 1 from Bank 2', 'Question 2 from Bank 2', 'Question 3 from Bank 2'],
        'Bank 3': ['Question 1 from Bank 3', 'Question 2 from Bank 3', 'Question 3 from Bank 3']
      }
    };
  },
  computed: {
    selectedQuestions() {
      return this.questions[this.selectedTestBank] || [];
    }
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
    }
  }
};
</script>

<style scoped>
@import '../assets/publisher_styles.css';
</style>