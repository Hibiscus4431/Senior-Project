<!-- filepath: c:\Users\laure\Senior-Project\TestCreationVue\my-vue-app\src\components\PubViewTB.vue -->
<template>
  <div class="pub-viewTB-container">
    <div class="center large-heading sticky">
      <h1 id="pageTitle">View Test Banks - {{ selectedTestBank }}</h1>
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
        <button class="p_button">Return to Question Page</button>
      </router-link><br>
      <router-link :to="{ name: 'PubViewFeedback', params: { testbank_id: selectedTestBankId } }">
        <button class="p_button">View Test Bank Feedback</button>
      </router-link>

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


.pub-viewTB-container {
  background-color: #17552a;
  font-family: Arial, sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.dropbtn {
  background-color: rgb(48, 191, 223);
  color: black;
  padding: 10px;
  font-size: 20px;
  border: none;
}

.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-content {
  display: none;
  position: absolute;
  background-color: #f1f1f1;
  min-width: 160px;
  box-shadow: 0px 8px 16px 0px rgba(0, 0, 0, 0.2);
  z-index: 1;
}

.dropdown-content a {
  color: black;
  padding: 10px 15px;
  text-decoration: none;
  display: block;
}

.dropdown-content a:hover {
  background-color: rgb(48, 191, 223);
}

.dropdown:hover .dropdown-content {
  display: block;
}

.dropdown:hover .dropbtn {
  background-color: rgb(40, 151, 176);
}
</style>