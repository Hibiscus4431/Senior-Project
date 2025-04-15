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
      <button class="t_button" @click="publishTest">Publish Final Test</button>
      <button class="t_button" @click="showBackWarning = true">Back to Draft Pool</button>
      <button class="t_button" @click="exportToWord">Export Test to Document</button>
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
      <strong>Total Points:</strong> {{ this.questions.length }} points
    </p>
    <hr />

    <!-- Warning Modal -->
    <div class="popup-overlay" v-if="showBackWarning" @click.self="showBackWarning = false">
      <div class="form-popup-modal">
        <div class="form-container">
          <h2 style="text-align: center;">Warning</h2>
          <p style="text-align: center; font-size: 18px;">
            If you go back to the Draft Pool, any unsaved changes on this page may be lost.
          </p>
          <div style="display: flex; justify-content: center; gap: 10px; margin-top: 20px;">
            <button class="btn" @click="confirmBack">Continue</button>
            <button class="btn cancel" @click="showBackWarning = false">Cancel</button>
          </div>
        </div>
      </div>
    </div>

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
        graphicPreview: savedOptions.graphicPreview || ''
      },
      testBankId: this.$route.query.testBankId,
      showBackWarning: false,
      hasUnsavedChanges: true
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
    }
  },

  methods: {
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
            type: this.testOptions.selectedTemplate || "All Questions"
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
            `This exam is worth ${this.questions.length} points.`,
            `You have ${this.totalEstimatedTime || "N/A"} minutes to complete the exam.`,
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
      const testContent = () => {
        const content = [
          new Paragraph({
            text: `${this.testOptions.testName} - Version: XXXX`,
            heading: HeadingLevel.HEADING_1,
            spacing: { after: 300 },
          }),
          new Paragraph({ text: "Name: __________________________", spacing: { after: 400 } }),
          createHorizontalLine()
        ];

        this.questions.forEach((q, index) => {
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
        });

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
          children: [
            ...coverPageContent(),
            ...testContent(),
            ...resourceSection
          ]
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
