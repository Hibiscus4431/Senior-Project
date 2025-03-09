<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherTemplate.vue -->
<template>
    <div>
      <div class="center large-heading">
        <h1>Test Template</h1>
      </div>
      <div class="center large-paragraph">
        Questions will be generated here
  
        <p>Cover Page: <span>{{ testOptions.coverPage ? 'Yes' : 'No' }}</span></p>
        <p>Time Allowed: <span>{{ testOptions.timeAllowed }}</span></p>
        <p>Selected Template: <span>{{ testOptions.selectedTemplate }}</span></p>
        <p>Uploaded Image: <span>{{ testOptions.uploadedImage ? testOptions.uploadedImage : 'No image uploaded' }}</span></p>
      </div>
    </div>
  </template>
  
  <script>
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
    }
  };
  </script>
  
  <style scoped>
  @import './teacher_styles.css';
  </style>