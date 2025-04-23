<template>
  <div class="theme-teacher">
    <div class="top-banner">
      <div class="banner-title">Community Resources</div>
      <div class="t_banner-actions">
        <router-link to="/TeacherHome" class="t_banner-btn">Home</router-link>
        <router-link to="/" class="t_banner-btn">Log Out</router-link>
      </div>
    </div>

    <div class="center large-paragraph" style="color:#222;">
      Please select an option to view:
      <div class="button-row">
        <button class="t_button" @click="viewPublishedTests">Published Tests</button>
        <button class="t_button" @click="fetchFeedback">View Community Draft Pools</button>
      </div>

      <div v-if="viewing === 'published'">
        <div v-if="loadingPublished" class="center large-paragraph" style="color: #555;">
          Loading published draft pools...
        </div>

        <div v-else-if="fullTestbanks.length === 0" class="center large-paragraph" style="color: #222;">
          No published draft pools available for this course.
        </div>

        <div v-else>
          <div v-for="tb in fullTestbanks" :key="tb.testbank_id" class="published-bank">
            <h3>{{ tb.name }} (Chapter {{ tb.chapter_number }}, Section {{ tb.section_number }})</h3>
            <div v-for="(q, index) in tb.questions" :key="q.id"
              :class="['question-box', { selected: selectedQuestionId === q.id }]"
              @click="toggleQuestionSelection(q.id)">
              <strong>Question {{ index + 1 }}:</strong> {{ q.question_text }}<br />
              <span><strong>Type:</strong> {{ q.type }}</span><br />
              <span><strong>Chapter:</strong> {{ q.chapter_number || 'N/A' }}</span><br />
              <span><strong>Section:</strong> {{ q.section_number || 'N/A' }}</span><br />

              <div v-if="q.type === 'True/False'">
                <strong>Answer:</strong> {{ q.true_false_answer ? 'True' : 'False' }}
              </div>

              <div v-if="q.type === 'Multiple Choice'">
                <span class="correct-answer">Correct Answer:</span> {{ q.correct_option && q.correct_option.option_text
                  ||
                  'Not specified' }}
                <br />
                <p><strong>Other Options:</strong></p>
                <ul>
                  <li v-for="(option, i) in q.incorrect_options" :key="i" class="incorrect-answer">
                    {{ option.option_text }}
                  </li>
                </ul>
              </div>


              <div v-if="q.type === 'Matching'">
                <strong>Pairs:</strong>
                <ul>
                  <li v-for="(pair, i) in q.matches" :key="i">
                    {{ pair.prompt_text }} - {{ pair.match_text }}
                  </li>
                </ul>
              </div>

              <div v-if="q.type === 'Fill in the Blank'">
                <strong>Correct Answers:</strong>
                <ul>
                  <li v-for="(blank, i) in q.blanks" :key="i">{{ blank.correct_text }}</li>
                </ul>
              </div>

              <div v-if="q.type === 'Short Answer'">
                <strong>Answer:</strong> {{ q.answer || 'Not provided' }}
              </div>

              <div v-if="q.type === 'Essay'">
              </div>

              <div><strong>Grading Instructions:</strong> {{ q.grading_instructions || 'None' }}</div>

              <!-- Feedback Section -->
              <div v-if="q.feedback && q.feedback.length" class="feedback-section">
                <strong>Feedback:</strong>
                <!-- Show average rating if available -->
                <div v-if="q.feedback && q.feedback.length">
                  <p v-if="q.class_average !== undefined">
                    <strong>Average Question Rating:</strong> {{ q.class_average.toFixed(1) }}/100
                  </p>
                </div>

                <ul>
                  <li v-for="(f, i) in q.feedback" :key="i">
                    <em>{{ f.username }} ({{ f.role }})</em>: "{{ f.comment_field }}"
                    <span v-if="f.rating !== undefined"> - Class Average: {{ f.rating }}/100</span>
                  </li>

                </ul>
              </div>
              <div v-if="q.attachment || (q.attachments && q.attachments.length)">
                <strong>Attachments:</strong>
                <ul>
                  <li v-if="q.attachment">
                    <img :src="q.attachment.url" :alt="q.attachment.name" style="max-width: 100%; margin-top: 10px;" />
                  </li>
                </ul>
              </div>

              <!-- Buttons only visible when box is selected -->
              <div v-if="selectedQuestionId === q.id" class="button-group">
                <button @click.stop="openFeedbackForm(q.id)">Leave Feedback</button>
                <button @click.stop="openTestBankModal(q.id)">Add to Draft Pool</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Published Test Questions -->
      <div v-if="viewing === 'published-tests'">

        <div v-if="loadingPublished" class="center large-paragraph" style="color: #555;">
          Loading published tests...
        </div>

        <div v-else-if="fullTestbanks.length === 0" class="center large-paragraph" style="color: #222;">
          No published tests available for this course.
        </div>

        <div v-else>
          <div v-for="tb in fullTestbanks" :key="tb.testbank_id" class="published-bank">
            <h3>{{ tb.name }} (Chapter {{ tb.chapter_number }}, Section {{ tb.section_number }})</h3>
            <div v-for="(q, index) in tb.questions" :key="q.id"
              :class="['question-box', { selected: selectedQuestionId === q.id }]"
              @click="toggleQuestionSelection(q.id)">
              <strong>Question {{ index + 1 }}:</strong> {{ q.question_text }}<br />
              <span><strong>Type:</strong> {{ q.type }}</span><br />
              <span><strong>Chapter:</strong> {{ q.chapter_number || 'N/A' }}</span><br />
              <span><strong>Section:</strong> {{ q.section_number || 'N/A' }}</span><br />

              <div v-if="q.type === 'True/False'">
                <strong>Answer:</strong> {{ q.true_false_answer ? 'True' : 'False' }}
              </div>
              <div v-if="q.type === 'Multiple Choice'">
                <span class="correct-answer">Correct Answer:</span> {{ (q.correct_option &&
                  q.correct_option.option_text) || 'Not specified' }}

                <br />
                <p><strong>Other Options:</strong></p>
                <ul>
                  <li v-for="(option, i) in q.incorrect_options" :key="i" class="incorrect-answer">
                    {{ option.option_text }}
                  </li>
                </ul>
              </div>
              <div v-if="q.type === 'Matching'">
                <strong>Pairs:</strong>
                <ul>
                  <li v-for="(pair, i) in q.matches" :key="i">
                    {{ pair.prompt_text }} - {{ pair.match_text }}
                  </li>
                </ul>
              </div>
              <div v-if="q.type === 'Fill in the Blank'">
                <strong>Correct Answers:</strong>
                <ul>
                  <li v-for="(blank, i) in q.blanks" :key="i">{{ blank.correct_text }}</li>
                </ul>
              </div>
              <div v-if="q.type === 'Short Answer'">
                <strong>Answer:</strong> {{ q.answer || 'Not provided' }}
              </div>
              <div v-if="q.type === 'Essay'">
              </div>

              <div><strong>Grading Instructions:</strong> {{ q.grading_instructions || 'None' }}</div>

              <div v-if="q.feedback && q.feedback.length" class="feedback-section">
                <strong>Feedback:</strong>

                <!-- Show average rating if available -->
                <div v-if="q.feedback && q.feedback.length">
                  <p v-if="q.class_average !== undefined">
                    <strong>Average Question Rating:</strong> {{ q.class_average.toFixed(1) }}/100
                  </p>
                </div>

                <ul>
                  <li v-for="(f, i) in q.feedback" :key="i">
                    <em>{{ f.username }} ({{ f.role }})</em>: "{{ f.comment_field }}"
                    <span v-if="f.rating !== undefined"> - Class Average: {{ f.rating }}/100</span>
                  </li>

                </ul>
              </div>
              <div v-if="q.attachment || (q.attachments && q.attachments.length)">
                <strong>Attachments:</strong>
                <ul>
                  <li v-if="q.attachment">
                    <img :src="q.attachment.url" :alt="q.attachment.name" style="max-width: 100%; margin-top: 10px;" />
                  </li>
                </ul>
              </div>

              <div v-if="selectedQuestionId === q.id" class="button-group">
                <button @click.stop="openFeedbackForm(q.id)">Leave Feedback</button>
                <button @click.stop="openTestBankModal(q.id)">Add to Draft Pool</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>


    <!-- Popups -->
    <div class="popup-overlay" v-if="showFeedbackForm">
      <div class="form-popup-modal">
        <h2>Leave Feedback</h2>
        <textarea v-model="feedbackText" rows="5" style="width: 100%;"
          placeholder="Enter your comment here..."></textarea>
        <br /><br />
        <label><strong>Please enter class average for this question: (0–100):</strong></label>
        <input type="number" v-model="feedbackRating" min="0" max="100" style="width: 100%;" />

        <br /><br />
        <div class="button-row">
          <button class="btn" @click="submitFeedback">Submit</button>
          <button class="btn cancel" @click="closeFeedbackForm">Cancel</button>
        </div>
      </div>
    </div>

    <div class="popup-overlay" v-if="showTestBankModal">
      <div class="form-popup-modal">
        <h2>Select draft pool to add question to:</h2>
        <div style="display: flex; flex-direction: column; align-items: flex-start;">
          <div v-for="tb in unpublishedDraftPools" :key="tb.testbank_id" style="margin-bottom: 10px; width: 100%;">
            <button class="t_button" style="width: 100%;" @click="assignToDraftPool(tb.testbank_id)">
              {{ tb.name }}
            </button>
          </div>
          <div style="width: 100%;">
            <button type="button" class="btn cancel" style="width: 100%; margin-top: 20px;" @click="closeTestBankModal">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>


  </div>
</template>

<script>
import api from '@/api';

export default {
  name: 'TeacherPubQ',
  data() {
    return {
      courseId: '',
      textbookId: '',
      fullTestbanks: [],
      viewing: '',
      showFeedbackForm: false,
      selectedQuestionIdForFeedback: null,
      feedbackText: '',
      testBanks: [],
      selectedQuestionToAdd: null,
      showTestBankModal: false,
      selectedQuestionId: null,
      loadingPublished: false,
      feedbackRating: ''
    };
  },
  mounted() {
    this.courseId = this.$route.query.course_id;
    this.fetchCourseTextbook();
    this.fetchTeacherTestbanks();
  },
  computed: {
    unpublishedDraftPools() {
      return this.testBanks.filter(tb => !tb.is_published);
    }
  },
  methods: {

    async fetchFeedback() {
      this.viewing = 'published';
      this.loadingPublished = true;
      try {
        const res = await api.get(`/resources/full-testbanks?course_id=${this.courseId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        this.fullTestbanks = res.data.testbanks || [];
        console.log("Full published testbanks loaded:", this.fullTestbanks);

        for (const tb of this.fullTestbanks) {
          for (const q of tb.questions) {
            await this.loadFeedbackForQuestion(q);

            console.log("Fetched questions:", tb.questions);
            if (q.attachment && !q.attachments) {
              q.attachments = [q.attachment];
            }
          }
        }

      } catch (err) {
        console.error('Failed to load testbanks:', err);
        alert('Could not load published testbanks.');
      }
      finally {
        this.loadingPublished = false;
      }
    },
    async fetchCourseTextbook() {
      try {
        const res = await api.get(`/courses/${this.courseId}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        this.textbookId = res.data.textbook_id;
        console.log("Fetched textbook ID:", this.textbookId);
      } catch (err) {
        console.error("Failed to fetch course textbook:", err);
      }
    },
    async viewPublishedTests() {
      this.viewing = 'published-tests';
      this.fullTestbanks = [];
      this.loadingPublished = true;

      try {
        // Step 1: Get textbook ID if not already set
        // Step 1: Always fetch textbook ID based on courseId
        const courseRes = await api.get(`/courses/${this.courseId}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        this.textbookId = courseRes.data.textbook_id;


        // Step 2: Get all courses that use the same textbook
        // Step 2: Fetch all published tests
        const testListRes = await api.get('/tests/published', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });

        const allPublishedTests = testListRes.data || [];

        const publishedTests = allPublishedTests.filter(t =>
          parseInt(t.textbook_id) === parseInt(this.textbookId)
        );

        console.log("🧪 Filtered published tests by textbook:", publishedTests);


        console.log("🧪 Filtered published tests:", publishedTests);

        // Step 4: Load questions for each test
        for (const test of publishedTests) {
          try {
            const res = await api.get(`/resources/tests/${test.test_id}/questions`, {
              headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
            });

            const questions = res.data.questions || [];

            for (const q of questions) {
              await this.loadFeedbackForQuestion(q);

              if (q.attachment && !q.attachments) {
                q.attachments = [q.attachment];
              }
            }

            this.fullTestbanks.push({
              testbank_id: test.test_id,
              name: test.name || `Test ${test.test_id}`,
              chapter_number: 'N/A',
              section_number: 'N/A',
              questions
            });

          } catch (err) {
            console.error(`❌ Failed to fetch questions for test ID ${test.test_id}`, err);
          }
        }

      } catch (err) {
        console.error("❌ Failed to load published tests:", err);
        alert("Failed to load published tests.");
      } finally {
        this.loadingPublished = false;
      }
    },
    async fetchTeacherTestbanks() {
      try {
        const res = await api.get(`/testbanks/teacher?course_id=${this.courseId}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        this.testBanks = res.data.testbanks || [];
      } catch (err) {
        console.error("Failed to load teacher testbanks:", err);
      }
    },
    toggleQuestionSelection(questionId) {
      this.selectedQuestionId = this.selectedQuestionId === questionId ? null : questionId;
    },
    openFeedbackForm(id) {
      this.selectedQuestionIdForFeedback = id;
      this.feedbackText = '';
      this.showFeedbackForm = true;
    },
    closeFeedbackForm() {
      this.selectedQuestionIdForFeedback = null;
      this.feedbackText = '';
      this.showFeedbackForm = false;
    },
    async submitFeedback() {
      try {
        console.log("Submitting feedback:", {
          question_id: this.selectedQuestionIdForFeedback,
          comment_field: this.feedbackText,
          rating: this.feedbackRating
        });

        await api.post('/feedback/create', {
          question_id: this.selectedQuestionIdForFeedback,
          comment_field: this.feedbackText,
          rating: this.feedbackRating || null
        }, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        this.closeFeedbackForm();
      } catch (err) {
        console.error("Error submitting feedback:", err);
        alert("Failed to submit feedback.");
      }
    },
    openTestBankModal(id) {
      this.selectedQuestionToAdd = id;
      this.showTestBankModal = true;
    },
    closeTestBankModal() {
      this.selectedQuestionToAdd = null;
      this.showTestBankModal = false;
    },
    async assignToDraftPool(testbankId) {
      const courseId = this.$route.query.course_id;
      if (!courseId || !this.selectedQuestionToAdd) {
        console.error("Missing courseId or selectedQuestionToAdd");
        return;
      }

      try {
        // Step 1: Copy question into the teacher's course
        const copyRes = await api.post('/resources/questions/copy', {
          question_id: this.selectedQuestionToAdd,
          course_id: courseId
        });

        const newQuestionId = copyRes.data.new_question_id;

        // Step 2: Link to draft pool
        await api.post(`/testbanks/${testbankId}/questions`, {
          question_ids: [newQuestionId]
        });

        this.closeTestBankModal();
      } catch (err) {
        console.error("❌ Failed to assign question to draft pool:", err);
      }
    }

    ,
    async loadFeedbackForQuestion(q) {
      try {
        const res = await api.get(`/feedback/question/${q.id}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });

        const feedbackList = res.data.feedback || [];
        q.feedback = feedbackList.map(f => ({
          ...f,
          comment_field: f.comment || f.comment_field,  // ensure compatibility
        }));

        q.newRating = ''; // default for new rating

        // Assign class average to each feedback entry so we can show it
        if (res.data.class_average !== null) {
          q.class_average = res.data.class_average;
        }
      } catch (err) {
        console.error(`Failed to load feedback for question ${q.id}`, err);
      }
    },
    async submitRating(questionId, rating) {
      try {
        await api.post('/feedback/create', {
          question_id: questionId,
          rating: rating
        }, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });

        alert("Rating submitted!");
        const q = this.fullTestbanks.flatMap(tb => tb.questions).find(q => q.id === questionId);
        if (q) await this.loadFeedbackForQuestion(q); // refresh feedback

      } catch (err) {
        console.error(`Error submitting rating for question ${questionId}:`, err);
        alert("Failed to submit rating.");
      }
    }

  }
};
</script>

<style scoped>
@import '../assets/teacher_styles.css';

.btn.cancel {
  background-color: red !important;
  color: white !important;
  font-weight: bold;
  border: none;
  padding: 12px 20px;
  /* ⬅️ make it taller */
  border-radius: 8px;
  font-size: 16px;
  transition: background-color 0.2s ease;
}
</style>
