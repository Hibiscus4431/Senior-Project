-- This is where you will place the foreign keys we will follow the strucutre i will place from another source 
ALTER TABLE Questions
ADD CONSTRAINT fk_questions_course
FOREIGN KEY (course_id)
REFERENCES Courses(course_id)
ON DELETE SET NULL;

ALTER TABLE Questions
ADD CONSTRAINT fk_questions_textbook
FOREIGN KEY (textbook_id)
REFERENCES Textbook(textbook_id)
ON DELETE SET NULL;

ALTER TABLE Questions
ADD CONSTRAINT fk_questions_attachment
FOREIGN KEY (attachment_id)
REFERENCES Attachments(attachments_id)
ON DELETE SET NULL;

ALTER TABLE Tests
ADD CONSTRAINT fk_tests_course
FOREIGN KEY (course_id)
REFERENCES Courses(course_id)
ON DELETE CASCADE;

ALTER TABLE Tests
ADD CONSTRAINT fk_tests_template
FOREIGN KEY (template_id)
REFERENCES Templates(template_id)
ON DELETE SET NULL;

ALTER TABLE Tests
ADD CONSTRAINT fk_tests_user
FOREIGN KEY (user_id)
REFERENCES Users(user_id)
ON DELETE CASCADE;

ALTER TABLE Test_MetaData
ADD CONSTRAINT fk_test_metadata_test
FOREIGN KEY (test_id)
REFERENCES Tests(tests_id)
ON DELETE CASCADE;

ALTER TABLE Test_MetaData
ADD CONSTRAINT fk_test_metadata_question
FOREIGN KEY (question_id)
REFERENCES Questions(id)
ON DELETE CASCADE;

ALTER TABLE Answer_Key
ADD CONSTRAINT fk_answer_key_test
FOREIGN KEY (test_id)
REFERENCES Tests(tests_id)
ON DELETE CASCADE;

ALTER TABLE Feedback
ADD CONSTRAINT fk_feedback_test
FOREIGN KEY (test_id)
REFERENCES Tests(tests_id)
ON DELETE CASCADE;

ALTER TABLE Feedback
ADD CONSTRAINT fk_feedback_question
FOREIGN KEY (question_id)
REFERENCES Questions(id)
ON DELETE CASCADE;

ALTER TABLE QuestionFillBlanks
ADD CONSTRAINT fk_fill_blanks_question
FOREIGN KEY (question_id)
REFERENCES Questions(id)
ON DELETE CASCADE;

ALTER TABLE QuestionMatches
ADD CONSTRAINT fk_matches_question
FOREIGN KEY (question_id)
REFERENCES Questions(id)
ON DELETE CASCADE;

ALTER TABLE QuestionOptions
ADD CONSTRAINT fk_options_question
FOREIGN KEY (question_id)
REFERENCES Questions(id)
ON DELETE CASCADE;

ALTER TABLE Attachments_MetaData
ADD CONSTRAINT fk_attachments_metadata_attachment
FOREIGN KEY (attachment_id)
REFERENCES Attachments(attachments_id)
ON DELETE CASCADE;

--ALTER TABLE Attachments_MetaData
--ADD CONSTRAINT fk_attachments_metadata_reference
--FOREIGN KEY (reference_id)
--REFERENCES Questions(id)
--ON DELETE CASCADE;

ALTER TABLE QTI_Imports
ADD CONSTRAINT fk_qti_imports_test
FOREIGN KEY (test_id)
REFERENCES Tests(tests_id)
ON DELETE CASCADE;