-- Triggers -- 

-- Answer Key Triggers -- 

    --Ensure  a test id exists before inserting an answer key 
CREATE OR REPLACE FUNCTION ensure_test_exists()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM tests WHERE test_id = NEW.test_id) THEN
        RAISE EXCEPTION 'Test ID % does not exist', NEW.test_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_test_exists
BEFORE INSERT ON answer_key
FOR EACH ROW
EXECUTE FUNCTION ensure_test_exists();

    -- Prevent multiple answer keys for the same test 
CREATE OR REPLACE FUNCTION prevent_duplicate_answer_keys()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM answer_key WHERE test_id = NEW.test_id) THEN
        RAISE EXCEPTION 'An answer key already exists for test ID %', NEW.test_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_single_answer_key
BEFORE INSERT ON answer_key
FOR EACH ROW
EXECUTE FUNCTION prevent_duplicate_answer_keys();

    -- Delete answer key when a test is deleted 
CREATE OR REPLACE FUNCTION delete_answer_key_on_test_deletion()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM answer_key WHERE test_id = OLD.test_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER cascade_delete_answer_key
AFTER DELETE ON tests
FOR EACH ROW
EXECUTE FUNCTION delete_answer_key_on_test_deletion();

    -- Update answer key path if needed -- CHeck this one!
CREATE OR REPLACE FUNCTION log_answer_key_update()
RETURNS TRIGGER AS $$
BEGIN
    RAISE NOTICE 'Answer key ID %: file path changed from % to %', OLD.answer_key_id, OLD.file_path, NEW.file_path;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER track_answer_key_updates
BEFORE UPDATE ON answer_key
FOR EACH ROW
WHEN (OLD.file_path IS DISTINCT FROM NEW.file_path)
EXECUTE FUNCTION log_answer_key_update();



-- Attachemtns Table Triggers --

    --Prevent insert without valid file path 
CREATE OR REPLACE FUNCTION check_valid_filepath()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.filepath NOT LIKE 'attachments/%' THEN
        RAISE EXCEPTION 'Invalid file path. File must be stored under the "attachments/" directory.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_insert_check_filepath
BEFORE INSERT ON attachments
FOR EACH ROW
EXECUTE FUNCTION check_valid_filepath();

    -- Prevents deltion if used in a test or question
ALTER TABLE attachments
ADD CONSTRAINT prevent_attachment_deletion
FOREIGN KEY (attachments_id)
REFERENCES attachments(attachments_id)
ON DELETE RESTRICT;



-- Attachments MetaData Triggers -- 

    -- Prevent invalid refrences 
CREATE OR REPLACE FUNCTION validate_reference_id()
RETURNS TRIGGER AS $$
BEGIN
         -- Check if the reference_id exists in the correct table based on reference_type
    IF NEW.reference_type = 'question' AND 
       NOT EXISTS (SELECT 1 FROM questions WHERE id = NEW.reference_id) THEN
        RAISE EXCEPTION 'Invalid reference_id: Question does not exist';
    
    ELSIF NEW.reference_type = 'test' AND 
          NOT EXISTS (SELECT 1 FROM tests WHERE id = NEW.reference_id) THEN
        RAISE EXCEPTION 'Invalid reference_id: Test does not exist';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_reference_existence
BEFORE INSERT OR UPDATE ON attachments_metadata
FOR EACH ROW EXECUTE FUNCTION validate_reference_id();

            -- Prevent duplicate attachments for the saem question/test 
CREATE OR REPLACE FUNCTION prevent_duplicate_attachment()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM attachments_metadata 
        WHERE attachments_id = NEW.attachments_id
          AND reference_id = NEW.reference_id
          AND reference_type = NEW.reference_type
    ) THEN
        RAISE EXCEPTION 'Duplicate attachment: This attachment is already linked to this reference';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_duplicate_attachment
BEFORE INSERT ON attachments_metadata
FOR EACH ROW EXECUTE FUNCTION prevent_duplicate_attachment();

            -- Preserve attachments when a question or test is deleted 

CREATE OR REPLACE FUNCTION preserve_attachments_on_reference_delete()
RETURNS TRIGGER AS $$
BEGIN
    -- Remove only the metadata linking the attachment to the deleted question/test
    DELETE FROM attachments_metadata 
    WHERE reference_id = OLD.id 
    AND reference_type = TG_TABLE_NAME;  -- Dynamically applies to either Questions or tests

    -- Do NOT delete the actual attachment file from the Attachments table

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Attach the trigger to the Questions table
CREATE TRIGGER handle_question_deletion
AFTER DELETE ON questions
FOR EACH ROW EXECUTE FUNCTION preserve_attachments_on_reference_delete();

-- Attach the trigger to the tests table
CREATE TRIGGER handle_test_deletion
AFTER DELETE ON tests
FOR EACH ROW EXECUTE FUNCTION preserve_attachments_on_reference_delete();



-- Courses Tables Triggers -- 

   -- ensure a textbook id exists before assigning a course 
CREATE OR REPLACE FUNCTION ensure_textbook_exists()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Textbooks WHERE textbook_id = NEW.textbook_id) THEN
        RAISE EXCEPTION 'Textbook ID % does not exist', NEW.textbook_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_textbook_exists
BEFORE INSERT ON courses
FOR EACH ROW
EXECUTE FUNCTION ensure_textbook_exists();

    --Prevent duplicate course names for the same teacher 
CREATE OR REPLACE FUNCTION prevent_duplicate_courses()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM courses 
        WHERE course_name = NEW.course_name 
        AND teacher_id = NEW.teacher_id
    ) THEN
        RAISE EXCEPTION 'Teacher ID % already has a course named %', NEW.teacher_id, NEW.course_name;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_unique_teacher_course
BEFORE INSERT ON courses
FOR EACH ROW
EXECUTE FUNCTION prevent_duplicate_courses();

    -- Cascade delete courses when a teacher is deleted 
CREATE OR REPLACE FUNCTION cascade_delete_courses()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.role = 'teacher' THEN  -- Use 'teacher' instead of role_id = 2
        DELETE FROM courses WHERE teacher_id = OLD.user_id;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER delete_courses_on_teacher_removal
AFTER DELETE ON users
FOR EACH ROW
EXECUTE FUNCTION cascade_delete_courses();

    -- Prevents course deletion if questions are associated 
CREATE OR REPLACE FUNCTION prevent_course_deletion_if_questions_exist()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM questions WHERE course_id = OLD.course_id) THEN
        RAISE EXCEPTION 'Course ID % cannot be deleted because it has associated questions', OLD.course_id;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER block_course_deletion
BEFORE DELETE ON courses
FOR EACH ROW
EXECUTE FUNCTION prevent_course_deletion_if_questions_exist();

    -- Ensures a teacher id exists before assigning a course 
CREATE OR REPLACE FUNCTION ensure_teacher_exists()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM users WHERE user_id = NEW.teacher_id AND role = 'teacher'
    ) THEN
        RAISE EXCEPTION 'Teacher ID % does not exist or is not a teacher', NEW.teacher_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_teacher_exists
BEFORE INSERT ON courses
FOR EACH ROW
EXECUTE FUNCTION ensure_teacher_exists();


-- Feedback Table Triggers -- 

    -- Ensure a test id or questio id exists 
CREATE OR REPLACE FUNCTION ensure_test_or_question_exists()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM tests WHERE test_id = NEW.test_id) THEN
        RAISE EXCEPTION 'Test ID % does not exist', NEW.test_id;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM questions WHERE question_id = NEW.question_id) THEN
        RAISE EXCEPTION 'Question ID % does not exist', NEW.question_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_test_or_question_exists
BEFORE INSERT ON feedback
FOR EACH ROW
EXECUTE FUNCTION ensure_test_or_question_exists();

    -- Ensure only teachers or publishers can provide feedback 
CREATE OR REPLACE FUNCTION ensure_valid_feedback_user()
RETURNS TRIGGER AS $$
DECLARE
    user_role user_role;
BEGIN
    -- Fetch user role
    SELECT role INTO user_role FROM users WHERE user_id = NEW.user_id;

    -- Ensure the user is either a teacher or publisher
    IF user_role NOT IN ('teacher', 'publisher') THEN
        RAISE EXCEPTION 'Only teachers and publishers can provide feedback';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_feedback_role
BEFORE INSERT ON feedback
FOR EACH ROW
EXECUTE FUNCTION ensure_valid_feedback_user();

    -- Prevent duplicate feedback on the same question/test 
CREATE OR REPLACE FUNCTION prevent_duplicate_feedback()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM feedback 
        WHERE test_id = NEW.test_id 
          AND question_id = NEW.question_id 
          AND user_id = NEW.user_id
    ) THEN
        RAISE EXCEPTION 'User % has already provided feedback for Test ID % or Question ID %', NEW.user_id, NEW.test_id, NEW.question_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_unique_feedback
BEFORE INSERT ON feedback
FOR EACH ROW
EXECUTE FUNCTION prevent_duplicate_feedback();

    -- Cascade delte feedback when a test or question is deleted 
CREATE OR REPLACE FUNCTION cascade_delete_feedback()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM feedback WHERE test_id = OLD.test_id OR question_id = OLD.question_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER delete_feedback_on_test_question_removal
AFTER DELETE ON tests
FOR EACH ROW
EXECUTE FUNCTION cascade_delete_feedback();

CREATE TRIGGER delete_feedback_on_question_removal
AFTER DELETE ON questions
FOR EACH ROW
EXECUTE FUNCTION cascade_delete_feedback();


-- Fill in the blank table triggers -- 

    -- Prevent adding fill in hte blank answers to nin fill in the blank questions 
CREATE FUNCTION prevent_fill_blank_for_non_fill_blank() RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM questions
        WHERE question_id = NEW.question_id AND type = 'Fill-in-the-Blank'
    ) THEN
        RAISE EXCEPTION 'Only Fill-in-the-Blank questions can have blank answers';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_fill_blank_for_non_fill_blank
BEFORE INSERT ON questionfillblanks
FOR EACH ROW
EXECUTE FUNCTION prevent_fill_blank_for_non_fill_blank();

    -- Ensure fill in the blank have at one lest one corret answer 
CREATE FUNCTION enforce_minimum_fill_blank_answers() RETURNS TRIGGER AS $$
DECLARE
    blank_count INT;
    question_type VARCHAR(50);
BEGIN
    -- Get the type of the question
    SELECT type INTO question_type FROM questions WHERE id = NEW.question_id;

    -- Check if it's a Fill-in-the-Blank question
    IF question_type = 'Fill in the Blank' THEN
        -- Count the number of blanks for the question
        SELECT COUNT(*) INTO blank_count FROM questionfillblanks WHERE question_id = NEW.question_id;

        -- Enforce minimum one correct answer
        IF blank_count < 1 THEN
            RAISE EXCEPTION 'Fill-in-the-Blank questions must have at least one correct answer';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_enforce_minimum_fill_blank_answers
AFTER INSERT ON questionfillblanks
FOR EACH ROW
EXECUTE FUNCTION enforce_minimum_fill_blank_answers();


-- Mathching Choice Triggers -- 

    -- Prevents adding matching pairs to non mathcing questions
CREATE FUNCTION prevent_matches_for_non_matching() RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM questions
        WHERE question_id = NEW.question_id AND type = 'Matching'
    ) THEN
        RAISE EXCEPTION 'Only Matching questions can have match pairs';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_matches_for_non_matching
BEFORE INSERT ON questionmatches
FOR EACH ROW
EXECUTE FUNCTION prevent_matches_for_non_matching();

    --Ensure mathich question have at lease 2 pairs 
CREATE FUNCTION enforce_minimum_matching_pairs() RETURNS TRIGGER AS $$
DECLARE
    match_count INT;
    question_type VARCHAR(50);
BEGIN
    -- Get the type of the question
    SELECT type INTO question_type FROM questions WHERE id = NEW.question_id;

    -- Check if it's a Matching question
    IF question_type = 'Matching' THEN
        -- Count the number of matching pairs for the question
        SELECT COUNT(*) INTO match_count FROM questionmatches WHERE question_id = NEW.question_id;

        -- Enforce minimum two pairs
        IF match_count < 2 THEN
            RAISE EXCEPTION 'Matching questions must have at least two pairs';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_enforce_minimum_matching_pairs
AFTER INSERT ON questionmatches
FOR EACH ROW
EXECUTE FUNCTION enforce_minimum_matching_pairs();


-- Multiple Choice Triggers -- 

    -- Prevent addicng answer choices option to non - MCQ Questions 
CREATE FUNCTION prevent_options_for_non_mcq() RETURNS TRIGGER AS $$
DECLARE
    question_type VARCHAR(50);
BEGIN
    -- Get the type of the question
    SELECT type INTO question_type FROM questions WHERE id = NEW.question_id;

    -- Only allow options for Multiple Choice questions
    IF question_type IS DISTINCT FROM 'Multiple Choice' THEN
        RAISE EXCEPTION 'Only Multiple Choice questions can have answer options';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_options_for_non_mcq
BEFORE INSERT ON QuestionOptions
FOR EACH ROW
EXECUTE FUNCTION prevent_options_for_non_mcq();


    -- Ensure multiple choice questions have at least have 2 options 
CREATE FUNCTION enforce_minimum_mcq_options() RETURNS TRIGGER AS $$
DECLARE
    option_count INT;
    question_type VARCHAR(50);
BEGIN
    -- Get the type of the question
    SELECT type INTO question_type FROM questions WHERE id = NEW.question_id;

    -- Ensure the question exists
    IF question_type IS NULL THEN
        RAISE EXCEPTION 'Question ID % does not exist', NEW.question_id;
    END IF;

    -- Check if it's a Multiple Choice question
    IF question_type = 'Multiple Choice' THEN
        -- Count the number of options
        SELECT COUNT(*) INTO option_count FROM questionoptions WHERE question_id = NEW.question_id;

        -- Ensure at least 2 options exist
        IF option_count < 2 THEN
            RAISE EXCEPTION 'Multiple Choice questions must have at least two answer options';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_enforce_minimum_mcq_options
AFTER INSERT ON QuestionOptions
FOR EACH ROW
EXECUTE FUNCTION enforce_minimum_mcq_options();

    -- Ensure multiple choice question have at least one correct answer 
CREATE FUNCTION enforce_mcq_correct_answer() RETURNS TRIGGER AS $$
DECLARE
    correct_count INT;
    question_type VARCHAR(50);
BEGIN
    -- Get the type of the question
    SELECT type INTO question_type FROM questions WHERE id = NEW.question_id;

    -- Ensure the question exists
    IF question_type IS NULL THEN
        RAISE EXCEPTION 'Question ID % does not exist', NEW.question_id;
    END IF;

    -- Check if it's a Multiple Choice question
    IF question_type = 'Multiple Choice' THEN
        -- Count the number of correct answers
        SELECT COUNT(*) INTO correct_count FROM questionoptions WHERE question_id = NEW.question_id AND is_correct = TRUE;

        -- Ensure at least 1 correct option exists
        IF correct_count < 1 THEN
            RAISE EXCEPTION 'Multiple Choice questions must have at least one correct answer';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_enforce_mcq_correct_answer
AFTER INSERT OR UPDATE ON QuestionOptions
FOR EACH ROW
EXECUTE FUNCTION enforce_mcq_correct_answer();


-- QTI Import Triggers -- 
CREATE OR REPLACE FUNCTION enforce_test_link_on_import()
RETURNS TRIGGER AS $$
BEGIN
    -- Ensure the question source is 'canvas_qti'
    IF NEW.source = 'canvas_qti' AND NEW.test_id IS NULL THEN
        RAISE EXCEPTION 'Imported questions must be linked to a test.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_enforce_test_link
BEFORE INSERT ON questions
FOR EACH ROW
EXECUTE FUNCTION enforce_test_link_on_import();



-- Triggers for Question --- 

    -- deptes a question if has been used on a publihed test 
CREATE OR REPLACE FUNCTION prevent_deleting_published_question()
RETURNS TRIGGER AS $$
BEGIN
    -- Verify the question is linked to a published test
    IF EXISTS (
        SELECT 1 FROM tests t
        JOIN Test_MetaData tm ON t.test_id = tm.test_id -- Ensure correct column name
        WHERE tm.question_id = OLD.id AND t.status = 'Published'
    ) THEN
        RAISE EXCEPTION 'Cannot delete a question used in a published test.';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER no_delete_published_question
BEFORE DELETE ON questions
FOR EACH ROW
EXECUTE FUNCTION prevent_deleting_published_question();

    
    -- To prevent modifying a question if it has been used in a published test. 
CREATE OR REPLACE FUNCTION prevent_modifying_published_question()
RETURNS TRIGGER AS $$
BEGIN
    -- Verify the question is linked to a published test
    IF EXISTS (
        SELECT 1 FROM tests t
        JOIN Test_MetaData tm ON t.tests_id = tm.test_id -- ✅ Using tests_id
        WHERE tm.question_id = NEW.id AND t.status = 'Published'
    ) THEN
        RAISE EXCEPTION 'Cannot modify a question used in a published test.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER no_modify_published_question
BEFORE UPDATE ON questions
FOR EACH ROW
EXECUTE FUNCTION prevent_modifying_published_question();

    -- Auto-Publish a question when added to a published test
CREATE FUNCTION auto_publish_question() RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM tests
        WHERE tests_id = NEW.test_id AND status = 'Published' -- ✅ Using tests_id
    ) THEN
        UPDATE questions
        SET is_published = TRUE
        WHERE id = NEW.question_id; -- ✅ Using id instead of question_id
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_auto_publish_question
AFTER INSERT ON Test_MetaData
FOR EACH ROW
EXECUTE FUNCTION auto_publish_question();


    -- Links a question to a textbook and links to a course 
CREATE FUNCTION enforce_valid_question_links() RETURNS TRIGGER AS $$
BEGIN
    -- If the question was originally created under a textbook, allow linking to a course
    IF NEW.course_id IS NOT NULL AND NEW.textbook_id IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1 FROM questions WHERE id = NEW.question_id AND textbook_id IS NOT NULL -- ✅ Using id instead of question_id
        ) THEN
            RAISE EXCEPTION 'A teacher-created question cannot be linked to both a course and a textbook';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_enforce_valid_question_links
BEFORE INSERT OR UPDATE ON questions
FOR EACH ROW
EXECUTE FUNCTION enforce_valid_question_links();

    -- Prevent True/False questions from having multiple-choice options
CREATE FUNCTION prevent_options_for_true_false() RETURNS TRIGGER AS $$
DECLARE
    question_type VARCHAR(50);
BEGIN
    -- Get the type of the question
    SELECT type INTO question_type FROM questions WHERE id = NEW.question_id;

    -- Ensure the question exists
    IF question_type IS NULL THEN
        RAISE EXCEPTION 'Question ID % does not exist', NEW.question_id;
    END IF;

    -- If it's a True/False question, prevent adding multiple-choice options
    IF question_type = 'True/False' THEN
        RAISE EXCEPTION 'True/False questions cannot have multiple-choice options';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_options_for_true_false
BEFORE INSERT ON QuestionOptions
FOR EACH ROW
EXECUTE FUNCTION prevent_options_for_true_false();


-- Template Table -- 


    -- Prevent duplicate template names 
CREATE OR REPLACE FUNCTION prevent_duplicate_templates()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM templates 
        WHERE LOWER(template_name) = LOWER(NEW.template_name)
    ) THEN
        RAISE EXCEPTION 'A template with the name % already exists', NEW.template_name;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER enforce_unique_template_name
BEFORE INSERT ON templates
FOR EACH ROW
EXECUTE FUNCTION prevent_duplicate_templates();

    -- Prevent duplicate file paths 

CREATE OR REPLACE FUNCTION prevent_duplicate_file_paths()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM templates WHERE file_path = NEW.file_path) THEN
        RAISE EXCEPTION 'The file path % is already in use', NEW.file_path;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER enforce_unique_file_path
BEFORE INSERT ON templates
FOR EACH ROW
EXECUTE FUNCTION prevent_duplicate_file_paths();

    --Prevent Deleting Templates if they are in use 
CREATE OR REPLACE FUNCTION prevent_template_deletion_if_in_use()
RETURNS TRIGGER AS $$
DECLARE 
    template_count INT;
BEGIN
    -- Ensure the template exists before checking for tests
    SELECT COUNT(*) INTO template_count FROM templates WHERE template_id = OLD.template_id;

    IF template_count = 0 THEN
        RAISE EXCEPTION 'Template ID % does not exist', OLD.template_id;
    END IF;

    -- Prevent deletion if the template is in use
    IF EXISTS (SELECT 1 FROM tests WHERE template_id = OLD.template_id) THEN
        RAISE EXCEPTION 'Template ID % is in use and cannot be deleted', OLD.template_id;
    END IF;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER block_template_deletion
BEFORE DELETE ON templates
FOR EACH ROW
EXECUTE FUNCTION prevent_template_deletion_if_in_use();


-- Test Meta_Data Table 
-- there are no triggers needed for this table 

-- Test Table -- 

    -- Enforce test status progression 

    -- Allows draft to final  fianl to published 
CREATE OR REPLACE FUNCTION enforce_status_progression()
RETURNS TRIGGER AS $$
DECLARE 
    status_exists INT;
BEGIN
    -- Check if the status column exists in tests table
    SELECT COUNT(*) INTO status_exists FROM information_schema.columns 
    WHERE table_name = 'tests' AND column_name = 'status';

    IF status_exists = 0 THEN
        RAISE EXCEPTION 'Column status does not exist in tests table';
    END IF;

    -- Ensure progression rules are followed
    IF (OLD.status = 'Published' AND NEW.status <> 'Published') THEN
        RAISE EXCEPTION 'Cannot change a Published test back to Draft or Final';
    END IF;
    IF (OLD.status = 'Final' AND NEW.status = 'Draft') THEN
        RAISE EXCEPTION 'Cannot change a Final test back to Draft';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER check_status_progression
BEFORE UPDATE ON tests
FOR EACH ROW
EXECUTE FUNCTION enforce_status_progression();


    -- A published test must have at least one question -- 
CREATE OR REPLACE FUNCTION check_questions_before_publish()
RETURNS TRIGGER AS $$
DECLARE
    question_count INT;
BEGIN
    -- Ensure the status column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns WHERE table_name = 'tests' AND column_name = 'status'
    ) THEN
        RAISE EXCEPTION 'Column status does not exist in tests table';
    END IF;

    -- Prevent publishing if no questions are assigned
    IF NEW.status = 'Published' THEN
        SELECT COUNT(*) INTO question_count FROM test_metadata WHERE test_id = NEW.tests_id; -- ✅ Using tests_id in tests table and test_id in Test_MetaData
        IF question_count = 0 THEN
            RAISE EXCEPTION 'Cannot publish a test without at least one question';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER ensure_questions_before_publish
BEFORE UPDATE ON tests
FOR EACH ROW
EXECUTE FUNCTION check_questions_before_publish();

    -- Prevents modifications to published test (except minor fields) 
CREATE OR REPLACE FUNCTION prevent_published_test_edits()
RETURNS TRIGGER AS $$
BEGIN
    -- Ensure the status column exists in tests table
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns WHERE table_name = 'tests' AND column_name = 'status'
    ) THEN
        RAISE EXCEPTION 'Column status does not exist in tests table';
    END IF;

    -- Prevent edits on published tests except for minor updates
    IF OLD.status = 'Published' THEN
        IF (NEW.name <> OLD.name OR 
            NEW.course_id <> OLD.course_id OR 
            NEW.template_id <> OLD.template_id OR 
            NEW.status <> 'Published') THEN
            RAISE EXCEPTION 'Cannot modify Published tests except for minor updates';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER restrict_published_test_edits
BEFORE UPDATE ON tests
FOR EACH ROW
EXECUTE FUNCTION prevent_published_test_edits();

    -- Auto updates point total before publishing 
CREATE OR REPLACE FUNCTION update_points_before_publish()
RETURNS TRIGGER AS $$
DECLARE
    total_points INT;
BEGIN
    IF NEW.status = 'Published' THEN
        SELECT COALESCE(SUM(points), 0) INTO total_points FROM test_metadata WHERE test_id = NEW.tests_id; -- ✅ Using Test_MetaData and tests_id
        NEW.points_total := total_points;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_points_publish
BEFORE UPDATE ON tests
FOR EACH ROW
EXECUTE FUNCTION update_points_before_publish();


-- Textbook Triggers -- 

    -- Prevent Duplicate ISBNs
CREATE OR REPLACE FUNCTION prevent_duplicate_isbn()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM textbook WHERE textbook_isbn = NEW.textbook_isbn) THEN
        RAISE EXCEPTION 'A textbook with ISBN % already exists', NEW.textbook_isbn;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER enforce_unique_isbn
BEFORE INSERT ON textbook
FOR EACH ROW
EXECUTE FUNCTION prevent_duplicate_isbn();

    --Ensure only publishers are able to insert textbooks 
CREATE OR REPLACE FUNCTION ensure_publisher_exists()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM users WHERE user_id = NEW.publisher_id AND role = 'publisher'::user_role -- ✅ Ensuring role uses ENUM type
    ) THEN
        RAISE EXCEPTION 'User ID % is not a publisher and cannot create textbooks', NEW.publisher_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_publisher_exists
BEFORE INSERT ON textbook
FOR EACH ROW
EXECUTE FUNCTION ensure_publisher_exists(); 

    -- Prevent duplicate title versions by the same author -- 
CREATE OR REPLACE FUNCTION prevent_duplicate_title_version()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM textbook 
        WHERE LOWER(textbook_title) = LOWER(NEW.textbook_title) 
        AND textbook_version = NEW.textbook_version
        AND LOWER(textbook_author) = LOWER(NEW.textbook_author)
    ) THEN
        RAISE EXCEPTION 'Author % already has a textbook % (Version: %)', NEW.textbook_author, NEW.textbook_title, NEW.textbook_version;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_unique_title_version
BEFORE INSERT ON textbook
FOR EACH ROW
EXECUTE FUNCTION prevent_duplicate_title_version();


-- users Table -- 
CREATE OR REPLACE FUNCTION enforce_lowercase_username()
RETURNS TRIGGER AS $$
BEGIN
    NEW.username := LOWER(NEW.username);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_lowercase_username_trigger
BEFORE INSERT OR UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION enforce_lowercase_username();

