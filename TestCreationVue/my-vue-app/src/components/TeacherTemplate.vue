<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherTemplate.vue -->
<template>
  <div class="teacher-template-container">
    <div class="center large-heading">
      <h1>{{ testOptions.testName || 'Test Template' }}</h1>

      <p style="font-size: 20px; color: whitesmoke;">
        from: {{ testBankName }}
      </p>
    </div>

    <div class="center" style="margin-bottom: 20px;">
      <button class="t_button" @click="publishTest">Publish Test Draft</button>
      <button class="t_button" @click="exportToWord">Export Test</button>
      <button class="t_button" @click="showNavigateWarning = true">
        Go Back to Draft Pool
      </button>

      <!-- Confirmation Popup -->
      <div class="popup-overlay" v-if="showConfirmPopup" @click.self="cancelConfirm">
        <div class="form-popup-modal">
          <div class="form-container">
            <h2 style="text-align: center;">Confirm Action</h2>
            <p style="text-align: center; font-size: 18px;">
              Once you
              <strong>{{ confirmAction === 'publish' ? 'publish' : 'export' }}</strong>
              this test draft, the questions can no longer be edited.<br />
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



    </div>
    <hr>
    <!--This div is for questions to display and all its contents will be exporting with button-->
    <div class="center large-paragraph" id="contentToExport">
      Questions will be generated here
      <br>
      1. Question Information
      <br>
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
      confirmAction: '', // either 'publish' or 'export'
      showNavigateWarning: false,
    };
  },
  mounted() {
    try {
      const testOptions = JSON.parse(localStorage.getItem('testOptions'));
      if (testOptions) {
        this.testOptions = testOptions;
      }

      // Load route query data
      this.courseId = this.$route.query.courseId || '';
      this.courseTitle = this.$route.query.courseTitle || '';
      this.testBankId = this.$route.query.testBankId || '';
      this.testBankName = this.$route.query.testBankName || '';
    } catch (error) {
      console.error('Failed to load test options or query params:', error);
    }
  },

  methods: {
    //Function to publish the test doc
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

    // /*note to self: 
    // -when making js function to display questions
    //     include <br> tags to separate questions and <br> x2 for sections
    // -figure out how to make section headings dynamically
    // */

    // /*note to self:
    // -seperate js function to move questions and sections around on html page 
    //     while also keeping the content inside the id="content" div
    // -use drag and drop feature to move questions and sections around
    // */
  }
}
</script>

<style scoped>
@import '../assets/teacher_styles.css';

.teacher-template-container {
  background-color: #43215a;
  font-family: Arial, sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>