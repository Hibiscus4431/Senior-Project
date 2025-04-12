<template>
  <div class="theme-teacher">
    <div class="top-banner">
      <div class="banner-title">{{ testOptions.testName || 'Test Template' }}</div>
      <div class="t_banner-actions">
        <router-link to="/TeacherHome" class="t_banner-btn">Home</router-link>
        <router-link to="/" class="t_banner-btn">Log Out</router-link>
      </div>
    </div>

    <div class="center button-row">
      <button class="t_button" @click="publishTest">Publish Final Test</button>
      <button class="t_button" @click="goBackTB">Back to Draft Pool</button>
      <button class="t_button" @click="exportToWord">Export Test to .docx</button>
    </div>

    <p class="export-note">
      <strong>Note:</strong> Anything displayed in <span class="green-text">green</span> will not appear on the student
      test but will be included in the test key. <br />
      If selected, a cover page and any uploaded graphic will be added automatically to the exported document.
    </p>

    <hr />

    <div class="question-list-container">
      <draggable v-model="questions" item-key="id" class="drag-list" handle=".drag-handle" @update="saveOrder">
        <template #header></template>

        <template #item="{ element, index }">
          <div class="question-box">
            <div class="drag-header">
              <span class="drag-handle" title="Drag to reorder">✥</span>
              <h3>{{ index + 1 }}. {{ element.question_text }}</h3>
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
        coverPage: savedOptions.coverPage || false,
        selectedTemplate: savedOptions.selectedTemplate || "All Questions",
        uploadedImage: savedOptions.uploadedImage || '',
        timeAllowed: savedOptions.timeAllowed || ''
      },
      testBankId: this.$route.query.testBankId
    };
  },

  mounted() {
    this.fetchQuestions();
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

  methods: {
    //function to go back to draft pool
    goBackTB() {
      this.$router.push({
        name: 'TeacherViewTB',
        params: { id: this.testBankId },
        query: {
          courseId: this.$route.query.courseId,
          courseTitle: this.$route.query.courseTitle,
          testBankName: this.$route.query.testBankName
        }
      });
    },
    //fetch desired testbank questions
    async fetchQuestions() {
      try {
        const response = await api.get(`/tests/draft-questions`, {
          params: {
            test_bank_id: this.testBankId,
            type: "All Questions"
          },
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        const rawQuestions = response.data.questions || [];
        const savedOrder = localStorage.getItem(`questionOrder_${this.testBankId}`);

        if (savedOrder) {
          const idOrder = JSON.parse(savedOrder);
          const questionMap = new Map(rawQuestions.map(q => [q.id, q]));

          const ordered = idOrder
            .map(id => questionMap.get(id))
            .filter(Boolean); // remove missing

          // Add any new questions that aren’t in saved order
          rawQuestions.forEach(q => {
            if (!idOrder.includes(q.id)) {
              ordered.push(q);
            }
          });

          this.questions = ordered;
        } else {
          this.questions = rawQuestions;
        }

      } catch (error) {
        console.error("Failed to fetch questions:", error);
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
    async exportToWord() {
      const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, BorderStyle } = await import("docx");
      const children = [];


      const horizontalLine = new Paragraph({
        border: {
          bottom: {
            color: "000000",       // black line
            space: 1,
            value: BorderStyle.SINGLE,
            size: 6,               // thickness (8 = 1pt, 6 = 0.75pt)
          },
        },
        children: [],              // no text inside
        spacing: { after: 200 },
      });

      // Create a paragraph that forces a page break
      const pageBreak = new Paragraph({
        children: [],
        pageBreakBefore: true,
      });


      // --- COVER PAGE ---
      if (this.testOptions.coverPage) {
        children.push(
          new Paragraph({
            text: this.testOptions.testName,
            heading: HeadingLevel.TITLE,
            alignment: AlignmentType.CENTER,
            spacing: { after: 200 },
          }),
          new Paragraph({
            text: "Course: " + (this.$route.query.courseTitle || "N/A"),
            alignment: AlignmentType.CENTER,
          }),
          new Paragraph({
            text: "Time Allowed: " + (this.testOptions.timeAllowed || "N/A") + " minutes",
            alignment: AlignmentType.CENTER,
            spacing: { after: 400 },
          }),
          new Paragraph({}) // page break spacer
        );

        children.push(pageBreak);
      }

      // --- TEST PAGE ---
      children.push(
        new Paragraph({
          text: `${this.testOptions.testName}`,
          heading: HeadingLevel.HEADING_1,
          spacing: { after: 300 },
        }),
        new Paragraph({
          text: "Name: __________________________",
          spacing: { after: 400 },
        })
      );

      children.push(horizontalLine);

      this.questions.forEach((q, index) => {
        children.push(
          new Paragraph({
            text: `${index + 1}. ${q.question_text}`,
            spacing: { after: 200 },
          })
        );

        if (q.type === "Multiple Choice") {
          const options = this.shuffleOptions(q);
          options.forEach((opt, i) => {

            children.push(new Paragraph({
              text: `${String.fromCharCode(65 + i)}. ${opt.option_text}`,
              spacing: { after: 100 },
              indent: {
                left: 720, // 720 twips = 0.5 inches
              }
            }));
          });
        } else if (q.type === "True/False") {
          children.push(new Paragraph("True/False: __________________________"));




        } else if (q.type === "Fill in the Blank") {
          children.push(new Paragraph("Answer: "));




        } else if (q.type === "Short Answer") {
          // Add approx. half a page of vertical space (~15 blank lines)
          for (let i = 0; i < 15; i++) {
            children.push(new Paragraph({
              text: " ",
              spacing: { after: 200 }
            }));
          }



        } else if (q.type === "Essay") {
          // Add approx. full page of vertical space (~30 blank lines)
          for (let i = 0; i < 30; i++) {
            children.push(new Paragraph({
              text: " ",
              spacing: { after: 200 }
            }));
          }


        } else if (q.type === "Matching") {
          children.push(new Paragraph("Match the following:"));
          const shuffled = this.getShuffledMatches(q);
          shuffled.forEach((pair, i) => {
            children.push(new Paragraph(`${i + 1}. ${pair.prompt_text}`));
          });

          children.push(new Paragraph("Answer Bank:"));
          this.getShuffledAnswerBank(q).forEach((ans, i) => {
            children.push(new Paragraph(`${String.fromCharCode(65 + i)}. ${ans}`));
          });
        }

        children.push(new Paragraph("")); // spacing
      });

      // --- KEY PAGE ---
      children.push(pageBreak);

      let testKeyCount = 0;

      // Initial Test Key heading
      children.push(new Paragraph({
        children: [
          new TextRun({
            text: `${this.testOptions.testName} - Test Key`,
            bold: true,
            size: 32,
            color: "FF0000",
          })
        ],
        spacing: { after: 300 }
      }));

      this.questions.forEach((q, index) => {
        // Add a new heading every ~20 answers
        if (testKeyCount > 0 && testKeyCount % 20 === 0) {
          children.push(
            pageBreak,
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
          );
        }

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
          const key = this.getMatchingKeyString(q);
          answerText = `Correct Matches: ${key}`;
        }

        children.push(
          new Paragraph({
            text: `${index + 1}. ${q.question_text}`,
            spacing: { after: 100 },
          }),
          new Paragraph({
            text: answerText,
            spacing: { after: 200 },
          })
        );

        testKeyCount++;
      });


      // --- RESOURCE PAGE (if image uploaded) ---
      if (this.testOptions.uploadedImage) {
        children.push(
          new Paragraph({}),
          new Paragraph({
            text: "Resource Page",
            heading: HeadingLevel.HEADING_1,
            spacing: { after: 300 },
          }),
          new Paragraph({
            text: "Graphic: " + this.testOptions.uploadedImage,
            spacing: { after: 100 },
          })
        );
      }

      // --- CREATE FINAL DOCUMENT ---
      const doc = new Document({
        sections: [{ properties: {}, children }],
        styles: {
          default: {
            document: {
              run: {
                font: "Arial",
                size: 24, // 12pt
              },
              paragraph: {
                spacing: { line: 276 },
              },
            },
          },
        },
      });

      const blob = await Packer.toBlob(doc);
      saveAs(blob, `${this.testOptions.testName || "GeneratedTest"}.docx`);
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
