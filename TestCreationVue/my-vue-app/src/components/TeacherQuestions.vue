<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/TeacherQuestions.vue -->
<template>
  <div class="teacher-questions-container">
    <div class="center large-heading sticky">
      <h1>{{ courseTitle }}</h1>
    </div>
    <div class="center large-paragraph">
      <!--Button to go to view test bank page-->
      <router-link :to="{ path: '/TeacherViewTB', query: { courseTitle: courseTitle, courseId: courseId } }">
        <button class="t_button">View Test Banks</button>
      </router-link>
      <router-link :to="{ path: '/TeacherNewTB', query: { courseTitle: courseTitle, courseId: courseId } }">
        <button class="t_button">New Test Bank</button>
      </router-link>
      <button class="t_button" @click="importTest">Import Test</button>
      <br>
      <!-- Dropdown to select question type -->
      <div class="dropdown">
        <button class="dropbtn">Question Type</button>
        <div class="dropdown-content">
          <a href="#" @click="fetchQuestions('True/False')">True/False</a>
          <a href="#" @click="fetchQuestions('Multiple Choice')">Multiple Choice</a>
          <a href="#" @click="fetchQuestions('Matching')">Matching</a>
          <a href="#" @click="fetchQuestions('Fill in the Blank')">Fill in the Blank</a>
          <a href="#" @click="fetchQuestions('Short Answer')">Short Answer</a>
          <a href="#" @click="fetchQuestions('Essay')">Essay</a>
        </div>
      </div>
      <button class="t_button" @click="edit">New Question</button>
      <router-link to="/TeacherPubQ">
        <button class="t_button">Publisher Textbook Page</button>
      </router-link>
      <div id="selectedQuestionType" class="center large-paragraph">{{ selectedQuestionType }}</div>
    </div>

    <!-- Insert the fetched questions display here -->
    <ul>
      <li v-for="(question, index) in questions" :key="index" class="question-box"
        @click="toggleQuestionSelection(question.id)">
        <strong>Question {{ index + 1 }}:</strong> {{ question.text }}<br>
        <span><strong>Type:</strong> {{ question.type }}</span><br>
        <span><strong>Chapter:</strong> {{ question.chapter || 'N/A' }}</span><br>
        <span><strong>Section:</strong> {{ question.section || 'N/A' }}</span><br>
        <span><strong>Points:</strong> {{ question.points }}</span><br>
        <span><strong>Estimated Time:</strong> {{ question.time }} minutes</span><br>

        <!-- Answer types -->
        <div v-if="question.type === 'True/False'">
          <strong>Answer:</strong> {{ question.answer ? 'True' : 'False' }}
        </div>

        <div v-if="question.type === 'Multiple Choice'">
          <strong>Correct Answer:</strong> {{ (question.correctOption && question.correctOption.option_text) ||
            'Not specified' }}<br>
          <p><strong>Other Options:</strong></p>
          <ul>
            <li v-for="(option, i) in question.incorrectOptions" :key="i" class="incorrect-answer">
              {{ option.option_text }}
            </li>
          </ul>
        </div>

        <div v-if="question.type === 'Short Answer'">
          <strong>Answer:</strong> {{ question.answer || 'Not provided' }}
        </div>

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

        <div v-if="question.type === 'Essay'">
          <strong>Essay Instructions:</strong> {{ question.instructions || 'None' }}
        </div>

        <span><strong>Grading Instructions:</strong> {{ question.instructions || 'None' }}</span><br>

        <!-- Buttons shown only if selected -->
        <div v-if="selectedQuestionId === question.id" class="button-group">
          <button @click.stop="editQuestion(question)">Edit</button>
          <button @click.stop="deleteQuestion(question.id)">Delete</button>
        </div>
      </li>
    </ul>




    <!--file input element -->
    <input type="file" id="fileInput" style="display: none;" @change="handleFileUpload">


    <!-- contents of popup-->
    <div class="form-popup" id="q_edit">
      <form class="form-container" @submit.prevent="handleQuestionSave">
        <h1>New Question</h1>

        <!-- Common Fields -->
        <label for="ch"><b>Chapter Number</b></label><br>
        <input type="text" id="ch" v-model="chapter"><br>

        <label for="sec"><b>Section Number</b></label><br>
        <input type="text" id="sec" v-model="section"><br>

        <!-- Select Question Type -->
        <label for="questionType"><b>Question Type</b></label><br>
        <select id="questionType" v-model="selectedQuestionType">
          <option value="">Select Question Type</option>
          <option value="True/False">True/False</option>
          <option value="Multiple Choice">Multiple Choice</option>
          <option value="Matching">Matching</option>
          <option value="Fill in the Blank">Fill in the Blank</option>
          <option value="Short Answer">Short Answer</option>
          <option value="Essay">Essay</option>
        </select><br><br>

        <label for="question"><b>Question</b></label><br>
        <input type="text" id="question" v-model="question"><br>

        <!-- Conditional Fields -->
        <div v-if="selectedQuestionType === 'True/False'">
          <label for="answer"><b>Answer (True/False)</b></label><br>
          <select id="answer" v-model="answer">
            <option value="True">True</option>
            <option value="False">False</option>
          </select><br><br>
        </div>

        <div v-if="selectedQuestionType === 'Multiple Choice'">
          <label for="answerChoices"><b>Answer Choices</b></label><br>
          <input type="text" id="answerChoices" v-model="answerChoices" placeholder="Separate choices with commas"><br>

          <label for="answer"><b>Correct Answer</b></label><br>
          <input type="text" id="answer" v-model="answer"><br>
        </div>

        <div v-if="selectedQuestionType === 'Short Answer'">
          <label for="answer"><b>Answer</b></label><br>
          <input type="text" id="answer" v-model="answer"><br>
        </div>

        <div v-if="selectedQuestionType === 'Essay'">
          <label for="instructions"><b>Grading Instructions</b></label><br>
          <textarea id="instructions" v-model="instructions" placeholder="Provide grading instructions"></textarea><br>
        </div>

        <div v-if="selectedQuestionType === 'Fill in the Blank'">
          <label for="answer"><b>Correct Answer</b></label><br>
          <input type="text" id="answer" v-model="answer" placeholder="Enter the correct answer"><br>
        </div>

        <div v-if="selectedQuestionType === 'Matching'">
          <label><b>Matching Pairs</b></label><br>
          <div v-for="(pair, index) in matchingPairs" :key="index" class="matching-pair">
            <input type="text" v-model="pair.term" placeholder="Term" class="matching-input" />
            <span>:</span>
            <input type="text" v-model="pair.definition" placeholder="Definition" class="matching-input" />
            <button type="button" @click="removePair(index)" class="remove-pair-btn">Remove</button><br>
          </div>
          <button type="button" @click="addPair" class="add-pair-btn">Add Pair</button>
        </div>

        <label for="points"><b>Points Worth</b></label><br>
        <input type="text" id="points" v-model="points" required><br>

        <label for="time"><b>Est Time (in Minutes)</b></label><br>
        <input type="text" id="time" v-model="time" required><br>

        <label for="ins"><b>Grading Instructions</b></label><br>
        <input type="text" id="ins" v-model="instructions" required><br>

        <label for="image"><b>Upload Image</b></label><br>
        <input type="file" id="image" @change="handleImageUpload" accept="image/*"><br>
        <img id="imagePreview" :src="imagePreview" alt="Image preview" v-if="imagePreview"
          style="max-width: 100%; max-height: 100%;"><br>

        <button type="submit" class="btn">Save</button>
        <button type="t_button" class="btn cancel" @click="closeForm">Close</button>
      </form>
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
      editingQuestionId: null // To store the ID of the question being edited
    };
  },
  methods: {
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
              section: question.section_number
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

    addPair() {
      this.matchingPairs.push({ term: '', definition: '' });
    },
    removePair(index) {
      this.matchingPairs.splice(index, 1);
    },
    selectQuestionType(type) {
      this.selectedQuestionType = type;
      document.getElementById('q_edit').style.display = 'block';
    },
    importTest() {
      document.getElementById('fileInput').click();
    },
    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file)  {
        alert("No file selected.");
        return;
      }
      const formData = new FormData();
      formData.append('file', file);

      try{
        //Phase 1: Uplod QTI file
        const uploadResponse = await api.post('/qti/upload',formData, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'multipart/form-data'
          }
        });
        const file_path = uploadResponse.data.file_path;
        console.log('File uploaded successfully:', file_path);

        //Phase 1.B: Create import record
        const importResponse= await api.post('/qti/import', { file_path}, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          }
        });
        const import_id = importResponse.data.import_id;
        console.log('QTI import created. Import ID:', import_id);

        //Phase 3: save imported questions to the database
        const saveResponse = await api.post(`qti/save/${import_id}`,{
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

    //function to post new question to the database
    async handleQuestionSave() {
      try {
        const isEditing = !!this.editingQuestionId;

        const payload = {
          question_text: this.question,
          default_points: parseInt(this.points),
          est_time: parseInt(this.time),
          chapter_number: this.chapter,
          section_number: this.section,
          grading_instructions: this.instructions,
        };

        // Type-specific fields
        if (this.selectedQuestionType === 'True/False') {
          payload.true_false_answer = this.answer === 'True';
        }

        if (this.selectedQuestionType === 'Multiple Choice') {
          const choices = this.answerChoices.split(',').map(c => c.trim());
          if (choices.length < 2) {
            alert('Please provide at least two answer choices.');
            return;
          }

          payload.options = choices.map(choice => ({
            option_text: choice,
            is_correct: choice.toLowerCase() === this.answer.trim().toLowerCase()
          }));
        }

        if (this.selectedQuestionType === 'Fill in the Blank') {
          payload.blanks = [{
            correct_text: this.answer
          }];
        }

        if (this.selectedQuestionType === 'Short Answer') {
          payload.answer = this.answer;
        }

        if (this.selectedQuestionType === 'Essay') {
          payload.grading_instructions = this.instructions;
        }

        if (this.selectedQuestionType === 'Matching') {
          payload.matches = this.matchingPairs.map(pair => ({
            prompt_text: pair.term,
            match_text: pair.definition
          }));
        }

        const headers = {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        };

        if (isEditing) {
          // PATCH request to update existing question
          await api.patch(`/questions/${this.editingQuestionId}`, payload, headers);
          alert('Question updated successfully!');
        } else {
          // POST request to create new question
          payload.course_id = this.courseId;
          payload.type = this.selectedQuestionType;
          payload.source = 'manual';
          await api.post('/questions', payload, headers);
          alert('Question created successfully!');
        }

        this.closeForm();
        this.resetForm();
        this.fetchQuestions(this.selectedQuestionType);

      } catch (error) {
        console.error('Error saving question:', error);
        alert('Something went wrong. Please try again.');
      }
    },


    handleImageUpload(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.image = e.target.result;
          this.imagePreview = e.target.result;
        };
        reader.readAsDataURL(file);
      } else {
        console.error('No image selected.');
      }
    },
    edit() {
      document.getElementById('q_edit').style.display = 'block';
    },
    closeForm() {
      document.getElementById('q_edit').style.display = 'none';
    },
    //helper function to reset form fields
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
    },

    //functions to edit and delete questions when selected box
    toggleQuestionSelection(id) {
      this.selectedQuestionId = this.selectedQuestionId === id ? null : id;
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
        this.answerChoices = [
          ...(question.correctOption ? [question.correctOption.option_text] : []),
          ...(question.incorrectOptions || []).map(o => o.option_text)
        ].join(', ');
      } else if (question.type === 'Matching') {
        this.matchingPairs = question.pairs || [];
      }

      document.getElementById('q_edit').style.display = 'block';
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

.teacher-questions-container {
  background-color: #43215a;
  font-family: Arial, sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>