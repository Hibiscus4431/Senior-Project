-- Adding foreign keys to link tables together

-- Linking Questions to Courses (each question belongs to a course)
DO $$ 
BEGIN
    -- Linking Questions to Courses (each question belongs to a course)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'questions' AND constraint_name = 'fk_questions_course'
    ) THEN
        ALTER TABLE Questions
        ADD CONSTRAINT fk_questions_course
        FOREIGN KEY (course_id)
        REFERENCES Courses(course_id)
        ON DELETE SET NULL;
    END IF;

-- Linking Questions to Textbook (each question may reference a textbook)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'questions' AND constraint_name = 'fk_questions_textbook'
    ) THEN
        ALTER TABLE Questions
        ADD CONSTRAINT fk_questions_textbook
        FOREIGN KEY (textbook_id)
        REFERENCES Textbook(textbook_id)
        ON DELETE SET NULL;
    END IF;

-- Linking Questions to Attachments (each question may have an attachment)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'questions' AND constraint_name = 'fk_questions_attachment'
    ) THEN
        ALTER TABLE Questions
        ADD CONSTRAINT fk_questions_attachment
        FOREIGN KEY (attachment_id)
        REFERENCES Attachments(attachments_id)
        ON DELETE SET NULL;
    END IF;

-- Linking Tests to Courses (each test is for a specific course)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'tests' AND constraint_name = 'fk_tests_course'
    ) THEN
        ALTER TABLE Tests
        ADD CONSTRAINT fk_tests_course
        FOREIGN KEY (course_id)
        REFERENCES Courses(course_id)
        ON DELETE CASCADE;
    END IF;

-- Linking Tests to Templates (each test may be based on a template)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'tests' AND constraint_name = 'fk_tests_template'
    ) THEN
        ALTER TABLE Tests
        ADD CONSTRAINT fk_tests_template
        FOREIGN KEY (template_id)
        REFERENCES Templates(template_id)
        ON DELETE SET NULL;
    END IF;

-- Linking Tests to Users (each test is created by a user)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'tests' AND constraint_name = 'fk_tests_user'
    ) THEN
        ALTER TABLE Tests
        ADD CONSTRAINT fk_tests_user
        FOREIGN KEY (user_id)
        REFERENCES Users(user_id)
        ON DELETE CASCADE;
    END IF;


-- Linking Test_MetaData to Tests (metadata belongs to a test)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'test_metadata' AND constraint_name = 'fk_test_metadata_test'
    ) THEN
        ALTER TABLE Test_MetaData
        ADD CONSTRAINT fk_test_metadata_test
        FOREIGN KEY (test_id)
        REFERENCES Tests(tests_id)
        ON DELETE CASCADE;
    END IF;

-- Linking Test_MetaData to Questions (metadata includes questions)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'test_metadata' AND constraint_name = 'fk_test_metadata_question'
    ) THEN
        ALTER TABLE Test_MetaData
        ADD CONSTRAINT fk_test_metadata_question
        FOREIGN KEY (question_id)
        REFERENCES Questions(id)
        ON DELETE CASCADE;
    END IF;

-- Linking Answer_Key to Tests (each answer key is for a specific test)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'answer_key' AND constraint_name = 'fk_answer_key_test'
    ) THEN
        ALTER TABLE Answer_Key
        ADD CONSTRAINT fk_answer_key_test
        FOREIGN KEY (test_id)
        REFERENCES Tests(tests_id)
        ON DELETE CASCADE;
    END IF;

-- Linking Feedback to Tests (feedback is given for a test)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'feedback' AND constraint_name = 'fk_feedback_test'
    ) THEN
        ALTER TABLE Feedback
        ADD CONSTRAINT fk_feedback_test
        FOREIGN KEY (test_id)
        REFERENCES Tests(tests_id)
        ON DELETE CASCADE;
    END IF;

-- Linking Feedback to Questions (feedback is tied to a question)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'feedback' AND constraint_name = 'fk_feedback_question'
    ) THEN
        ALTER TABLE Feedback
        ADD CONSTRAINT fk_feedback_question
        FOREIGN KEY (question_id)
        REFERENCES Questions(id)
        ON DELETE CASCADE;
    END IF;

-- Add foreign key for feedback.user_id referencing users.user_id
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'feedback' AND constraint_name = 'fk_feedback_user'
    ) THEN
        ALTER TABLE feedback 
        ADD CONSTRAINT fk_feedback_user 
        FOREIGN KEY (user_id) REFERENCES users(user_id) 
        ON DELETE CASCADE;
    END IF;

-- Linking QuestionFillBlanks to Questions (fill-in-the-blank questions belong to a question)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'questionfillblanks' AND constraint_name = 'fk_fill_blanks_question'
    ) THEN
        ALTER TABLE QuestionFillBlanks
        ADD CONSTRAINT fk_fill_blanks_question
        FOREIGN KEY (question_id)
        REFERENCES Questions(id)
        ON DELETE CASCADE;
    END IF;

-- Linking QuestionMatches to Questions (matching questions belong to a question)
    IF NOT EXISTS ( 
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'questionmatches' AND constraint_name = 'fk_matches_question'
    ) THEN
        ALTER TABLE QuestionMatches
        ADD CONSTRAINT fk_matches_question
        FOREIGN KEY (question_id)
        REFERENCES Questions(id)
        ON DELETE CASCADE;
    END IF;

-- Linking QuestionOptions to Questions (each question has multiple options)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'questionoptions' AND constraint_name = 'fk_options_question'
    ) THEN
        ALTER TABLE QuestionOptions
        ADD CONSTRAINT fk_options_question
        FOREIGN KEY (question_id)
        REFERENCES Questions(id)
        ON DELETE CASCADE;
    END IF;

-- Linking Attachments_MetaData to Attachments (metadata belongs to an attachment)
    IF NOT EXISTS ( 
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'attachments_metadata' AND constraint_name = 'fk_attachments_metadata_attachment'
    ) THEN
        ALTER TABLE Attachments_MetaData
        ADD CONSTRAINT fk_attachments_metadata_attachment
        FOREIGN KEY (attachment_id)
        REFERENCES Attachments(attachments_id)
        ON DELETE CASCADE;
    END IF;

-- Linking Attachments_MetaData to Questions (metadata references a question)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'attachments_metadata' AND constraint_name = 'fk_attachments_metadata_reference'
    ) THEN
        ALTER TABLE Attachments_MetaData
        ADD CONSTRAINT fk_attachments_metadata_reference
        FOREIGN KEY (reference_id)
        REFERENCES Questions(id)
        ON DELETE CASCADE;
    END IF;

-- Linking QTI_Imports to Tests (imported test data belongs to a test)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'qti_imports' AND constraint_name = 'fk_qti_imports_test'
    ) THEN
        ALTER TABLE QTI_Imports
        ADD CONSTRAINT fk_qti_imports_test
        FOREIGN KEY (test_id)
        REFERENCES Tests(tests_id)
        ON DELETE CASCADE;
    END IF;

-- Linking Textbook to Users (publisher is a user)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'textbook' AND constraint_name = 'fk_textbook_publisher'
    ) THEN
        ALTER TABLE Textbook
        ADD CONSTRAINT fk_textbook_publisher
        FOREIGN KEY (publisher_id)
        REFERENCES Users(user_id)
        ON DELETE SET NULL;
    END IF;
END $$;