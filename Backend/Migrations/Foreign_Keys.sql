-- Adding foreign keys to link tables together

-- Linking Questions to Courses (each question belongs to a course)
ALTER TABLE Questions
ADD CONSTRAINT fk_questions_course
FOREIGN KEY (course_id)
REFERENCES Courses(course_id)
ON DELETE SET NULL;

-- Linking Questions to Textbook (each question may reference a textbook)
ALTER TABLE Questions
ADD CONSTRAINT fk_questions_textbook
FOREIGN KEY (textbook_id)
REFERENCES Textbook(textbook_id)
ON DELETE SET NULL;

-- Linking Questions to Attachments (each question may have an attachment)
ALTER TABLE Questions
ADD CONSTRAINT fk_questions_attachment
FOREIGN KEY (attachment_id)
REFERENCES Attachments(attachments_id)
ON DELETE SET NULL;

-- Linking Tests to Courses (each test is for a specific course)
ALTER TABLE Tests
ADD CONSTRAINT fk_tests_course
FOREIGN KEY (course_id)
REFERENCES Courses(course_id)
ON DELETE CASCADE;

-- Linking Tests to Templates (each test may be based on a template)
ALTER TABLE Tests
ADD CONSTRAINT fk_tests_template
FOREIGN KEY (template_id)
REFERENCES Templates(template_id)
ON DELETE SET NULL;

-- Linking Tests to Users (each test is created by a user)
ALTER TABLE Tests
ADD CONSTRAINT fk_tests_user
FOREIGN KEY (user_id)
REFERENCES Users(user_id)
ON DELETE CASCADE;

-- Linking Test_MetaData to Tests (metadata belongs to a test)
ALTER TABLE Test_MetaData
ADD CONSTRAINT fk_test_metadata_test
FOREIGN KEY (test_id)
REFERENCES Tests(tests_id)
ON DELETE CASCADE;

-- Linking Test_MetaData to Questions (metadata includes questions)
ALTER TABLE Test_MetaData
ADD CONSTRAINT fk_test_metadata_question
FOREIGN KEY (question_id)
REFERENCES Questions(id)
ON DELETE CASCADE;

-- Linking Answer_Key to Tests (each answer key is for a specific test)
ALTER TABLE Answer_Key
ADD CONSTRAINT fk_answer_key_test
FOREIGN KEY (test_id)
REFERENCES Tests(tests_id)
ON DELETE CASCADE;

-- Linking Feedback to Tests (feedback is given for a test)
ALTER TABLE Feedback
ADD CONSTRAINT fk_feedback_test
FOREIGN KEY (test_id)
REFERENCES Tests(tests_id)
ON DELETE CASCADE;

-- Linking Feedback to Questions (feedback is tied to a question)
ALTER TABLE Feedback
ADD CONSTRAINT fk_feedback_question
FOREIGN KEY (question_id)
REFERENCES Questions(id)
ON DELETE CASCADE;

-- Linking QuestionFillBlanks to Questions (fill-in-the-blank questions belong to a question)
ALTER TABLE QuestionFillBlanks
ADD CONSTRAINT fk_fill_blanks_question
FOREIGN KEY (question_id)
REFERENCES Questions(id)
ON DELETE CASCADE;

-- Linking QuestionMatches to Questions (matching questions belong to a question)
ALTER TABLE QuestionMatches
ADD CONSTRAINT fk_matches_question
FOREIGN KEY (question_id)
REFERENCES Questions(id)
ON DELETE CASCADE;

-- Linking QuestionOptions to Questions (each question has multiple options)
ALTER TABLE QuestionOptions
ADD CONSTRAINT fk_options_question
FOREIGN KEY (question_id)
REFERENCES Questions(id)
ON DELETE CASCADE;

-- Linking Attachments_MetaData to Attachments (metadata belongs to an attachment)
ALTER TABLE Attachments_MetaData
ADD CONSTRAINT fk_attachments_metadata_attachment
FOREIGN KEY (attachment_id)
REFERENCES Attachments(attachments_id)
ON DELETE CASCADE;

-- Linking Attachments_MetaData to Questions (metadata references a question)
ALTER TABLE Attachments_MetaData
ADD CONSTRAINT fk_attachments_metadata_reference
FOREIGN KEY (reference_id)
REFERENCES Questions(id)
ON DELETE CASCADE;

-- Linking QTI_Imports to Tests (imported test data belongs to a test)
ALTER TABLE QTI_Imports
ADD CONSTRAINT fk_qti_imports_test
FOREIGN KEY (test_id)
REFERENCES Tests(tests_id)
ON DELETE CASCADE;

-- Linking Textbook to Users (publisher is a user)
ALTER TABLE Textbook
ADD CONSTRAINT fk_textbook_publisher
FOREIGN KEY (publisher_id)
REFERENCES Users(user_id)
ON DELETE SET NULL;
