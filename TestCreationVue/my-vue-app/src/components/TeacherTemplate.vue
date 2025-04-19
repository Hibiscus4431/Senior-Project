<template>
  <div class="theme-teacher">
    <div class="top-banner">
      <div class="banner-title">{{ testOptions.testName || 'Test Template' }}</div>
      <div class="t_banner-actions">
        <router-link to="/TeacherHome" class="t_banner-btn">Home</router-link>
        <router-link to="/" class="t_banner-btn">Log Out</router-link>
      </div>
    </div>

    <div class="button-row">
      <button class="t_button" @click="showBackWarning = true">Back to Draft Pool</button>
      <button class="t_button" @click="exportWarning = true">Export Test to Document</button>
    </div>


    <p class="export-note">
      <strong>Note:</strong> Anything displayed in <span class="green-text">green</span> will not appear on the student
      test but will be included in the test key. <br />
      If selected, a cover page and any uploaded graphic will be added automatically to the exported document.
    </p>

    <p class="export-note">
      <strong>Total Test Time:</strong> {{ totalEstimatedTime }} minutes
    </p>
    <p class="export-note">
      <strong>Total Points:</strong> {{ totalPoints }} points
    </p>
    <hr />

    <!-- Warning Modal -->
    <div class="popup-overlay" v-if="showBackWarning">
      <div class="form-popup-modal">
        <div class="form-container">
          <h2 style="text-align: center;">Warning</h2>
          <p style="text-align: center; font-size: 18px;">
            If you go back to the Draft Pool, any unsaved changes on this page may be lost.
          </p>
          <div class="popup-button-group">
            <button class="btn" @click="confirmBack">Continue</button>
            <button class="btn cancel" @click="showBackWarning = false">Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Export Warning Modal -->
    <div class="popup-overlay" v-if="exportWarning">
      <div class="form-popup-modal">
        <div class="form-container">
          <h2 style="text-align: center;">Confirm Export</h2>
          <p style="text-align: center; font-size: 18px;">
            Exporting will generate a Word document based on the current test setup.
            Any unsaved changes will not be included. Continue?
          </p>
          <div style="display: flex; justify-content: center; gap: 10px; margin-top: 20px;">
            <button class="btn" @click="confirmExport">Yes, Export</button>
            <button class="btn cancel" @click="exportWarning = false">Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Blocked Warning Modal -->
    <div class="popup-overlay" v-if="editBlockedPopup">
      <div class="form-popup-modal">
        <h2>Cannot Edit Question</h2>
        <p>{{ editBlockedReason }}</p>
        <p>A new copy will be made and inserted to your draft pool instead.</p>
        <div class="button-group">
          <button @click="createCopyInstead">Create a Copy</button>
          <button @click="editBlockedPopup = false">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Edit Question Modal -->
    <div class="popup-overlay" v-if="showEditForm">
      <div class="form-popup-modal">
        <form class="form-container" @submit.prevent="saveEditedQuestion">
          <h2>Edit Question</h2>
          <label><b>Chapter Number</b></label>
          <input type="text" v-model="editForm.chapter" required />

          <label><b>Section Number</b></label>
          <input type="text" v-model="editForm.section" required />

          <label><b>Question Text</b></label>
          <input type="text" v-model="editForm.question_text" required />

          <!-- Inside your Edit Question Modal -->
          <label><b>Question Type</b></label>
          <input type="text" :value="editForm.type" disabled />

          <!-- True/False -->
          <div v-if="editForm.type === 'True/False'">
            <label><b>Answer</b></label>
            <select v-model="editForm.true_false_answer">
              <option :value="true">True</option>
              <option :value="false">False</option>
            </select>
          </div>

          <!-- Multiple Choice -->
          <div v-if="editForm.type === 'Multiple Choice'">
            <label><b>Correct Answer</b></label>
            <input type="text" v-model="editForm.correct_option.option_text" />

            <label><b>Incorrect Answers (readonly)</b></label>
            <ul>
              <li v-for="(opt, index) in editForm.incorrect_options" :key="index">{{ opt.option_text }}</li>
            </ul>
          </div>

          <!-- Fill in the Blank -->
          <div v-if="editForm.type === 'Fill in the Blank'">
            <label><b>Blanks</b></label>
            <ul>
              <li v-for="(blank, index) in editForm.blanks" :key="index">
                <input type="text" v-model="blank.correct_text" />
              </li>
            </ul>
          </div>

          <!-- Matching -->
          <div v-if="editForm.type === 'Matching'">
            <label><b>Matching Pairs</b></label>
            <ul>
              <li v-for="(match, index) in editForm.matches" :key="index">
                <input type="text" v-model="match.prompt_text" placeholder="Prompt" />
                <input type="text" v-model="match.match_text" placeholder="Match" />
              </li>
            </ul>
          </div>


          <label><b>Points</b></label>
          <input type="text" v-model="editForm.points" required />

          <label><b>Estimated Time (in minutes)</b></label>
          <input type="text" v-model="editForm.est_time" required />

          <label><b>Grading Instructions</b></label>
          <input type="text" v-model="editForm.grading_instructions" />

          <br /><br />
          <button type="submit" class="btn">Save</button>
          <button type="button" class="btn cancel" @click="showEditForm = false">Cancel</button>
        </form>
      </div>
    </div>





    <div class="question-list-container">
      <draggable v-model="questions" item-key="id" class="drag-list" handle=".drag-handle" @update="saveOrder">
        <template #header></template>

        <template #item="{ element, index }">
          <div class="question-box" :class="{ selected: selectedQuestionId === element.id }"
            @click="toggleQuestionSelection(element.id)">
            <div class="drag-header">
              <span class="drag-handle" title="Drag to reorder">✥</span>
              <h3>{{ index + 1 }}. {{ element.question_text }}</h3>
            </div>

            <!-- Image Preview if available -->
            <div v-if="element.attachment && element.attachment.url" class="question-image-preview">
              <img :src="element.attachment.url" alt="Question Image"
                style="max-width: 100%; max-height: 300px; margin-top: 10px; margin-bottom: 10px;" />
            </div>


            <!-- Multiple Choice Question boxes-->
            <div v-if="element.type === 'Multiple Choice'">
              <ol type="A">
                <li v-for="(opt, i) in shuffleOptions(element)" :key="opt.option_id || i"
                  :class="{ 'correct-answer': opt.is_correct }">
                  {{ opt.option_text }}
                </li>
              </ol>
              <div class="question-type-label">{{ element.type }}</div>
            </div>

            <!-- Fill in the Blank Question boxes-->
            <div v-else-if="element.type === 'Fill in the Blank'">
              <p><strong>Answer:</strong> __________________________</p>
              <p class="correct-answer-display">
                Correct Answer: {{element.blanks.map(b => b.correct_text).join(', ')}}
              </p>
              <div class="question-type-label">{{ element.type }}</div>
            </div>


            <!-- Matching Question boxes-->
            <div v-else-if="element.type === 'Matching'">
              <div class="matching-container">
                <div class="matching-prompts">
                  <h4>Match the following:</h4>
                  <ul>
                    <li v-for="(pair, i) in getShuffledMatches(element)" :key="i">
                      {{ i + 1 }}. {{ pair.prompt_text }}
                    </li>
                  </ul>
                </div>
                <div class="matching-answers">
                  <h4>Answer Bank:</h4>
                  <ul>
                    <li v-for="(text, i) in getShuffledAnswerBank(element)" :key="i">
                      {{ String.fromCharCode(65 + i) }}. {{ text }}
                    </li>
                  </ul>
                </div>
              </div>

              <div class="matching-footer">
                <p class="correct-answer-display">
                  Correct Matches: {{ getMatchingKeyString(element) }}
                </p>


                <div class="question-type-label">{{ element.type }}</div>
              </div>
            </div>



            <!-- True/False -->
            <div v-else-if="element.type === 'True/False'">
              <p><strong>Answer:</strong> __________________________</p>
              <p class="correct-answer-display">
                Correct Answer: {{ element.true_false_answer ? 'True' : 'False' }}
              </p>
              <div class="question-type-label">{{ element.type }}</div>
            </div>



            <!-- Short Answer or Essay -->
            <div v-else-if="element.type === 'Short Answer' || element.type === 'Essay'">
              <p class="correct-answer-display">
                Grading Instructions: {{ element.grading_instructions || 'None provided' }}
              </p>
              <div class="question-type-label">{{ element.type }}</div>
            </div>


            <!-- Other fallback -->
            <div v-else>
              <em>Type: {{ element.type }}</em>
            </div>

            <div v-if="selectedQuestionId === element.id" class="button-group">
              <button @click.stop="editQuestion(element)">Edit</button>
              <button @click.stop="removeFromTest(element.id)">Remove from Test</button>
            </div>


          </div>
        </template>

        <template #footer></template>
      </draggable>


    </div>
  </div>
</template>

<script>
import draggable from 'vuedraggable';
import api from '@/api'; // consistent with your other components
import { saveAs } from 'file-saver';

export default {
  components: { draggable },
  data() {
    const savedOptions = JSON.parse(localStorage.getItem("testOptions") || "{}");

    return {
      questions: [],
      testOptions: {
        testName: savedOptions.testName || this.$route.query.testBankName || "Test Template",
        coverPage: savedOptions.coverPage === true || savedOptions.coverPage === 'true', selectedTemplate: savedOptions.selectedTemplate || "All Questions",
        uploadedImage: savedOptions.uploadedImage || '',
        graphicPreview: savedOptions.graphicPreview || '',
        selectedTypes: this.$route.query.selectedTypes
          ? JSON.parse(this.$route.query.selectedTypes)
          : savedOptions.selectedTypes || [],
      },
      testBankId: this.$route.query.testBankId,
      showBackWarning: false,
      hasUnsavedChanges: true,
      publishWarning: false,
      exportWarning: false,
      selectedQuestionId: null,
      editingQuestionId: null,
      editBlockedPopup: false,
      editBlockedReason: '',
      showEditForm: false,
      editForm: {
        question_text: '',
        chapter: '',
        section: '',
        type: '',
        points: '',
        est_time: '',
        grading_instructions: ''
      }

    };
  },

  mounted() {
    this.fetchQuestions();
    window.addEventListener('beforeunload', this.confirmExit);
  },
  beforeDestroy() {
    window.removeEventListener('beforeunload', this.confirmExit);
  },

  //this looks for the order of questions changing and updates storage
  watch: {
    questions: {
      deep: true,
      handler(newList) {
        const idOrder = newList.map(q => q.id);
        localStorage.setItem(`questionOrder_${this.testBankId}`, JSON.stringify(idOrder));
      }
    }
  },
  computed: {
    totalEstimatedTime() {
      return this.questions.reduce((sum, q) => {
        const time = parseInt(q.est_time, 10);
        return sum + (isNaN(time) ? 0 : time);
      }, 0);
    },
    totalPoints() {
      return this.questions.reduce((sum, q) => {
        const pts = parseFloat(q.default_points);
        return sum + (isNaN(pts) ? 0 : pts);
      }, 0);
    }
  },

  methods: {
    //methods for editing questions==========================================
    async editQuestion(question) {
      try {
        const res = await api.get(`/questions/${question.id}/used_in`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (res.data.is_used) {
          // Question is used in a finalized test
          this.editBlockedReason = `This question is used in a "${res.data.tests[0].status}" test: "${res.data.tests[0].name}".`;
          this.editingQuestionId = question.id;
          this.editBlockedPopup = true;
          return;
        }
        this.editingQuestionId = question.id;
        this.editForm = {
          question_text: question.question_text,
          chapter: question.chapter_number,
          section: question.section_number,
          type: question.type,
          points: question.default_points,
          est_time: question.est_time,
          grading_instructions: question.grading_instructions || '',
          correct_option: question.correct_option || null,
          incorrect_options: question.incorrect_options || [],
          blanks: question.blanks || [],
          matches: question.matches || [],
          true_false_answer: question.true_false_answer
        };


        this.showEditForm = true;

      } catch (err) {
        console.error('Error checking question status:', err);
        alert('Could not verify question status.');
      }
    },
    async createCopyInstead() {
      try {
        // Step 1: Copy the question to the current course
        const res = await api.post(`/questions/${this.editingQuestionId}/copy_to_course`, {
          course_id: this.$route.query.courseId
        }, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        const newQuestionId = res.data.new_question_id;
        if (!newQuestionId) throw new Error("New question ID not returned.");

        // Step 2: Remove the original question from the test bank (backend)
        await api.delete(`/testbanks/${this.testBankId}/questions/${this.editingQuestionId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        // ✅ Remove old question ID from localStorage to keep it out on reload
        const orderKey = `questionOrder_${this.testBankId}`;
        const savedOrder = JSON.parse(localStorage.getItem(orderKey) || "[]");
        const updatedOrder = savedOrder.filter(id => id !== this.editingQuestionId);
        localStorage.setItem(orderKey, JSON.stringify(updatedOrder));


        // Step 3: Add the copied question to the test bank (backend)
        await api.post(`/testbanks/${this.testBankId}/questions`, {
          question_ids: [newQuestionId]
        }, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        // Step 4: Refresh all questions in local state
        await this.fetchQuestions();

        // Step 5: Scroll to and open the new question in edit mode
        this.$nextTick(() => {
          const newQuestion = this.questions.find(q => q.id === newQuestionId);
          if (!newQuestion) {
            alert("Newly copied question not found after refresh.");
            return;
          }

          // Scroll to the question in the DOM (optional, improve UX)
          const el = document.querySelector(`[data-id="${newQuestion.id}"]`);
          if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });

          this.editingQuestionId = newQuestion.id;
          this.selectedQuestionId = newQuestion.id;
          this.editForm = {
            question_text: newQuestion.question_text,
            chapter: newQuestion.chapter_number,
            section: newQuestion.section_number,
            type: newQuestion.type,
            points: newQuestion.default_points,
            est_time: newQuestion.est_time,
            grading_instructions: newQuestion.grading_instructions || '',
            correct_option: newQuestion.correct_option || null,
            incorrect_options: newQuestion.incorrect_options || [],
            blanks: newQuestion.blanks || [],
            matches: newQuestion.matches || [],
            true_false_answer: newQuestion.true_false_answer
          };

          this.editBlockedPopup = false;
          this.showEditForm = true;
        });

      } catch (err) {
        console.error('❌ Failed to create or edit copy:', err);
        alert('An error occurred while replacing the uneditable question.');
      }
    },

    async saveEditedQuestion() {
      try {
        const payload = {
          question_text: this.editForm.question_text,
          chapter_number: this.editForm.chapter,
          section_number: this.editForm.section,
          default_points: parseFloat(this.editForm.points),
          est_time: parseInt(this.editForm.est_time),
          grading_instructions: this.editForm.grading_instructions
        };

        // Type-specific fields
        if (this.editForm.type === 'True/False') {
          payload.true_false_answer = this.editForm.true_false_answer;
        }

        if (this.editForm.type === 'Multiple Choice') {
          payload.options = [
            { option_text: this.editForm.correct_option.option_text, is_correct: true },
            ...this.editForm.incorrect_options.map(opt => ({
              option_text: opt.option_text,
              is_correct: false
            }))
          ];
        }

        if (this.editForm.type === 'Fill in the Blank') {
          payload.blanks = this.editForm.blanks.map(b => ({
            correct_text: b.correct_text
          }));
        }

        if (this.editForm.type === 'Matching') {
          payload.matches = this.editForm.matches.map(pair => ({
            prompt_text: pair.prompt_text,
            match_text: pair.match_text
          }));
        }

        const res = await api.patch(`/questions/${this.editingQuestionId}`, payload, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        alert("✅ Question updated!");
        this.showEditForm = false;
        await this.fetchQuestions(); // Refresh questions from backend

      } catch (err) {
        console.error("❌ Failed to update question:", err);
        alert("Could not update question.");
      }
    },



    //methods for exporting, publishing, and going back to the draft pool
    // finalize the document export
    blobToFile(blob, filename) {
      return new File([blob], filename, {
        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
      });
    },

    //finalize test key before export
    async uploadAnswerKey(testId, keyFile) {
      const formData = new FormData();
      formData.append('file', keyFile);

      try {
        const response = await api.post(`/tests/${testId}/upload_answer_key`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        console.log("✅ Answer key uploaded:", response.data);
      } catch (err) {
        console.error("❌ Failed to upload answer key:", err);
        alert("The answer key could not be saved to the backend.");
      }
    },

    //publish the test
    async publishTest() {
      try {
        const testId = localStorage.getItem('finalizedTestId');

        if (!testId) {
          alert("❌ No finalized test found. Please export the test first.");
          return;
        }

        // Step 1: Publish the finalized test
        await api.post(`/tests/${testId}/publish`, {}, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        alert("✅ Test successfully published!");
        localStorage.removeItem('finalizedTestId');

      } catch (err) {
        console.error("❌ Failed to publish test:", (err.response && err.response.data) || err.message);
        alert("An error occurred while publishing. Check the console.");
      }
    },


    async finalizeTestBeforeExport() {
      try {
        const selectedTemplate = this.testOptions.selectedTemplate || "All Questions";

        const finalizePayload = {
          test_bank_id: parseInt(this.testBankId),
          name: this.testOptions.testName,
          estimated_time: this.totalEstimatedTime > 0 ? this.totalEstimatedTime : 1,
          test_instructions: "",
          course_id: parseInt(this.$route.query.courseId),
          type: selectedTemplate
        };

        // 🔑 If it's not "All Questions", provide question_ids
        if (selectedTemplate !== "All Questions") {
          finalizePayload.question_ids = this.questions.map(q => q.id);
        }

        console.log("🟡 Finalizing test with payload:", finalizePayload);

        const response = await api.post('/tests/finalize', finalizePayload, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (response.status === 201) {
          const testId = response.data.test_id;

          //this needs to be debugged
          // // Upload graphic if present
          // if (this.testOptions.graphicPreview) {
          //   const imageFile = this.dataUrlToFile(this.testOptions.graphicPreview, "resource_image.png");
          //   const formData = new FormData();
          //   formData.append('file', imageFile);

          //   await api.post(`/tests/${testId}/upload_attachment`, formData, {
          //     headers: {
          //       'Content-Type': 'multipart/form-data',
          //       Authorization: `Bearer ${localStorage.getItem('token')}`
          //     }
          //   });
          // }

          return {
            testId,
            questionCount: response.data.question_count
          };
        } else {
          throw new Error("Finalize test failed with non-201 response");
        }

      } catch (err) {
        console.error("❌ Finalize error:", (err.response && err.response.data) || err.message);
        alert("Failed to finalize test. See console for details.");
        throw err;
      }
    },

    // Convert data URL to File object
    dataUrlToFile(dataUrl, filename) {
      const arr = dataUrl.split(',');
      const mime = arr[0].match(/:(.*?);/)[1];
      const bstr = atob(arr[1]);
      let n = bstr.length;
      const u8arr = new Uint8Array(n);
      while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
      }
      return new File([u8arr], filename, { type: mime });
    },


    async confirmExport() {
      this.exportWarning = false;
      try {
        const finalizedMeta = await this.finalizeTestBeforeExport();
        const testId = finalizedMeta.testId;

        // ✅ Save to localStorage or Vue data
        localStorage.setItem('finalizedTestId', testId); // OR use: this.finalizedTestId = testId;

        await this.exportToWord(finalizedMeta);
      } catch (err) {
        console.error("Export canceled due to finalize error");
      }
    },
    confirmPublish() {
      this.publishWarning = false;
      this.publishTest(); // call your existing publish logic
    },

    confirmExit(e) {
      if (this.hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = ''; // For modern browsers to trigger prompt
      }
    },

    confirmBack() {
      this.showBackWarning = false;
      this.goBackTB();
    },

    //function to go back to draft pool
    goBackTB() {
      this.$router.push({
        path: '/TeacherViewTB',
        query: {
          courseId: this.$route.query.courseId,
          courseTitle: this.$route.query.courseTitle,
          testBankId: this.testBankId,
          testBankName: this.$route.query.testBankName
        }
      });

    },
    //methods for question management==========================================
    toggleQuestionSelection(questionId) {
      this.selectedQuestionId = this.selectedQuestionId === questionId ? null : questionId;
    },
    removeFromTest(questionId) {
      if (confirm("Remove this question from the test?")) {
        this.questions = this.questions.filter(q => q.id !== questionId);
        this.selectedQuestionId = null;

        // ✅ Update localStorage to exclude removed ID
        const orderKey = `questionOrder_${this.testBankId}`;
        const savedOrder = JSON.parse(localStorage.getItem(orderKey) || "[]");
        const updatedOrder = savedOrder.filter(id => id !== questionId);
        localStorage.setItem(orderKey, JSON.stringify(updatedOrder));
      }
    },


    //methods for page contents==========================================
    //fetch desired testbank questions
    async fetchQuestions() {
      try {
        const selectedTypes = this.testOptions.selectedTypes || [];

        const params = {
          test_bank_id: this.testBankId
        };

        // Only include 'types' param if not selecting all questions
        if (!selectedTypes.includes("All Questions")) {
          params.types = JSON.stringify(selectedTypes);
        }

        const response = await api.get(`/tests/draft-questions`, {
          params,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        const rawQuestions = response.data.questions || [];
        const savedOrder = localStorage.getItem(`questionOrder_${this.testBankId}`);

        let finalOrdered = [];

        if (savedOrder) {
          const idOrder = JSON.parse(savedOrder);
          const questionMap = new Map(rawQuestions.map(q => [q.id, q]));

          // Preserve order from localStorage
          finalOrdered = idOrder.map(id => questionMap.get(id)).filter(Boolean);

          // Add any newly added questions not in saved order
          rawQuestions.forEach(q => {
            if (!idOrder.includes(q.id)) {
              finalOrdered.push(q);
            }
          });
        } else {
          finalOrdered = rawQuestions;
        }

        // Deep clone to ensure Vue reactivity and clear stale properties
        this.questions = JSON.parse(JSON.stringify(finalOrdered));

        // Clear any cached memoized data like _shuffledAnswers
        this.questions.forEach(q => {
          if (q._shuffledAnswers) delete q._shuffledAnswers;
        });

      } catch (error) {
        console.error("❌ Failed to fetch questions:", error);
      }
    },




    //save order of questions
    saveOrder() {
      const idOrder = this.questions.map(q => q.id);
      localStorage.setItem(`questionOrder_${this.testBankId}`, JSON.stringify(idOrder));
    },

    //randomly assign order for answer choices
    shuffleOptions(question) {
      const options = [...question.incorrect_options, question.correct_option].map(opt => ({
        ...opt, is_correct: !!opt.is_correct
      }));

      // Fisher-Yates shuffle
      for (let i = options.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [options[i], options[j]] = [options[j], options[i]];
      }

      return options;
    },

    shuffleArray(arr) {
      const copy = [...arr];
      for (let i = copy.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [copy[i], copy[j]] = [copy[j], copy[i]];
      }
      return copy;
    },

    getShuffledBlanks(question) {
      return this.shuffleArray(question.blanks || []);
    },

    //shuffle matches terms
    getShuffledMatches(question) {
      const matches = question.matches || [];
      const prompts = matches.map(pair => pair.prompt_text);
      const answers = this.getShuffledAnswerBank(question);
      return prompts.map((prompt, index) => ({
        prompt_text: prompt,
        match_text: answers[index]
      }));
    },

    //shuffle matches answers
    getShuffledAnswerBank(question) {
      // Memoize shuffle on question
      if (!question._shuffledAnswers) {
        const matches = question.matches || [];
        const answers = this.shuffleArray(matches.map(pair => pair.match_text));
        question._shuffledAnswers = answers;
      }
      return question._shuffledAnswers;
    },

    //helper for matches answers
    getMatchingKeyString(question) {
      const shuffledAnswers = this.getShuffledAnswerBank(question);
      return (question.matches || [])
        .map((pair, index) => {
          const matchIndex = shuffledAnswers.findIndex(ans => ans === pair.match_text);
          return `${index + 1} → ${String.fromCharCode(65 + matchIndex)}`;
        })
        .join(', ');
    },

    //export the questions to a document
    async exportToWord(finalizedMeta) {
      const totalPoints = this.questions.reduce((sum, q) => {
        const pts = parseFloat(q.default_points);
        return sum + (isNaN(pts) ? 0 : pts);
      }, 0);

      const totalTime = this.questions.reduce((sum, q) => {
        const time = parseInt(q.est_time, 10);
        return sum + (isNaN(time) ? 0 : time);
      }, 0);

      const confirmedPoints = totalPoints;
      const confirmedTime = this.totalEstimatedTime || totalTime;

      const {
        Document,
        Packer,
        Paragraph,
        TextRun,
        ImageRun,
        Table,
        TableRow,
        TableCell,
        HeadingLevel,
        AlignmentType,
        BorderStyle,
        ThematicBreak,
        WidthType
      } = await import("docx");

      const createHorizontalLine = () => new Paragraph(new ThematicBreak());


      const pageBreak = new Paragraph({ children: [], pageBreakBefore: true });
      //----Cover Page Content-----
      const coverPageContent = () => {
        const cover = [
          new Paragraph({
            text: this.testOptions.testName,
            heading: HeadingLevel.TITLE,
            alignment: AlignmentType.CENTER,
            spacing: { after: 200 },
          }),
          new Paragraph({
            text: "Version: XXXX",
            heading: HeadingLevel.HEADING_1,
            alignment: AlignmentType.CENTER,
            spacing: { after: 200 },
          }),
          new Paragraph({ text: "Name: __________________________", spacing: { after: 400 } }),
          new Paragraph({ text: "Date: __________________________", spacing: { after: 400 } }),
          new Paragraph({ text: "Course: " + (this.$route.query.courseTitle || "N/A") }),
          new Paragraph({
            text: "Time Allowed: " + (this.totalEstimatedTime || "N/A") + " minutes",
            spacing: { after: 400 }
          }),
          createHorizontalLine(),
          new Paragraph({
            text: "Instructions:",
            heading: HeadingLevel.HEADING_2,
            spacing: { after: 100 },
          }),
          ...[
            `This exam is worth ${confirmedPoints} points.`,
            `You have ${confirmedTime || "N/A"} minutes to complete the exam.`,
            "Read each question carefully.",
            "Be sure to answer all questions, do not leave anything blank.",
            "Turn in all work and scratch paper with your exam.",
            "You may not use any external materials unless permitted by the instructor.",
            "This exam is closed-book, closed-notes, and no external devices or help.",
            "Check your work before submitting."
          ].map(instruction => new Paragraph({
            text: instruction,
            bullet: { level: 0 },
            spacing: { after: 100 }
          })),
          pageBreak
        ];

        return cover;
      };

      // ------Test Page-----
      const testContent = async () => {
        const content = [
          new Paragraph({
            text: `${this.testOptions.testName} - Version: XXXX`,
            heading: HeadingLevel.HEADING_1,
            spacing: { after: 300 },
          }),
          new Paragraph({ text: "Name: __________________________", spacing: { after: 400 } }),
          new Paragraph({ text: `Score: ______ / ${confirmedPoints} points`, spacing: { after: 400 } }),
          createHorizontalLine()
        ];

        for (let index = 0; index < this.questions.length; index++) {
          const q = this.questions[index];
          // ✅ Fetch and insert question attachment image
          if (q.attachment && q.attachment.url) {
            try {
              const imageResponse = await fetch(q.attachment.url);
              const imageBuffer = await imageResponse.arrayBuffer();
              const imageBytes = new Uint8Array(imageBuffer);

              content.push(
                new Paragraph({
                  children: [
                    new ImageRun({
                      data: imageBytes,
                      transformation: {
                        width: 500,
                        height: 300
                      }
                    })
                  ],
                  spacing: { after: 100 }
                })
              );
            } catch (err) {
              console.warn(`⚠ Failed to fetch image for question ${index + 1}:`, err);
            }
          };


          //question text
          content.push(
            new Paragraph({
              text: `${index + 1}. ${q.question_text}`,
              spacing: { after: 200 }
            })
          );

          if (q.type === "Multiple Choice") {
            const options = this.shuffleOptions(q);
            options.forEach((opt, i) => {
              content.push(new Paragraph({
                text: `${String.fromCharCode(65 + i)}. ${opt.option_text}`,
                indent: { left: 720 },
                spacing: { after: 100 }
              }));
            });
          } else if (q.type === "True/False") {
            content.push(new Paragraph("True/False: __________________________"));
          } else if (q.type === "Fill in the Blank") {
            content.push(new Paragraph("Blank: _____________________"));
          } else if (q.type === "Short Answer") {
            for (let i = 0; i < 15; i++) content.push(new Paragraph(" "));
          } else if (q.type === "Essay") {
            for (let i = 0; i < 30; i++) content.push(new Paragraph(" "));
          } else if (q.type === "Matching") {
            content.push(new Paragraph({
              spacing: { after: 200 }
            }));

            const shuffledMatches = this.getShuffledMatches(q);
            const answerBank = this.getShuffledAnswerBank(q);

            const tableRows = shuffledMatches.map((pair, i) => {
              const prompt = `${i + 1}. ${pair.prompt_text}`;
              const answer = `${String.fromCharCode(65 + i)}. ${pair.match_text}`;
              return new TableRow({
                children: [
                  new TableCell({
                    width: { size: 50, type: WidthType.PERCENTAGE },
                    children: [
                      new Paragraph({
                        text: prompt,
                        spacing: { after: 150 } // extra spacing below
                      })
                    ],
                    margins: { top: 100, bottom: 100 }
                  }),
                  new TableCell({
                    width: { size: 50, type: WidthType.PERCENTAGE },
                    children: [
                      new Paragraph({
                        text: answer,
                        spacing: { after: 150 }
                      })
                    ],
                    margins: { top: 100, bottom: 100 }
                  })
                ]
              });
            });

            content.push(new Table({
              rows: tableRows,
              width: { size: 100, type: WidthType.PERCENTAGE },
              borders: {
                top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                insideHorizontal: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
                insideVertical: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" }
              }
            }));

            content.push(new Paragraph({ text: " ", spacing: { after: 300 } }));
          }



          content.push(new Paragraph({ text: " ", spacing: { after: 300 } }));
        };

        return content;
      };

      // ----Test Key Content-----
      const keyContent = () => {
        const content = [
          new Paragraph({
            children: [
              new TextRun({
                text: `${this.testOptions.testName} - Test Key`,
                bold: true,
                size: 32,
                color: "FF0000",
              })
            ],
            spacing: { after: 300 }
          })
        ];

        this.questions.forEach((q, index) => {
          let answerText = "";
          if (q.type === "Multiple Choice") {
            const options = this.shuffleOptions(q);
            const correctIndex = options.findIndex(o => o.is_correct);
            answerText = `Correct Answer: ${String.fromCharCode(65 + correctIndex)}. ${options[correctIndex].option_text}`;
          } else if (q.type === "True/False") {
            answerText = `Correct Answer: ${q.true_false_answer ? "True" : "False"}`;
          } else if (q.type === "Fill in the Blank") {
            answerText = `Correct Answer: ${q.blanks.map(b => b.correct_text).join(", ")}`;
          } else if (q.type === "Short Answer" || q.type === "Essay") {
            answerText = `Grading Instructions: ${q.grading_instructions || "None"}`;
          } else if (q.type === "Matching") {
            answerText = `Correct Matches: ${this.getMatchingKeyString(q)}`;
          }

          content.push(
            new Paragraph({
              text: `${index + 1}. ${q.question_text}`,
              spacing: { after: 100 },
            }),
            new Paragraph({
              children: [new TextRun({ text: answerText, color: "FF0000" })],
              spacing: { after: 300 }
            })
          );
        });

        return content;
      };
      // Helper to convert base64 string to ArrayBuffer
      // Utility to convert base64 to Uint8Array (what docx expects)
      const base64ToUint8Array = (base64) => {
        const base64Data = base64.split(',')[1]; // remove the data:image/*;base64, part
        const binaryString = window.atob(base64Data);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        return bytes;
      };

      // Resource Page Content
      const resourceContent = async () => {
        const resourceSection = [];

        if (this.testOptions.graphicPreview) {
          try {
            const base64Data = this.testOptions.graphicPreview.split(',')[1];
            const binaryString = window.atob(base64Data);
            const byteArray = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
              byteArray[i] = binaryString.charCodeAt(i);
            }

            resourceSection.push(
              new Paragraph({ children: [], pageBreakBefore: true }),
              new Paragraph({
                text: "Resource Page",
                heading: HeadingLevel.HEADING_1,
                spacing: { after: 300 }
              }),
              new Paragraph({
                children: [
                  new ImageRun({
                    data: byteArray,
                    transformation: {
                      width: 500,
                      height: 300
                    }
                  })
                ],
                spacing: { after: 300 }
              })
            );
          } catch (err) {
            console.error("⚠ Failed to load image for resource page:", err);
            resourceSection.push(new Paragraph("⚠ Could not load the uploaded image."));
          }
        }

        return resourceSection;
      };



      // Build final documents
      const resourceSection = await resourceContent();

      const testDoc = new Document({
        sections: [{
          properties: {},
          children: []
            .concat(this.testOptions.coverPage ? coverPageContent() : [])
            .concat(await testContent())
            .concat(resourceSection)

        }],
        styles: {
          default: {
            document: {
              run: {
                font: "Arial",
                size: 24  // 12pt (24 half-points)
              }
            }
          }
        }
      });

      const keyDoc = new Document({
        sections: [{
          properties: {},
          children: keyContent()
        }],
        styles: {
          default: {
            document: {
              run: {
                font: "Arial",
                size: 24  // 12pt (24 half-points)
              }
            }
          }
        }
      });

      const [testBlob, keyBlob] = await Promise.all([
        Packer.toBlob(testDoc),
        Packer.toBlob(keyDoc)
      ]);


      const testFile = this.blobToFile(testBlob, `${this.testOptions.testName || "GeneratedTest"}.docx`);
      const keyFile = this.blobToFile(keyBlob, `${this.testOptions.testName || "TestKey"}.key.docx`);

      const testId = finalizedMeta.testId;

      try {
        // Upload the test file as PDF equivalent
        const testForm = new FormData();
        testForm.append('file', testFile);

        await api.post(`/tests/${testId}/upload_pdf`, testForm, {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        // Upload the answer key to its dedicated endpoint
        await this.uploadAnswerKey(testId, keyFile);

      } catch (err) {
        console.error("❌ Upload failed:", err);
        alert("Failed to upload test or answer key.");
      }




      saveAs(testBlob, `${this.testOptions.testName || "GeneratedTest"}.docx`);
      saveAs(keyBlob, `${this.testOptions.testName || "TestKey"}.key.docx`);
    }

  }
};
</script>

<style scoped>
.question-list-container {
  margin: 20px auto;
  max-width: 800px;
}

.question-box {
  background: #f0f8f7;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 8px;
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.1);
}
</style>
