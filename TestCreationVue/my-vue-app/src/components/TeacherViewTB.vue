<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherViewTB.vue -->
<template>
  <div class="teacher-viewTB-container"> 
  <!-- This is the page where the teacher can see all of their test banks-->
  <div class="center large-heading sticky">
    <h1 id="pageTitle">View Test Banks{{ selectedTestBank }}</h1>
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

    <router-link to="TeacherQuestions">
      <button class="t_button">Return to Question Page</button>
    </router-link><br>

    <router-link to="TeacherNewTest">
      <button class="t_button">Create New Test</button>
    </router-link>

    <button class="t_button" @click="edit">View Drafts</button>
    <br>
    <hr>

    <!--Test bank questions will be generated here-->
    <div id="questionsContainer">
      <p v-for="question in selectedQuestions" :key="question">{{ question }}</p>
    </div>
  </div>
  <!-- contents of popup-->
  <div class="form-popup" id="test_view">
    <form action="#" class="form-container">
      Please select draft version to view:
      <!--Figure out how to list the old test versions-->
      <!--When version is clicked it will send them to test view page-->
      <button type="submit" class="btn">Save</button>
      <button type="button" class="btn cancel" @click="closeForm">Close</button>
    </form>
  </div>
  </div>
</template>

<script>
export default {
  name: 'TeacherViewTB',
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
      document.getElementById('test_view').style.display = 'block';
    },
    closeForm() {
      document.getElementById('test_view').style.display = 'none';
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
</style>