<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherQuestions.vue -->
<template>
  <div class="theme-teacher">
    <div class="top-banner">
      <div class="banner-title">{{ courseTitle }}</div>

      <div class="t_banner-actions">
        <router-link to="/TeacherHome" class="t_banner-btn">Home</router-link>
        <router-link to="/" class="t_banner-btn">Log Out</router-link>
      </div>
    </div>

    <div class="page-wrapper">
      <div class="button-row">
        <div class="t_dropdown">
          <button class="t_dropbtn">
            {{ selectedTestBank ? selectedTestBank.name : 'Select Draft Pool' }}
          </button>
          <div class="t_dropdown-content">
            <a v-for="tb in testBanks" :key="tb.testbank_id" href="#" @click.prevent="selectTestBank(tb)">
              {{ tb.name }}
            </a>
          </div>
        </div>
        <router-link :to="{ path: '/TeacherNewTB', query: { courseId: courseId } }">
          <button class="t_button">New Draft Pool</button>
        </router-link>
        <button class="t_button" @click="importTest">Import Test</button>

        <div class="t_dropdown">
          <button class="t_dropbtn">Question Type</button>
          <div class="t_dropdown-content">
            <a href="#" @click="selectQuestionType('True/False')">True/False</a>
            <a href="#" @click="selectQuestionType('Multiple Choice')">Multiple Choice</a>
            <a href="#" @click="selectQuestionType('Matching')">Matching</a>
            <a href="#" @click="selectQuestionType('Fill in the Blank')">Fill in the Blank</a>
            <a href="#" @click="selectQuestionType('Short Answer')">Short Answer</a>
            <a href="#" @click="selectQuestionType('Essay')">Essay</a>

          </div>
        </div>

        <!--button to edit course info-->
        <button class="t_button" @click="showCourseEditPopup = true">Edit Course Info</button>

        <button class="t_button" @click="edit">New Question</button>
        <router-link :to="{
          name: 'TeacherPubQ',
          query: {
            course_id: courseId,
            textbook_id: textbookId
          }
        }">
          <button class="t_button">Community Resources</button>
        </router-link>
        <div id="selectedQuestionType" style="color: #222" class="center large-paragraph">{{ selectedQuestionType }}
        </div>
      </div>

      <hr>
    </div>


  <ul>
    <div v-for="(question, index) in questions" :key="index"
      :class="['question-box', { selected: selectedQuestionId === question.id }]"
      @click="toggleQuestionSelection(question.id)">
      <strong>Question {{ index + 1 }}:</strong> {{ question.text }}<br>
      <span><strong>Type:</strong> {{ question.type }}</span><br>
      <span><strong>Chapter:</strong> {{ question.chapter || 'N/A' }}</span><br>
      <span><strong>Section:</strong> {{ question.section || 'N/A' }}</span><br>
      <span><strong>Points:</strong> {{ question.points }}</span><br>
      <span><strong>Estimated Time:</strong> {{ question.time }} minutes</span><br>

      <div v-if="question.type === 'True/False'"><strong>Answer:</strong> {{ question.answer ? 'True' : 'False' }}
      </div>
      <div v-if="question.type === 'Multiple Choice'">
        <strong>Correct Answer:</strong> {{ question.correctOption && question.correctOption.option_text ||
          'Not specified' }}<br>
        <p><strong>Other Options:</strong></p>
        <ul>
          <li v-for="(option, i) in question.incorrectOptions" :key="i" class="incorrect-answer">{{ option.option_text
          }}</li>
        </ul>
      </div>
      <!-- <div v-if="question.type === 'Short Answer'">
          <strong>Answer:</strong> {{ question.answer || 'Not provided' }}
        </div> -->
      <div v-if="question.type === 'Fill in the Blank'">
        <strong>Correct Answer(s):</strong>
        <ul>
          <li v-for="(blank, i) in question.blanks" :key="i">{{ blank.correct_text }}</li>
        </ul>
      </div>
      <div v-if="question.type === 'Matching'">
        <strong>Pairs:</strong>
        <ul>
          <li v-for="(pair, i) in question.pairs" :key="i">{{ pair.term }} - {{ pair.definition }}</li>
        </ul>
      </div>
      <div v-if="question.image_url">
        <p><strong>Attached Image:</strong></p>
        <img :src="question.image_url" alt="Question Attachment:"
          style="max-width: 100%; max-height: 400px; margin-bottom: 10px;" />
      </div>
      <span><strong>Grading Instructions:</strong> {{ question.instructions || 'None' }}</span><br>

      <div v-if="selectedQuestionId === question.id" class="button-group">
        <button @click.stop="editQuestion(question)">Edit</button>
        <button @click.stop="deleteQuestion(question.id)">Delete</button>
        <button @click.stop="openAddToTestBank(question.id)">Add to Draft Pool</button>
      </div>
    </div>
  </ul>


  <!-- Add to Test Bank Modal -->
  <div class="popup-overlay" v-show="showAddToTBModal" @click.self="closeAddToTBModal">
    <div class="form-popup-modal">
      <h2>Select draft pool to add question to:</h2>
      <div style="display: flex; flex-direction: column; align-items: flex-start;">
        <div v-for="tb in testBanks" :key="tb.testbank_id" style="margin-bottom: 10px; width: 100%;">
          <button class="t_button" style="width: 100%;" @click="assignQuestionToTestBank(tb.testbank_id)">
            {{ tb.name }}
          </button>
        </div>
        <div class="form-container" style="width: 100%;">
          <button type="button" class="btn cancel" style="width: 100%;" @click="closeAddToTBModal">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>

  <input type="file" id="fileInput" style="display: none;" @change="handleFileUpload">

  <!-- Popup Overlay -->
  <div class="popup-overlay" v-show="showForm" @click.self="closeForm">
    <div class="form-popup-modal">
      <form class="form-container" @submit.prevent="handleQuestionSave">
        <h1>{{ editingQuestionId ? 'Edit Question' : 'New Question' }}</h1>

        <label><b>Chapter Number</b></label>
        <input type="text" v-model="chapter" required />

        <label><b>Section Number</b></label>
        <input type="text" v-model="section" required />

        <label><b>Question Type</b><br /></label>
        <div v-if="!editingQuestionId">
          <select v-model="selectedQuestionType" required>
            <option disabled value="">Select a type</option>
            <option>True/False</option>
            <option>Multiple Choice</option>
            <option>Matching</option>
            <option>Fill in the Blank</option>
            <option>Short Answer</option>
            <option>Essay</option>
          </select>
        </div>
        <div v-else>
          <input type="text" :value="selectedQuestionType" disabled />
        </div>

        <br /><br />
        <label><b>Question Text</b></label>
        <input type="text" v-model="question" required />

        <div v-if="selectedQuestionType === 'True/False'">
          <label><b>Answer</b></label>
          <select v-model="answer">
            <option value="True">True</option>
            <option value="False">False</option>
          </select>
        </div>

        <div v-if="selectedQuestionType === 'Multiple Choice'">
          <label><b>Correct Answer</b></label>
          <input type="text" v-model="answer" />
          <label><b>Incorrect Answer Choices (comma-separated)</b></label>
          <input type="text" v-model="answerChoices" />
        </div>

        <div v-if="selectedQuestionType === 'Matching'">
          <label><b>Matching Pairs</b></label>
          <div v-for="(pair, index) in matchingPairs" :key="index">
            <input type="text" v-model="pair.term" placeholder="Term" />
            <input type="text" v-model="pair.definition" placeholder="Definition" />
            <button type="button" @click="removePair(index)">Remove</button>
          </div>
          <button type="button" @click="addPair">Add Pair</button>
        </div>

        <div v-if="selectedQuestionType === 'Fill in the Blank'">
          <label><b>Correct Answer</b></label>
          <input type="text" v-model="answer" />
        </div>

        <!-- <div v-if="selectedQuestionType === 'Short Answer'">
            <label><b>Answer</b></label>
            <input type="text" v-model="answer" />
          </div> -->

        <div v-if="selectedQuestionType === 'Essay'"></div>

        <br />
        <label><b>Points Worth</b></label>
        <input type="text" v-model="points" required />

        <label><b>Estimated Time (in minutes)</b></label>
        <input type="text" v-model="time" required />

        <label><b>Grading Instructions</b></label>
        <input type="text" v-model="instructions" required />

        <!-- Show Upload Only When Creating -->
        <div v-if="!editingQuestionId">
          <label><b>Upload Image</b></label>
          <input type="file" @change="handleImageUpload" accept="image/*" />
          <img v-if="imagePreview" :src="imagePreview" alt="Preview" style="max-width: 100%;" />
        </div>

        <!-- Show Existing Image on Edit -->
        <div v-if="editingQuestionId && imagePreview">
          <p><strong>Attached Image:</strong></p>
          <img :src="imagePreview" alt="Attached Image"
            style="max-width: 100%; max-height: 300px; margin-bottom: 10px;" />
        </div>

        <br /><br />
        <button type="submit" class="btn">Save</button>
        <button type="button" class="btn cancel" @click="closeForm">Close</button>
      </form>
    </div>
  </div>

  <!-- Course Edit Popup -->
  <div class="popup-overlay" v-if="showCourseEditPopup" @click.self="showCourseEditPopup = false">
    <div class="form-popup-modal">
      <form class="form-container" @submit.prevent="saveCourseInfo">
        <h1>Edit Course Info</h1>

        <label><b>Course Title</b></label>
        <input type="text" v-model="editCourseTitle" required />

        <label><b>Course Number</b></label>
        <input type="text" v-model="editCourseNumber" required />

        <br />
        <button type="submit" class="btn">Save</button>
        <button type="button" class="btn cancel" @click="showCourseEditPopup = false">Cancel</button>
      </form>
    </div>
  </div>
  </div>

</template>

<script>
import api from '@/api';

export default {
  name: 'TeacherQuestions',
  data() {
    return {
      courseTitle: this.$route.query.courseTitle || 'Untitled Course',
      courseId: this.$route.query.courseId || null,
      textbookId: this.$route.query.textbook_id,
      chapter: '',
      section: '',
      question: '',
      reference: '',
      answer: '',
      answerChoices: '',
      points: '',
      time: '',
      instructions: '',
      image: '',
      imagePreview: '',
      selectedQuestionType: '',
      matchingPairs: [], // Array to store matching pairs for matching question type
      questions: [], // Initialize questions as an empty array
      selectedQuestionId: null, // To store the ID of the selected question for editing
      editingQuestionId: null, // To store the ID of the question being edited
      showForm: false,
      selectedTestbank: null,
      testBanks: [], // Array to store testbank options
      showCourseEditPopup: false,
      editCourseTitle: this.$route.query.courseTitle || '',
      editCourseNumber: '',
      showAddToTBModal: false,
      questionToAddToTB: null,
      oldMCOptionIds: [] // ✅ Restored: used for tracking MC option deletions
    };
  },
  mounted() {
    const testbankId = this.$route.params.id;
    console.log("Viewing testbank:", testbankId);
    this.loadTestbanks();

    // Set selectedTestBank from query if provided
    if (this.$route.query.testBankName) {
      this.selectedTestBank = { name: this.$route.query.testBankName };
    }
  },

  methods: {
    //functions to add question to test bank
    openAddToTestBank(questionId) {
      this.questionToAddToTB = questionId;
      this.showAddToTBModal = true;
    },
    closeAddToTBModal() {
      this.questionToAddToTB = null;
      this.showAddToTBModal = false;
    },
    async assignQuestionToTestBank(testbankId) {
      if (!this.questionToAddToTB) return;
      try {
        await api.post(`/testbanks/${testbankId}/questions`, {
          question_ids: [this.questionToAddToTB]
        }, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });


        alert('Question successfully added to testbank!');
        this.closeAddToTBModal();
      } catch (error) {
        console.error('Failed to add question to testbank:', error);
        alert('Failed to add question.');
      }
    },
    //functions to edit course info
    openCourseEditPopup() {
      const titleParts = this.courseTitle.trim().split(' ');
      this.editCourseNumber = titleParts.length > 1 ? titleParts.pop() : '';
      this.editCourseTitle = titleParts.join(' ');
      this.showCourseEditPopup = true;
    },

    async saveCourseInfo() {
      try {
        const response = await api.patch(`/courses/${this.courseId}`, {
          course_name: this.editCourseTitle,
          course_number: this.editCourseNumber
        }, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        const newTitle = `${this.editCourseTitle} ${this.editCourseNumber}`.trim();
        this.courseTitle = newTitle;
        document.title = newTitle;
        this.showCourseEditPopup = false;
        alert('Course info updated successfully.');
      } catch (error) {
        console.error('Failed to update course:', error);
        alert('Failed to update course.');
      }
    },


    async loadTestbanks() {
      try {
        const response = await api.get(`/testbanks/teacher?course_id=${this.courseId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          },
        });

        this.testBanks = response.data.testbanks;
      } catch (error) {
        console.error("Failed to load teacher testbanks:", error);
      }
    },
    selectTestBank(tb) {
      this.selectedTestBank = tb;
      this.selectedTestbankId = tb.value;
      this.$router.push({
        name: 'TeacherViewTB',
        params: { id: tb.testbank_id },
        query: {
          courseId: this.courseId,
          courseTitle: this.courseTitle,
          testBankName: tb.name
        }
      }); // ✅ closes $router.push properly
    },

    //function to fetch questions from the database based on selected question type
    async fetchQuestions(type) {
      this.selectedQuestionType = type;
      try {
        const response = await api.get(`/questions`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          },
          params: {
            course_id: this.$route.query.courseId,
            type: type
          }
        });

        console.log('Questions fetched:', response.data);

        if (Array.isArray(response.data.questions)) {
          this.questions = response.data.questions.map((question) => {
            // Common base
            const base = {
              text: question.question_text,
              type: question.type,
              points: question.default_points,
              id: question.id,
              instructions: question.grading_instructions || '',
              time: question.est_time,
              chapter: question.chapter_number,
              section: question.section_number,
              image_url: question.attachment && question.attachment.url ? question.attachment.url : '' // ✅ Fixed
            };

            // Extend based on type
            switch (question.type) {
              case 'True/False':
                return {
                  ...base,
                  answer: question.true_false_answer
                };
              case 'Multiple Choice':
                return {
                  ...base,
                  correctOption: question.correct_option || null,
                  incorrectOptions: question.incorrect_options || []
                };


              case 'Matching':
                return {
                  ...base,
                  pairs: (question.matches || []).map(pair => ({
                    match_id: pair.match_id,
                    term: pair.prompt_text,
                    definition: pair.match_text
                  }))

                };
              case 'Fill in the Blank':
                return {
                  ...base,
                  blanks: question.blanks || [],
                  instructions: question.grading_instructions || ''
                };

              case 'Short Answer':
                return {
                  ...base,
                  answer: question.answer || ''
                };
              case 'Essay':
                return {
                  ...base,
                  instructions: question.instructions || ''
                };
              default:
                return base;
            }
          });
        } else {
          this.questions = [];
        }

      } catch (error) {
        console.error('Error fetching questions:', error);
        this.questions = [];
      }
    },
    //function to display questions fetched
    displayQuestionType(type) {
      this.selectedQuestionType = `Selected Question Type: ${type}`;
    },
    created() {
      console.log('Query Parameters:', this.$route.query);
    },

    importTest() {
      document.getElementById('fileInput').click();
    },
    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) {
        alert("No file selected.");
        return;
      }
      const formData = new FormData();
      formData.append('file', file);

      try {
        //Phase 1: Uplod QTI file
        const uploadResponse = await api.post('/qti/upload', formData, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'multipart/form-data'
          }
        });
        const file_path = uploadResponse.data.file_path;
        console.log('File uploaded successfully:', file_path);

        //Phase 1.B: Create import record
        const importResponse = await api.post('/qti/import', { file_path }, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          }
        });
        const import_id = importResponse.data.import_id;
        console.log('QTI import created. Import ID:', import_id);

        //Phase 3: save imported questions to the database
        const saveResponse = await api.post(`qti/save/${import_id}`, {
          course_id: this.courseId
        }, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          }
        });
        alert(saveResponse.data.message || 'Questions imported successfully!');
        console.log('Questions imported successfully:', saveResponse.data);

        //refrsh the question list
        this.fetchQuestions(this.selectedQuestionType);
      }
      catch (error) {
        console.error('QTI import Failed:', error);
        alert('Failed to upload file. Please try again.');
      }
    },
    async handleQuestionSave() {
      try {
        let postData;
        let config;
        const editingQuestion = this.questions.find(q => q.id === this.editingQuestionId);
        const isEditing = !!this.editingQuestionId;

        const commonFields = {
          question_text: this.question,
          default_points: parseInt(this.points),
          est_time: parseInt(this.time),
          chapter_number: this.chapter,
          section_number: this.section,
          grading_instructions: this.instructions,
          type: this.selectedQuestionType,
          source: 'manual',
          course_id: this.courseId
        };

        let options = [];
        if (this.selectedQuestionType === 'Multiple Choice') {
          const incorrectChoices = this.answerChoices
            .split(',')
            .map(c => c.trim())
            .filter(Boolean);

          const correctAnswerText = this.answer.trim();
          if (!correctAnswerText) {
            alert("Correct answer cannot be empty.");
            return;
          }

          options.push({ option_text: correctAnswerText, is_correct: true });
          incorrectChoices.forEach(choice => {
            options.push({ option_text: choice, is_correct: false });
          });

          if (!options.some(opt => opt.is_correct)) {
            alert("Multiple Choice questions must have at least one correct answer.");
            return;
          }
        }

        if (this.image) {
          postData = new FormData();
          postData.append('file', this.image);
          for (const [key, val] of Object.entries(commonFields)) {
            postData.append(key, val);
          }

          switch (this.selectedQuestionType) {
            case 'True/False':
              postData.append('true_false_answer', this.answer === 'True');
              break;
            case 'Multiple Choice':
              postData.append('options', JSON.stringify(options));
              if (isEditing && this.oldMCOptionIds.length > 0) {
                postData.append('to_delete', JSON.stringify(this.oldMCOptionIds));
              }
              break;
            case 'Matching':
              postData.append('matches', JSON.stringify(this.matchingPairs.map(p => ({ prompt_text: p.term, match_text: p.definition }))));
              if (isEditing && editingQuestion) {
                const oldMatchIds = (editingQuestion.pairs || []).map(p => p.match_id);
                postData.append('to_delete', JSON.stringify(oldMatchIds));
              }
              break;
            case 'Fill in the Blank':
              postData.append('blanks', JSON.stringify([{ correct_text: this.answer }]));
              if (isEditing && editingQuestion) {
                const oldBlankIds = (editingQuestion.blanks || []).map(b => b.blank_id);
                postData.append('to_delete', JSON.stringify(oldBlankIds));
              }
              break;
            case 'Short Answer':
              postData.append('answer', this.answer);
              break;
            case 'Essay':
              postData.append('grading_instructions', this.instructions);
              break;
          }

          config = {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`,
              'Content-Type': 'multipart/form-data'
            }
          };
        } else {
          postData = { ...commonFields };

          switch (this.selectedQuestionType) {
            case 'True/False':
              postData.true_false_answer = this.answer === 'True';
              break;
            case 'Multiple Choice':
              postData.options = options;
              if (isEditing && this.oldMCOptionIds.length > 0) {
                postData.to_delete = this.oldMCOptionIds;
              }
              break;
            case 'Matching':
              postData.matches = this.matchingPairs.map(p => ({ prompt_text: p.term, match_text: p.definition }));
              if (isEditing && editingQuestion) {
                const oldMatchIds = (editingQuestion.pairs || []).map(p => p.match_id);
                postData.to_delete = oldMatchIds;
              }
              break;
            case 'Fill in the Blank':
              postData.blanks = [{ correct_text: this.answer }];
              if (isEditing && editingQuestion) {
                const oldBlankIds = (editingQuestion.blanks || []).map(b => b.blank_id);
                postData.to_delete = oldBlankIds;
              }
              break;
            case 'Short Answer':
              postData.answer = this.answer;
              break;
            case 'Essay':
              postData.grading_instructions = this.instructions;
              break;
          }

          config = {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`
            }
          };
        }

        if (isEditing) {
          await api.patch(`/questions/${this.editingQuestionId}`, postData, config);
        } else {
          await api.post('/questions', postData, config);
        }

        alert('Question saved successfully!');
        this.closeForm();
        this.resetForm();
        this.fetchQuestions(this.selectedQuestionType);
      } catch (err) {
        let serverMsg = 'Something went wrong.';
        if (err && err.response && err.response.data) {
          serverMsg = err.response.data.error || err.response.data.message || serverMsg;
        }
        alert('Save failed: ' + serverMsg);
        console.error('Error saving question:', err);
      }
    },

    selectQuestionType(type) {
      this.selectedQuestionType = `Selected Question Type: ${type}`;
      this.fetchQuestions(type);
    },
    edit() {
      this.resetForm(); // Clear old data
      this.showForm = true;
    },
    closeForm() {
      this.showForm = false;
    },
    addPair() {
      this.matchingPairs.push({ term: '', definition: '' });
    },
    removePair(index) {
      this.matchingPairs.splice(index, 1);
    },

    handleImageUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.image = file;  // ✅ This was the missing link

        const reader = new FileReader();
        reader.onload = (e) => {
          this.imagePreview = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    },
    resetForm() {
      this.chapter = '';
      this.section = '';
      this.question = '';
      this.reference = '';
      this.answer = '';
      this.answerChoices = '';
      this.points = '';
      this.time = '';
      this.instructions = '';
      this.image = '';
      this.imagePreview = '';
      this.matchingPairs = [];
      this.selectedQuestionType = '';
      this.editingQuestionId = null;
      this.image = '';
      this.imagePreview = '';

    },

    editQuestion(question) {
      this.editingQuestionId = question.id;
      this.question = question.text;
      this.chapter = question.chapter;
      this.section = question.section;
      this.points = question.points;
      this.time = question.time;
      this.instructions = question.instructions;
      this.answer = question.answer || '';
      this.selectedQuestionType = question.type;

      if (question.type === 'Multiple Choice') {
        this.answer = (question.correctOption && question.correctOption.option_text) || '';
        this.answerChoices = (question.incorrectOptions || []).map(opt => opt.option_text).join(', ');
        this.oldMCOptionIds = [];
        if (question.correctOption && question.correctOption.option_id) {
          this.oldMCOptionIds.push(question.correctOption.option_id);
        }
        if (Array.isArray(question.incorrectOptions)) {
          question.incorrectOptions.forEach(opt => {
            if (opt.option_id) this.oldMCOptionIds.push(opt.option_id);
          });
        }
      } else if (question.type === 'Matching') {
        this.matchingPairs = (question.pairs || []).map(pair => ({
          term: pair.term,
          definition: pair.definition
        }));
      }
      this.imagePreview = question.image_url || '';
      this.image = null; // block file re-upload on edit
      this.showForm = true;
      const el = document.getElementById('q_edit');
      if (el && el.style) {
        el.style.display = 'block';
      }
    },


    //functions to delete questions
    toggleQuestionSelection(questionId) {
      this.selectedQuestionId = this.selectedQuestionId === questionId ? null : questionId;
    },

    async deleteQuestion(id) {
      if (confirm('Are you sure you want to delete this question?')) {
        try {
          await api.delete(`/questions/${id}`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`
            }
          });
          this.questions = this.questions.filter(q => q.id !== id);
          alert('Question deleted.');
        } catch (err) {
          console.error(err);
          alert('Failed to delete question.');
        }
      }
    }
  }
};
</script>


<style scoped>
@import '../assets/teacher_styles.css';
</style>
