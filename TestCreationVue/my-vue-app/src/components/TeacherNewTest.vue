<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherNewTest.vue -->
<template>
  <div class = "teacher-newTest-container">
    <div class="center large-heading sticky">
      <h1>Create Test</h1>
    </div>
    <div class="center large-paragraph">
      <div class="box" style="width: 250px;">
        <!--Can't figure out why text is off center-->
        <label class="container">Add Cover Page
          <input type="checkbox" v-model="coverPage">
          <span class="checkmark"></span>
        </label>
      </div>
      <br>
      <button class="t_button" @click="edit">Template Options</button>
      <br>
      <button class="t_button" @click="importGraphic">Add Embedded Graphic</button>
      <br>
      <div class="box">
        <label for="est">Time Allowed:</label>
        <input type="text" id="est" v-model="timeAllowed" style="height:20px;"><br>
      </div>
      <br>
      <button class="t_button" @click="generateTest">Generate Test</button>
    </div>

    <!-- file input element -->
    <input type="file" id="fileInput" style="display: none;" @change="handleFileUpload">

    <!-- contents of popup-->
    <div class="form-popup" id="test_view">
      <form class="form-container">
        Please select which template to use<br>
        <label class="r_container">Default
          <input type="radio" value="Default" v-model="selectedTemplate" name="template">
          <span class="checkmark"></span>
        </label>
        <label class="r_container">Mixed
          <input type="radio" value="Mixed" v-model="selectedTemplate" name="template">
          <span class="checkmark"></span>
        </label>
        <!--figure out different option types-->
        <label class="r_container">ETC
          <input type="radio" value="ETC" v-model="selectedTemplate" name="template">
          <span class="checkmark"></span>
        </label>

        <button type="button" class="btn" @click="saveTemplate">Save</button>
        <button type="button" class="btn cancel" @click="closeForm">Close</button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TeacherNewTest',
  data() {
    return {
      coverPage: true,
      selectedTemplate: 'Default',
      timeAllowed: '',
      uploadedImage: '',
      showPopup: false
    };
  },
  methods: {
    importGraphic() {
      document.getElementById('fileInput').click();
    },
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        console.log('File selected:', file.name);
        // Store the file name in localStorage --> change to saving to database later
        localStorage.setItem('uploadedImage', file.name);
        this.uploadedImage = file.name;
      }
    },
    generateTest() {
      const testOptions = {
        coverPage: this.coverPage,
        selectedTemplate: this.selectedTemplate,
        uploadedImage: this.uploadedImage,
        timeAllowed: this.timeAllowed
      };

      localStorage.setItem('testOptions', JSON.stringify(testOptions));
      this.$router.push({ path: 'TeacherTemplate' });
    },
    edit() {
      document.getElementById('test_view').style.display = 'block';
    },
    closeForm() {
      document.getElementById('test_view').style.display = 'none';
    },
    saveTemplate() {
      this.closeForm();
    }
  }
};
</script>

<style scoped>
@import '../assets/teacher_styles.css';
.teacher-newTest-container {
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