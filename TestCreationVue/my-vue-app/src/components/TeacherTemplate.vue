<template>
  <div class="theme-teacher">
    <div class="top-banner">
      <div class="banner-title">{{ testOptions.testName || 'Test Template' }}</div>
      <div class="t_banner-actions">
        <router-link to="/TeacherHome" class="t_banner-btn">Home</router-link>
        <router-link to="/" class="t_banner-btn">Log Out</router-link>
      </div>
    </div>

    <div class="center button-row">
      <button class="t_button" @click="publishTest">Publish Test Draft</button>

      <button class="t_button" @click="exportToWord">Export Test</button>

      <button class="t_button" @click="showNavigateWarning = true">
        Go Back to Draft Pool
      </button>
    </div>

    <!-- Confirmation Popup -->
    <div class="popup-overlay" v-if="showConfirmPopup" @click.self="cancelConfirm">
      <div class="form-popup-modal">
        <div class="form-container">
          <h2 style="text-align: center;">Confirm Action</h2>
          <p style="text-align: center; font-size: 18px;">
            Once you <strong>{{ confirmAction === 'publish' ? 'publish' : 'export' }}</strong> this test draft,
            the questions can no longer be edited.<br />
            <strong>This action cannot be undone.</strong><br /><br />
            Do you want to continue?
          </p>
          <button class="btn" @click="handleConfirm">Yes, Continue</button>
          <button class="btn cancel" @click="cancelConfirm">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Navigate Warning Popup -->
    <div class="popup-overlay" v-if="showNavigateWarning" @click.self="showNavigateWarning = false">
      <div class="form-popup-modal">
        <div class="form-container">
          <h2 style="text-align: center;">Leave This Page?</h2>
          <p style="text-align: center; font-size: 18px;">
            Any changes made on this page will be <strong>lost</strong> if you go back.<br />
            Are you sure you want to return to the Draft Pool?
          </p>
          <button class="btn" @click="navigateBack">Yes, Go Back</button>
          <button class="btn cancel" @click="showNavigateWarning = false">Cancel</button>
        </div>
      </div>
    </div>

    <hr />

    <!-- This div is for questions to display and all its contents will be exporting with button -->
    <div class="center large-paragraph" id="contentToExport">
      Questions will be generated here
      <br />
      1. Question Information
      <br />
    </div>
  </div>
</template>

<script>
import htmlDocx from 'html-docx-js/dist/html-docx';

export default {
  name: 'TeacherTemplate',
  data() {
    return {
      testOptions: {
        coverPage: false,
        timeAllowed: '',
        selectedTemplate: '',
        uploadedImage: '',
        testName: ''
      },
      courseId: '',
      courseTitle: '',
      testBankId: '',
      testBankName: '',
      showConfirmPopup: false,
      confirmAction: '',
      showNavigateWarning: false,
    };
  },
  async mounted() {
  try {
    const testOptions = JSON.parse(localStorage.getItem('testOptions'));
    if (testOptions) this.testOptions = testOptions;

    this.courseId = this.$route.query.courseId || '';
    this.courseTitle = this.$route.query.courseTitle || '';
    this.testBankId = this.$route.query.testBankId || '';
    this.testBankName = this.$route.query.testBankName || '';

    const response = await api.get(`/testbanks/${this.testBankId}/questions`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    });

    const allQuestions = response.data.questions || [];

    // Apply frontend filtering logic
    this.filteredQuestions = this.filterQuestionsByTemplate(
      allQuestions,
      this.testOptions.selectedTemplate
    );

    this.populateQuestionsIntoTemplate(this.filteredQuestions);

  } catch (error) {
    console.error('Error loading test template data:', error);
  }
},
  methods: {
    filterQuestionsByTemplate(questions, template) {
    if (template === 'All Questions') return questions;

    if (template === 'Multiple Choice') {
      return questions.filter(q =>
        ['Multiple Choice', 'True/False', 'Matching'].includes(q.type)
      );
    }

    if (template === 'Short Answer/Essay') {
      return questions.filter(q =>
        ['Short Answer', 'Essay', 'Fill in the Blank'].includes(q.type)
      );
    }

    return [];
  },

  populateQuestionsIntoTemplate(filtered) {
    const content = document.getElementById('contentToExport');
    content.innerHTML = ''; // clear any existing

    filtered.forEach((q, index) => {
      const qHTML = `
        <p><strong>Q${index + 1}:</strong> ${q.question_text}<br>
        <strong>Type:</strong> ${q.type}<br>
        <strong>Chapter:</strong> ${q.chapter_number || 'N/A'}<br>
        <strong>Section:</strong> ${q.section_number || 'N/A'}<br>
        <strong>Points:</strong> ${q.default_points || 0}<br>
        <strong>Estimated Time:</strong> ${q.est_time || 'N/A'} minutes</p><hr>
      `;
      content.insertAdjacentHTML('beforeend', qHTML);
    });
  }
},


    publishTest() {
      this.confirmAction = 'publish';
      this.showConfirmPopup = true;
    },
    exportToWord() {
      this.confirmAction = 'export';
      this.showConfirmPopup = true;
    },
    handleConfirm() {
      this.showConfirmPopup = false;
      if (this.confirmAction === 'export') {
        const content = document.getElementById('contentToExport').innerHTML;
        const converted = htmlDocx.asBlob(content);
        const link = document.createElement('a');
        link.href = URL.createObjectURL(converted);
        const fileName = this.testOptions.testName
          ? this.testOptions.testName.replace(/\s+/g, '_') + '.docx'
          : 'TestTemplate.docx';
        link.download = fileName;
        link.click();
      }
      this.confirmAction = '';
    },
    cancelConfirm() {
      this.showConfirmPopup = false;
      this.confirmAction = '';
    },
    navigateBack() {
      this.showNavigateWarning = false;
      this.$router.push({
        path: '/TeacherViewTB/' + this.testBankId,
        query: {
          courseId: this.courseId,
          courseTitle: this.courseTitle,
          testBankName: this.testBankName
        }
      });
    }
};
</script>

<style scoped>
@import '../assets/teacher_styles.css';

.teacher-template-container {
  background-color: #43215a;
  font-family: Arial, sans-serif;
  min-height: 100vh;
  padding-bottom: 40px;
}
</style>