<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherHome.vue -->
<template>
  <div class="theme-teacher">
    <div class="top-banner">
      <div class="banner-title">Course Selection</div>

      <div class="t_banner-actions">
        <router-link to="/" class="t_banner-btn">Log Out</router-link>
      </div>
    </div>
    <div class="center large-paragraph" style="color:#222">
      <div class="page-wrapper">
        <!-- Download all your question data: 
        <div class="button-row">
          <button class="t_button">Download Questions</button>
        </div> -->


        Please select or create a course:

        <div class="button-row">
          <!-- Conditionally render the dropdown or the no courses message -->
          <div class="t_dropdown" v-if="courses.length">
            <button class="t_dropbtn">Select Course</button>
            <div class="t_dropdown-content">
              <!-- Display all course titles in the dropdown -->
              <a v-for="course in courses" :key="course.id" @click="selectCourse(course)">
                {{ course.title }}
              </a>
            </div>
          </div>
          <div v-else>
            No courses available.
          </div>
          <!-- Button to create a new course will always be shown -->
          <router-link to="TeacherNewClass">
            <button class="t_button">Create New Course</button>
          </router-link>
        </div>

        <!-- Test Options Section -->
        <div class="center large-paragraph" style="color:#222">
          Test Options:
          <div class="button-row">
            <button class="t_button" @click="viewPreviousTests">View Previous Tests</button>
            <button class="t_button" @click="chooseTestToPublish">Choose Test to Publish</button>
          </div>

        </div>



        <!-- Finalized Test Popup -->
        <div class="popup-overlay" v-if="showPopup">
          <div class="form-popup-modal">
            <form class="form-container">
              Your Finalized Tests
              <ul style="list-style-type: none; padding-left: 0;">
                <li v-for="test in testFiles" :key="test.test_id">
                  <button v-if="test.download_url && test.hasAnswerKey" class="t_button"
                    @click.prevent="downloadTestAndKey(test)">
                    {{ test.name }}
                  </button>
                </li>
              </ul>
              <button type="button" class="btn cancel" @click="showPopup = false">Close</button>
            </form>
          </div>
        </div>


        <!-- Choose Test to Publish Popup -->
        <div class="popup-overlay" v-if="showPublishSelector">
          <div class="form-popup-modal">
            <form class="form-container" @submit.prevent="publishSelectedTest" style="font-size: 16px;">
              <h1 style="align-items: center;"> Choose a Finalized Test to Publish:</h1>
              <strong>Note:</strong> Any questions on tests that are published can no longer be edited or deleted.
              <br><br>
              <ul style="list-style-type: none; padding-left: 0;">
                <li v-for="test in testFiles" :key="test.test_id" style="margin-bottom: 8px;">
                  <label style="display: flex; align-items: center;">
                    <input type="radio" v-model="selectedTestIdToPublish" :value="test.test_id"
                      style="margin-right: 10px;" />
                    {{ test.name }}
                  </label>
                </li>
              </ul>

              <div style="display: flex; justify-content: center; gap: 10px; margin-top: 20px;">
                <button type="submit" class="btn">Confirm Publish</button>
                <button type="button" class="btn cancel" @click="showPublishSelector = false">Cancel</button>
              </div>
            </form>
          </div>
        </div>



      </div>
    </div>
    <br>
  </div>
</template>


<script>
import api from '@/api'; // <-- your custom Axios instance with token handling
import jwtDecode from 'jwt-decode';
export default {
  name: 'TeacherHome',
  data() {
    return {
      courses: [],
      error: null,
      testFiles: [],
      showPopup: false,
      showPublishSelector: false,
      selectedTestIdToPublish: null
    };
  },
  created() {
    this.fetchCourses();
  },
  methods: {
    // fetch courses from the database
    async fetchCourses() {
      try {
        console.log('Fetching courses...'); // Debugging

        const response = await api.get('/courses', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        console.log('Courses fetched:', response.data); // Debugging
        if (Array.isArray(response.data)) {
          this.courses = response.data.map(course => ({
            id: course.course_id,
            title: course.course_name,
            textbook_id: course.textbook_id
          }));
        } else {
          this.error = 'Failed to fetch course data.';
        }
      } catch (error) {
        console.error('Error fetching course:', error);

        // Check if error has a response from the backend
        if (error.response) {
          this.error = error.response.data.error || error.response.statusText;
        } else {
          this.error = 'Network error or server is not responding.';
        }
      }
    },
    // Handle course selection
    selectCourse(course) {
      // Navigate to the TeacherQuestions page with the selected course's ID and title
      this.$router.push({
        name: 'TeacherQuestions',
        query: {
          courseId: course.id,
          courseTitle: course.title,
          textbook_id: course.textbook_id
        }
      });
    },


    async viewPreviousTests() {
      try {
        const response = await api.get('/tests/final', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        const tests = response.data.final_tests || [];

        const enrichedTests = await Promise.all(tests.map(async test => {
          try {
            const keyRes = await api.get(`/tests/${test.test_id}/answer_key`, {
              headers: {
                Authorization: `Bearer ${localStorage.getItem('token')}`
              }
            });
            test.hasAnswerKey = !!(keyRes.data && keyRes.data.file_url);
          } catch {
            test.hasAnswerKey = false;
          }
          return test;
        }));

        this.testFiles = enrichedTests;
        this.showPopup = true;
      } catch (err) {
        console.error('Failed to fetch final tests:', err);
        alert('Could not load previous tests.');
      }
    },

    async downloadTestAndKey(test) {
      if (!test.download_url) {
        alert('Test file not available for download.');
        return;
      }

      const testLink = document.createElement('a');
      testLink.href = test.download_url;
      testLink.download = '';
      document.body.appendChild(testLink);
      testLink.click();
      document.body.removeChild(testLink);

      try {
        const response = await api.get(`/tests/${test.test_id}/answer_key`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (response.data.file_url) {
          const keyLink = document.createElement('a');
          keyLink.href = response.data.file_url;
          keyLink.download = '';
          document.body.appendChild(keyLink);
          keyLink.click();
          document.body.removeChild(keyLink);
        }
      } catch (err) {
        console.warn(`Failed to download answer key for test ${test.test_id}:`, err);
      }
    },

    async chooseTestToPublish() {
      try {
        const response = await api.get('/tests/final', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        this.testFiles = response.data.final_tests || [];
        this.selectedTestIdToPublish = null;
        this.showPublishSelector = true;
      } catch (err) {
        console.error("Failed to load final tests for publishing:", err);
        alert("Could not load test list.");
      }
    },

    async publishSelectedTest() {
      if (!this.selectedTestIdToPublish) {
        alert("Please select a test to publish.");
        return;
      }

      try {
        await api.post(`/tests/${this.selectedTestIdToPublish}/publish`, {}, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        //alert("✅ Test successfully published!");
        this.showPublishSelector = false;
      } catch (err) {
        console.error("❌ Publish failed:", (err.response && err.response.data) || err.message);
        alert("Failed to publish the selected test.");
      }
    }
  },


};
</script>

<style scoped>
@import '../assets/teacher_styles.css';
</style>