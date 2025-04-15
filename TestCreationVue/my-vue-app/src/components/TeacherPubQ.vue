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
        <div v-for="tb in fullTestbanks" :key="tb.testbank_id" class="published-bank">
          <h3>{{ tb.name }} (Chapter {{ tb.chapter_number }}, Section {{ tb.section_number }})</h3>
          <div v-for="(q, index) in tb.questions" :key="q.id"
            :class="['question-box', { selected: selectedQuestionId === q.id }]" @click="toggleQuestionSelection(q.id)">
            <strong>Question {{ index + 1 }}:</strong> {{ q.question_text }}<br />
            <span><strong>Type:</strong> {{ q.type }}</span><br />
            <span><strong>Chapter:</strong> {{ q.chapter_number || 'N/A' }}</span><br />
            <span><strong>Section:</strong> {{ q.section_number || 'N/A' }}</span><br />

            <div v-if="q.type === 'True/False'">
              <strong>Answer:</strong> {{ q.true_false_answer ? 'True' : 'False' }}
            </div>

            <div v-if="q.type === 'Multiple Choice'">
              <span class="correct-answer">Correct Answer:</span> {{ q.correct_option && q.correct_option.option_text ||
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
              <strong>Essay Instructions:</strong> {{ q.grading_instructions || 'None' }}
            </div>

            <div><strong>Grading Instructions:</strong> {{ q.grading_instructions || 'None' }}</div>

            <!-- ✅ Buttons only visible when box is selected -->
            <div v-if="selectedQuestionId === q.id" class="button-group">
              <button @click.stop="openFeedbackForm(q.id)">Leave Feedback</button>
              <button @click.stop="openTestBankModal(q.id)">Add to Draft Pool</button>
            </div>
          </div>

        </div>
      </div>

      <div v-if="viewing === 'published-tests'">
        <div v-if="fullTestbanks.length === 0" class="center large-paragraph" style="color:#222;">
          No published tests available for this course.
        </div>
        <div v-else></div>
        <div v-for="tb in fullTestbanks" :key="tb.testbank_id" class="published-bank">
          <h3>{{ tb.name }} (Chapter {{ tb.chapter_number }}, Section {{ tb.section_number }})</h3>
          <div v-for="(q, index) in tb.questions" :key="q.id"
            :class="['question-box', { selected: selectedQuestionId === q.id }]" @click="toggleQuestionSelection(q.id)">
            <strong>Question {{ index + 1 }}:</strong> {{ q.question_text }}<br />
            <span><strong>Type:</strong> {{ q.type }}</span><br />
            <span><strong>Chapter:</strong> {{ q.chapter_number || 'N/A' }}</span><br />
            <span><strong>Section:</strong> {{ q.section_number || 'N/A' }}</span><br />

            <div v-if="q.type === 'True/False'">
              <strong>Answer:</strong> {{ q.true_false_answer ? 'True' : 'False' }}
            </div>

            <div v-if="q.type === 'Multiple Choice'">
              <span class="correct-answer">Correct Answer:</span>{{ q.correct_option && q.correct_option.option_text ||
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
              <strong>Essay Instructions:</strong> {{ q.grading_instructions || 'None' }}
            </div>

            <div><strong>Grading Instructions:</strong> {{ q.grading_instructions || 'None' }}</div>

            <!-- ✅ Buttons only visible when box is selected -->
            <div v-if="selectedQuestionId === q.id" class="button-group">
              <button @click.stop="openFeedbackForm(q.id)">Leave Feedback</button>
              <button @click.stop="openTestBankModal(q.id)">Add to Draft Pool</button>
            </div>
          </div>
        </div>

      </div>
    </div>


    <div class="popup-overlay" v-if="showFeedbackForm" @click.self="closeFeedbackForm">
      <div class="form-popup-modal">
        <h2>Leave Feedback</h2>
        <textarea v-model="feedbackText" rows="5" style="width: 100%; padding: 10px;"
          placeholder="Enter your comment here..."></textarea>
        <br /><br />
        <button class="btn" @click="submitFeedback">Submit</button>
        <button class="btn cancel" @click="closeFeedbackForm">Cancel</button>
      </div>
    </div>
    <div v-if="showTestBankModal" class="popup-overlay" @click.self="closeTestBankModal">
      <div class="form-popup-modal">
        <h2>Select a Draft Pool</h2>
        <div v-if="testBanks.length">
          <button v-for="tb in testBanks" :key="tb.testbank_id" class="t_button"
            @click="assignToDraftPool(tb.testbank_id)" style="margin-bottom: 10px; display: block; width: 100%;">
            {{ tb.name }}
          </button>
        </div>
        <button class="btn cancel" @click="closeTestBankModal">Cancel</button>
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
      fullTestbanks: [],
      viewing: '',
      showFeedbackForm: false,
      selectedQuestionIdForFeedback: null,
      feedbackText: '',
      testBanks: [],
      selectedQuestionToAdd: null,
      showTestBankModal: false,
      selectedQuestionId: null,
    };
  },
  mounted() {
    this.courseId = this.$route.query.course_id;
    console.log("Course ID:", this.courseId);
    this.fetchTeacherTestbanks();
  },
  methods: {
    async fetchFeedback() {
      this.viewing = 'published';
      try {
        const res = await api.get(`/resources/full-testbanks?course_id=${this.courseId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        this.fullTestbanks = res.data.testbanks || [];
        console.log("Full published testbanks loaded:", this.fullTestbanks);
      } catch (err) {
        console.error('Failed to load testbanks:', err);
        alert('Could not load published testbanks.');
      }
    },
    openFeedbackForm(questionId) {
      this.selectedQuestionIdForFeedback = questionId;
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
        await api.post('/feedback/create', {
          question_id: this.selectedQuestionIdForFeedback,
          comment_field: this.feedbackText
        }, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        alert('Feedback submitted!');
        this.closeFeedbackForm();
      } catch (error) {
        console.error('Error submitting feedback:', error);
        alert('Failed to submit feedback.');
      }
    },
    async fetchTeacherTestbanks() {
      try {
        const res = await api.get(`/testbanks/teacher?course_id=${this.courseId}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        this.testBanks = res.data.testbanks || [];
      } catch (err) {
        console.error("Failed to load testbanks:", err);
      }
    },

    openTestBankModal(questionId) {
      this.selectedQuestionToAdd = questionId;
      this.showTestBankModal = true;
    },

    closeTestBankModal() {
      this.selectedQuestionToAdd = null;
      this.showTestBankModal = false;
    },

    async assignToDraftPool(testbankId) {
      try {
        await api.post(`/testbanks/${testbankId}/questions`, {
          question_ids: [this.selectedQuestionToAdd]
        }, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });

        alert('Question added to the selected draft pool!');
        this.closeTestBankModal();
      } catch (err) {
        console.error("Failed to add question:", err);
        alert("Could not add question to the selected pool.");
      }
    },
    toggleQuestionSelection(questionId) {
      this.selectedQuestionId = this.selectedQuestionId === questionId ? null : questionId;
    },
    async viewPublishedTests() {
      this.viewing = 'published-tests';
      this.fullTestbanks = [];

      const textbookId = this.$route.query.textbook_id;
      if (!textbookId) {
        console.error("Missing textbook_id in route.");
        return;
      }

      try {
        const testList = await api.get(`/tests/published`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        const publishedTests = (testList.data || []).filter(t => t.textbook_id == textbookId);

        for (const test of publishedTests) {
          const res = await api.get(`/resources/tests/${test.test_id}/questions`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`
            }
          });

          this.fullTestbanks.push({
            testbank_id: test.test_id,
            name: test.name || `Test ${test.test_id}`,
            chapter_number: 'N/A',
            section_number: 'N/A',
            questions: res.data.questions || []
          });
        }

        console.log("Published test questions loaded:", this.fullTestbanks);
      } catch (err) {
        console.error("Failed to load published tests:", err);
        alert("Could not load published test questions.");
      }
    }



  }
};
</script>

<style>
@import '../assets/teacher_styles.css';
</style>
