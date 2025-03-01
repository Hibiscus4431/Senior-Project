-- Triggers -- 

-- Step 1: Drop all existing functions to prevent conflicts
DO $$ 
DECLARE r RECORD;
BEGIN
    FOR r IN (SELECT routine_name FROM information_schema.routines WHERE routine_schema = 'public' AND routine_type = 'FUNCTION') 
    LOOP
        EXECUTE format('DROP FUNCTION IF EXISTS %I CASCADE;', r.routine_name);
    END LOOP;
END $$;

-- Answer Key Triggers -- 
CREATE FUNCTION ensure_test_exists()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM tests WHERE tests.tests_id = NEW.test_id) THEN
        RAISE EXCEPTION 'Test ID % does not exist', NEW.test_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'check_test_exists' 
        AND event_object_table = 'answer_key'
    ) THEN
        CREATE TRIGGER check_test_exists
        BEFORE INSERT ON answer_key
        FOR EACH ROW
        EXECUTE FUNCTION ensure_test_exists();
    END IF;
END $$;

-- Prevent multiple answer keys for the same test
CREATE FUNCTION prevent_duplicate_answer_keys()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM answer_key WHERE test_id = NEW.test_id) THEN
        RAISE EXCEPTION 'An answer key already exists for test ID %', NEW.test_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'enforce_single_answer_key' 
        AND event_object_table = 'answer_key'
    ) THEN
        CREATE TRIGGER enforce_single_answer_key
        BEFORE INSERT ON answer_key
        FOR EACH ROW
        EXECUTE FUNCTION prevent_duplicate_answer_keys();
    END IF;
END $$;

-- Delete answer key when a test is deleted
CREATE FUNCTION delete_answer_key_on_test_deletion()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM answer_key WHERE test_id = OLD.tests_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'cascade_delete_answer_key' 
        AND event_object_table = 'tests'
    ) THEN
        CREATE TRIGGER cascade_delete_answer_key
        AFTER DELETE ON tests
        FOR EACH ROW
        EXECUTE FUNCTION delete_answer_key_on_test_deletion();
    END IF;
END $$;

-- Update answer key path if needed
CREATE FUNCTION log_answer_key_update()
RETURNS TRIGGER AS $$
BEGIN
    RAISE NOTICE 'Answer key ID %: file path changed from % to %', OLD.answer_key_id, OLD.file_path, NEW.file_path;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'track_answer_key_updates' 
        AND event_object_table = 'answer_key'
    ) THEN
        CREATE TRIGGER track_answer_key_updates
        BEFORE UPDATE ON answer_key
        FOR EACH ROW
        WHEN (OLD.file_path IS DISTINCT FROM NEW.file_path)
        EXECUTE FUNCTION log_answer_key_update();
    END IF;
END $$;


-- Attachemtns Table Triggers --

-- Step 2: Create Functions 
CREATE FUNCTION check_valid_filepath()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.filepath NOT LIKE 'attachments/%' THEN
        RAISE EXCEPTION 'Invalid file path. File must be stored under the "attachments/" directory.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION prevent_attachment_deletion()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM attachments_metadata WHERE attachment_id = OLD.attachments_id) THEN
        RAISE EXCEPTION 'Cannot delete attachment as it is referenced in attachments metadata';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Step 3: Create Triggers If Not Exists 
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'before_insert_check_filepath' 
        AND event_object_table = 'attachments'
    ) THEN
        CREATE TRIGGER before_insert_check_filepath
        BEFORE INSERT ON attachments
        FOR EACH ROW
        EXECUTE FUNCTION check_valid_filepath();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'prevent_attachment_deletion' 
        AND event_object_table = 'attachments'
    ) THEN
        CREATE TRIGGER prevent_attachment_deletion
        BEFORE DELETE ON attachments
        FOR EACH ROW
        EXECUTE FUNCTION prevent_attachment_deletion();
    END IF;
END $$;


-- Attachments MetaData Triggers -- 
CREATE FUNCTION validate_reference_id()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.reference_type = 'question' AND 
       NOT EXISTS (SELECT 1 FROM questions WHERE id = NEW.reference_id) THEN
        RAISE EXCEPTION 'Invalid reference_id: Question does not exist';
    ELSIF NEW.reference_type = 'test' AND 
          NOT EXISTS (SELECT 1 FROM tests WHERE tests_id = NEW.reference_id) THEN
        RAISE EXCEPTION 'Invalid reference_id: Test does not exist';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION prevent_duplicate_attachment()
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

CREATE FUNCTION preserve_attachments_on_reference_delete()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM attachments_metadata 
    WHERE reference_id = OLD.id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Step 3: Create Triggers If Not Exists 
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'enforce_reference_existence' 
        AND event_object_table = 'attachments_metadata'
    ) THEN
        CREATE TRIGGER enforce_reference_existence
        BEFORE INSERT OR UPDATE ON attachments_metadata
        FOR EACH ROW
        EXECUTE FUNCTION validate_reference_id();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'check_duplicate_attachment' 
        AND event_object_table = 'attachments_metadata'
    ) THEN
        CREATE TRIGGER check_duplicate_attachment
        BEFORE INSERT ON attachments_metadata
        FOR EACH ROW
        EXECUTE FUNCTION prevent_duplicate_attachment();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'handle_question_deletion' 
        AND event_object_table = 'questions'
    ) THEN
        CREATE TRIGGER handle_question_deletion
        AFTER DELETE ON questions
        FOR EACH ROW 
        EXECUTE FUNCTION preserve_attachments_on_reference_delete();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'handle_test_deletion' 
        AND event_object_table = 'tests'
    ) THEN
        CREATE TRIGGER handle_test_deletion
        AFTER DELETE ON tests
        FOR EACH ROW 
        EXECUTE FUNCTION preserve_attachments_on_reference_delete();
    END IF;
END $$;



-- Courses Tables Triggers -- 
CREATE FUNCTION ensure_textbook_exists()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.textbook_id IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1 FROM textbook WHERE textbook_id = NEW.textbook_id
        ) THEN
            RAISE EXCEPTION 'Textbook ID % does not exist', NEW.textbook_id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION prevent_duplicate_courses()
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

CREATE FUNCTION cascade_delete_courses()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.role = 'teacher' THEN  -- Use 'teacher' instead of role_id = 2
        DELETE FROM courses WHERE teacher_id = OLD.user_id;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION prevent_course_deletion_if_questions_exist()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM questions WHERE course_id = OLD.course_id) THEN
        RAISE EXCEPTION 'Course ID % cannot be deleted because it has associated questions', OLD.course_id;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION ensure_teacher_exists()
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

-- Step 3: Create Triggers If Not Exists 
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'check_textbook_exists' 
        AND event_object_table = 'courses'
    ) THEN
        CREATE TRIGGER check_textbook_exists
        BEFORE INSERT ON courses
        FOR EACH ROW
        EXECUTE FUNCTION ensure_textbook_exists();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'enforce_unique_teacher_course' 
        AND event_object_table = 'courses'
    ) THEN
        CREATE TRIGGER enforce_unique_teacher_course
        BEFORE INSERT ON courses
        FOR EACH ROW
        EXECUTE FUNCTION prevent_duplicate_courses();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'delete_courses_on_teacher_removal' 
        AND event_object_table = 'users'
    ) THEN
        CREATE TRIGGER delete_courses_on_teacher_removal
        AFTER DELETE ON users
        FOR EACH ROW
        EXECUTE FUNCTION cascade_delete_courses();
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'block_course_deletion' 
        AND event_object_table = 'courses'
    ) THEN
        CREATE TRIGGER block_course_deletion
        BEFORE DELETE ON courses
        FOR EACH ROW
        EXECUTE FUNCTION prevent_course_deletion_if_questions_exist();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'check_teacher_exists' 
        AND event_object_table = 'courses'
    ) THEN
        CREATE TRIGGER check_teacher_exists
        BEFORE INSERT ON courses
        FOR EACH ROW
        EXECUTE FUNCTION ensure_teacher_exists();
    END IF;
END $$;



-- Feedback Table Triggers -- 

-- Step 2: Create Functions 
CREATE FUNCTION ensure_test_or_question_exists()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM tests WHERE tests.tests_id = NEW.test_id) THEN
        RAISE EXCEPTION 'Test ID % does not exist', NEW.test_id;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM questions WHERE questions.id = NEW.question_id) THEN
        RAISE EXCEPTION 'Question ID % does not exist', NEW.question_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION ensure_valid_feedback_user()
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

CREATE FUNCTION prevent_duplicate_feedback()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM feedback 
        WHERE test_id = NEW.test_id 
          AND question_id = NEW.question_id
          AND user_id = NEW.user_id
    ) THEN
        RAISE EXCEPTION 'User % has already provided feedback for Test ID % or Question ID %', 
        NEW.user_id, NEW.test_id, NEW.question_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION cascade_delete_feedback()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM feedback WHERE test_id = OLD.tests_id OR question_id = OLD.id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Step 3: Create Triggers If Not Exists 
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'check_test_or_question_exists' 
        AND event_object_table = 'feedback'
    ) THEN
        CREATE TRIGGER check_test_or_question_exists
        BEFORE INSERT ON feedback
        FOR EACH ROW
        EXECUTE FUNCTION ensure_test_or_question_exists();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'check_feedback_role' 
        AND event_object_table = 'feedback'
    ) THEN
        CREATE TRIGGER check_feedback_role
        BEFORE INSERT ON feedback
        FOR EACH ROW
        EXECUTE FUNCTION ensure_valid_feedback_user();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'enforce_unique_feedback' 
        AND event_object_table = 'feedback'
    ) THEN
        CREATE TRIGGER enforce_unique_feedback
        BEFORE INSERT ON feedback
        FOR EACH ROW
        EXECUTE FUNCTION prevent_duplicate_feedback();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'delete_feedback_on_test_question_removal' 
        AND event_object_table = 'tests'
    ) THEN
        CREATE TRIGGER delete_feedback_on_test_question_removal
        AFTER DELETE ON tests
        FOR EACH ROW
        EXECUTE FUNCTION cascade_delete_feedback();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'delete_feedback_on_question_removal' 
        AND event_object_table = 'questions'
    ) THEN
        CREATE TRIGGER delete_feedback_on_question_removal
        AFTER DELETE ON questions
        FOR EACH ROW
        EXECUTE FUNCTION cascade_delete_feedback();
    END IF;
END $$;



-- Fill in the blank table triggers -- 
-- Step 2: Create Functions 
CREATE FUNCTION prevent_fill_blank_for_non_fill_blank() RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM questions
        WHERE id = NEW.question_id AND type = 'Fill in the Blank'
    ) THEN
        RAISE EXCEPTION 'Only Fill-in-the-Blank questions can have blank answers';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

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

-- Step 3: Create Triggers If Not Exists 
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'trg_prevent_fill_blank_for_non_fill_blank' 
        AND event_object_table = 'questionfillblanks'
    ) THEN
        CREATE TRIGGER trg_prevent_fill_blank_for_non_fill_blank
        BEFORE INSERT ON questionfillblanks
        FOR EACH ROW
        EXECUTE FUNCTION prevent_fill_blank_for_non_fill_blank();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'trg_enforce_minimum_fill_blank_answers' 
        AND event_object_table = 'questionfillblanks'
    ) THEN
        CREATE TRIGGER trg_enforce_minimum_fill_blank_answers
        AFTER INSERT ON questionfillblanks
        FOR EACH ROW
        EXECUTE FUNCTION enforce_minimum_fill_blank_answers();
    END IF;
END $$;



-- Mathching Choice Triggers -- 
-- Step 2: Create Functions 

CREATE FUNCTION prevent_matches_for_non_matching() RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM questions
        WHERE id = NEW.question_id AND type = 'Matching'
    ) THEN
        RAISE EXCEPTION 'Only Matching questions can have match pairs';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

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

-- Step 3: Create Triggers If Not Exists 
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'trg_prevent_matches_for_non_matching' 
        AND event_object_table = 'questionmatches'
    ) THEN
        CREATE TRIGGER trg_prevent_matches_for_non_matching
        BEFORE INSERT ON questionmatches
        FOR EACH ROW
        EXECUTE FUNCTION prevent_matches_for_non_matching();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'trg_enforce_minimum_matching_pairs' 
        AND event_object_table = 'questionmatches'
    ) THEN
        CREATE TRIGGER trg_enforce_minimum_matching_pairs
        AFTER INSERT ON questionmatches
        FOR EACH ROW
        EXECUTE FUNCTION enforce_minimum_matching_pairs();
    END IF;
END $$;



-- Multiple Choice Triggers -- 
-- Step 2: Create Functions 
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

CREATE FUNCTION prevent_publishing_mcq_without_correct_answer() RETURNS TRIGGER AS $$
DECLARE
    correct_count INT;
    question_type VARCHAR(50);
BEGIN
    -- Get the type of the question
    SELECT type INTO question_type FROM questions WHERE id = NEW.id;
    
    -- Only enforce this rule for Multiple Choice questions
    IF question_type = 'Multiple Choice' THEN
        -- Count the number of correct answers
        SELECT COUNT(*) INTO correct_count FROM questionoptions WHERE question_id = NEW.id AND is_correct = TRUE;
        
        -- Prevent publishing if no correct answer exists
        IF correct_count < 1 THEN
            RAISE EXCEPTION 'Multiple Choice questions must have at least one correct answer before being published';
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Step 3: Create Triggers If Not Exists 
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'trg_prevent_options_for_non_mcq' 
        AND event_object_table = 'questionoptions'
    ) THEN
        CREATE TRIGGER trg_prevent_options_for_non_mcq
        BEFORE INSERT ON questionoptions
        FOR EACH ROW
        EXECUTE FUNCTION prevent_options_for_non_mcq();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'trg_enforce_minimum_mcq_options' 
        AND event_object_table = 'questionoptions'
    ) THEN
        CREATE TRIGGER trg_enforce_minimum_mcq_options
        AFTER INSERT ON questionoptions
        FOR EACH ROW
        EXECUTE FUNCTION enforce_minimum_mcq_options();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'trg_enforce_mcq_correct_answer' 
        AND event_object_table = 'questionoptions'
    ) THEN
        CREATE TRIGGER trg_enforce_mcq_correct_answer
        AFTER INSERT OR UPDATE ON questionoptions
        FOR EACH ROW
        EXECUTE FUNCTION enforce_mcq_correct_answer();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'trg_prevent_publishing_mcq_without_correct' 
        AND event_object_table = 'questions'
    ) THEN
        CREATE TRIGGER trg_prevent_publishing_mcq_without_correct
        BEFORE UPDATE ON questions
        FOR EACH ROW
        WHEN (NEW.is_published = TRUE AND OLD.is_published = FALSE)
        EXECUTE FUNCTION prevent_publishing_mcq_without_correct_answer();
    END IF;
END $$;



-- QTI Import Triggers -- 

-- Step 2: Create Functions 
CREATE FUNCTION enforce_test_link_on_import()
RETURNS TRIGGER AS $$
DECLARE
    test_exists BOOLEAN;
BEGIN
    -- Ensure the question source is 'canvas_qti'
    IF NEW.source = 'canvas_qti' THEN
        -- Verify the test exists before linking
        SELECT EXISTS (SELECT 1 FROM tests WHERE tests.tests_id = NEW.test_id) INTO test_exists;
        
        IF NOT test_exists THEN
            RAISE EXCEPTION 'Imported questions must be linked to a valid test.';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Step 3: Create Triggers If Not Exists 
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'trigger_enforce_test_link' 
        AND event_object_table = 'questions'
    ) THEN
        CREATE TRIGGER trigger_enforce_test_link
        BEFORE INSERT ON questions
        FOR EACH ROW
        EXECUTE FUNCTION enforce_test_link_on_import();
    END IF;
END $$;


-- Triggers for Question --- 
-- Step 2: Create Functions 
CREATE FUNCTION set_order_num_for_canvas() 
RETURNS TRIGGER AS $$
BEGIN
    -- Only apply logic for questions coming from 'canvas_qti'
    IF NEW.source = 'canvas_qti' THEN
        -- Ensure 'order_num' is missing before setting it
        IF NEW.order_num IS NULL THEN
            NEW.order_num := (SELECT COALESCE(MAX(order_num), 0) + 1 FROM test_metadata WHERE source = 'canvas_qti');
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION prevent_deleting_published_question() RETURNS TRIGGER AS $$
BEGIN
    -- Verify the question is linked to a published test
    IF EXISTS (
        SELECT 1 FROM tests t
        JOIN Test_MetaData tm ON t.test_id = tm.test_id 
        WHERE tm.question_id = OLD.id AND t.status = 'Published'
    ) THEN
        RAISE EXCEPTION 'Cannot delete a question used in a published test.';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION auto_publish_questions_on_test_publish() RETURNS TRIGGER AS $$
BEGIN
    -- Ensure the test is being updated to 'Published'
    IF NEW.status = 'Published' AND OLD.status <> 'Published' THEN
        -- Update all questions linked to this test
        UPDATE questions
        SET is_published = TRUE
        WHERE id IN (
            SELECT question_id FROM test_metadata WHERE test_id = NEW.tests_id
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION prevent_modifying_published_question() RETURNS TRIGGER AS $$
BEGIN
    -- Allow auto-publishing when test is transitioning to 'Published'
    IF TG_OP = 'UPDATE' AND NEW.is_published = TRUE THEN
        RETURN NEW;
    END IF;

    -- Verify the question is linked to a published test
    IF EXISTS (
        SELECT 1 FROM tests t
        JOIN Test_MetaData tm ON t.tests_id = tm.test_id 
        WHERE tm.question_id = NEW.id AND t.status = 'Published'
    ) THEN
        RAISE EXCEPTION 'Cannot modify a question used in a published test.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE FUNCTION enforce_valid_question_links() RETURNS TRIGGER AS $$
BEGIN
    -- If the question was originally created under a textbook, allow linking to a course
    IF NEW.course_id IS NOT NULL AND NEW.textbook_id IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1 FROM questions WHERE id = NEW.id AND textbook_id IS NOT NULL
        ) THEN
            RAISE EXCEPTION 'A teacher-created question cannot be linked to both a course and a textbook';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

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

-- Step 3: Create Triggers If Not Exists 
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'trg_set_order_num_for_canvas' 
        AND event_object_table = 'questions'
    ) THEN
        CREATE TRIGGER trg_set_order_num_for_canvas
        BEFORE INSERT ON questions
        FOR EACH ROW
        EXECUTE FUNCTION set_order_num_for_canvas();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'no_delete_published_question' 
        AND event_object_table = 'questions'
    ) THEN
        CREATE TRIGGER no_delete_published_question
        BEFORE DELETE ON questions
        FOR EACH ROW
        EXECUTE FUNCTION prevent_deleting_published_question();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'no_modify_published_question' 
        AND event_object_table = 'questions'
    ) THEN
        CREATE TRIGGER no_modify_published_question
        AFTER UPDATE ON questions
        FOR EACH ROW
        EXECUTE FUNCTION prevent_modifying_published_question();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'trg_auto_publish_questions_on_test_publish' 
        AND event_object_table = 'tests'
    ) THEN
        CREATE TRIGGER trg_auto_publish_questions_on_test_publish
        AFTER UPDATE ON tests
        FOR EACH ROW
        EXECUTE FUNCTION auto_publish_questions_on_test_publish();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'trg_enforce_valid_question_links' 
        AND event_object_table = 'questions'
    ) THEN
        CREATE TRIGGER trg_enforce_valid_question_links
        BEFORE INSERT OR UPDATE ON questions
        FOR EACH ROW
        EXECUTE FUNCTION enforce_valid_question_links();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'trg_prevent_options_for_true_false' 
        AND event_object_table = 'questionoptions'
    ) THEN
        CREATE TRIGGER trg_prevent_options_for_true_false
        BEFORE INSERT ON questionoptions
        FOR EACH ROW
        EXECUTE FUNCTION prevent_options_for_true_false();
    END IF;
END $$;

-- Template Table -- 

-- Step 2: Create Functions 
CREATE FUNCTION prevent_duplicate_templates()
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

CREATE FUNCTION prevent_duplicate_file_paths()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM templates WHERE file_path = NEW.file_path) THEN
        RAISE EXCEPTION 'The file path % is already in use', NEW.file_path;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION prevent_template_deletion_if_in_use()
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

-- Step 3: Create Triggers If Not Exists 
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'enforce_unique_template_name' 
        AND event_object_table = 'templates'
    ) THEN
        CREATE TRIGGER enforce_unique_template_name
        BEFORE INSERT ON templates
        FOR EACH ROW
        EXECUTE FUNCTION prevent_duplicate_templates();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'enforce_unique_file_path' 
        AND event_object_table = 'templates'
    ) THEN
        CREATE TRIGGER enforce_unique_file_path
        BEFORE INSERT ON templates
        FOR EACH ROW
        EXECUTE FUNCTION prevent_duplicate_file_paths();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'block_template_deletion' 
        AND event_object_table = 'templates'
    ) THEN
        CREATE TRIGGER block_template_deletion
        BEFORE DELETE ON templates
        FOR EACH ROW
        EXECUTE FUNCTION prevent_template_deletion_if_in_use();
    END IF;
END $$;

-- Test Meta_Data Table 
-- there are no triggers needed for this table
CREATE FUNCTION prevent_adding_questions_to_published_tests()
RETURNS TRIGGER AS $$
BEGIN
    -- Prevent adding new questions if the test is already published
    IF EXISTS (
        SELECT 1 FROM tests 
        WHERE tests.tests_id = NEW.test_id 
        AND status = 'Published'
    ) THEN
        RAISE EXCEPTION 'Cannot add new questions to a published test.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'trg_prevent_adding_questions_to_published_tests' 
        AND event_object_table = 'test_metadata'
    ) THEN
        CREATE TRIGGER trg_prevent_adding_questions_to_published_tests
        BEFORE INSERT ON test_metadata
        FOR EACH ROW
        EXECUTE FUNCTION prevent_adding_questions_to_published_tests();
    END IF;
END $$;



-- Test Table -- 
-- Step 2: Create Functions 
CREATE FUNCTION enforce_status_progression()
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

CREATE FUNCTION check_questions_before_publish()
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
        SELECT COUNT(*) INTO question_count FROM test_metadata WHERE test_id = NEW.tests_id;
        IF question_count = 0 THEN
            RAISE EXCEPTION 'Cannot publish a test without at least one question';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION prevent_published_test_edits()
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

CREATE FUNCTION update_points_before_publish()
RETURNS TRIGGER AS $$
DECLARE
    total_points INT;
BEGIN
    IF NEW.status = 'Published' THEN
        SELECT COALESCE(SUM(points), 0) INTO total_points FROM test_metadata WHERE test_id = NEW.tests_id;
        NEW.points_total := total_points;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Step 3: Create Triggers If Not Exists 
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'check_status_progression' 
        AND event_object_table = 'tests'
    ) THEN
        CREATE TRIGGER check_status_progression
        BEFORE UPDATE ON tests
        FOR EACH ROW
        EXECUTE FUNCTION enforce_status_progression();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'ensure_questions_before_publish' 
        AND event_object_table = 'tests'
    ) THEN
        CREATE TRIGGER ensure_questions_before_publish
        BEFORE UPDATE ON tests
        FOR EACH ROW
        EXECUTE FUNCTION check_questions_before_publish();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'restrict_published_test_edits' 
        AND event_object_table = 'tests'
    ) THEN
        CREATE TRIGGER restrict_published_test_edits
        BEFORE UPDATE ON tests
        FOR EACH ROW
        EXECUTE FUNCTION prevent_published_test_edits();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'update_points_publish' 
        AND event_object_table = 'tests'
    ) THEN
        CREATE TRIGGER update_points_publish
        BEFORE UPDATE ON tests
        FOR EACH ROW
        EXECUTE FUNCTION update_points_before_publish();
    END IF;
END $$;



-- Textbook Triggers -- 
-- Step 2: Create Functions 
CREATE FUNCTION prevent_duplicate_isbn()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM textbook WHERE textbook_isbn = NEW.textbook_isbn) THEN
        RAISE EXCEPTION 'A textbook with ISBN % already exists', NEW.textbook_isbn;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION ensure_publisher_exists()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM users WHERE user_id = NEW.publisher_id AND role = 'publisher'
    ) THEN
        RAISE EXCEPTION 'User ID % is not a publisher and cannot create textbooks', NEW.publisher_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION prevent_duplicate_title_version()
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

-- Step 3: Create Triggers If Not Exists 
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'enforce_unique_isbn' 
        AND event_object_table = 'textbook'
    ) THEN
        CREATE TRIGGER enforce_unique_isbn
        BEFORE INSERT ON textbook
        FOR EACH ROW
        EXECUTE FUNCTION prevent_duplicate_isbn();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'check_publisher_exists' 
        AND event_object_table = 'textbook'
    ) THEN
        CREATE TRIGGER check_publisher_exists
        BEFORE INSERT ON textbook
        FOR EACH ROW
        EXECUTE FUNCTION ensure_publisher_exists();
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'enforce_unique_title_version' 
        AND event_object_table = 'textbook'
    ) THEN
        CREATE TRIGGER enforce_unique_title_version
        BEFORE INSERT ON textbook
        FOR EACH ROW
        EXECUTE FUNCTION prevent_duplicate_title_version();
    END IF;
END $$;


-- users Table -- 
-- Step 2: Create Functions 
CREATE FUNCTION enforce_lowercase_username()
RETURNS TRIGGER AS $$
BEGIN
    NEW.username := LOWER(NEW.username);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Step 3: Create Triggers If Not Exists 
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'enforce_lowercase_username_trigger' 
        AND event_object_table = 'users'
    ) THEN
        CREATE TRIGGER enforce_lowercase_username_trigger
        BEFORE INSERT OR UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION enforce_lowercase_username();
    END IF;
END $$;

