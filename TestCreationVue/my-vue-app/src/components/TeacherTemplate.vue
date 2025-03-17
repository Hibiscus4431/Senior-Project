<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherTemplate.vue -->
<template>
    <div class = "teacher-template-container">
      <div class="center large-heading">
        <h1>Test Template</h1>
      </div>
      
    <!--This div is for questions to display and all its contents will be exporting with button-->
    <div class="center large-paragraph" id = "contentToExport">
        Questions will be generated here
        <br>
        testing pt 2
    </div>
      <div class="center large-paragraph">
  
        <p>Cover Page: <span>{{ testOptions.coverPage ? 'Yes' : 'No' }}</span></p>
        <p>Time Allowed: <span>{{ testOptions.timeAllowed }}</span></p>
        <p>Selected Template: <span>{{ testOptions.selectedTemplate }}</span></p>
        <p>Uploaded Image: <span>{{ testOptions.uploadedImage ? testOptions.uploadedImage : 'No image uploaded' }}</span></p>
      </div>
      
    <div class="center large-paragraph">
        <button class="button" @click="exportToWord">Export to Word</button>
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
          uploadedImage: ''
        }
      };
    },
    mounted() {
      try {
      const testOptions = JSON.parse(localStorage.getItem('testOptions'));
      if (testOptions) {
        this.testOptions = testOptions;
      }
    } catch (error) {
      console.error('Failed to load test options from localStorage:', error);
    }
    },
  
    methods: {
  
        //new fucntion to export the content of the webpage to a word document
        exportToWord() {
            const content = document.getElementById('contentToExport').innerHTML;
            const converted = htmlDocx.asBlob(content);
            const link = document.createElement('a');
            link.href = URL.createObjectURL(converted);
            link.download = 'TestTemplate.docx';
            link.click();
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
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
  </style>