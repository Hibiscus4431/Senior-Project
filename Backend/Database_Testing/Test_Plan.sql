-- Test Data Script for Local Testing
-- This script will insert sample data into the test database

-- 1️⃣ Insert Test Users (Webmaster, Teachers, Publisher)
INSERT INTO Users (role, username, password) VALUES 
('Webmaster', 'admin', 'securepass'),
('Teacher', 'teacher1', 'password123'),
('Teacher', 'teacher2', 'password123'),
('Publisher', 'publisher1', 'password123');

-- 2️⃣ Insert Sample Courses
INSERT INTO Courses (course_name, teacher_id, textbook_id) VALUES 
('CS 101', 2, 1),
('Math 201', 3, 2);

-- 3️⃣ Insert Sample Textbooks
INSERT INTO Textbook (textbook_title, textbook_author, textbook_version, textbook_isbn) VALUES 
('Intro to CS', 'John Doe', '1st Edition', '123-456-789'),
('Advanced Math', 'Jane Smith', '2nd Edition', '987-654-321');

-- 4️⃣ Insert Sample Questions (Multiple Types)
INSERT INTO Questions (course_id, textbook_id, question_text, type, default_points, owner_id, is_published, chapter_number, section_number) VALUES 
(1, NULL, 'What is 2 + 2?', 'Multiple Choice', 5, 2, FALSE, 1, 'A'),
(NULL, 1, 'Define an Algorithm.', 'Short Answer', 10, 4, FALSE, 1, 'B'),
(NULL, 1, 'The capital of France is _______.', 'Fill in the Blank', 5, 3, FALSE, 2, 'C'),
(2, NULL, 'What is the square root of 16?', 'Multiple Choice', 5, 2, FALSE, 2, 'A'),
(NULL, 2, 'Match the following terms with their definitions.', 'Matching', 10, 3, FALSE, 1, 'B');

-- 5️⃣ Insert Sample Tests
INSERT INTO Tests (course_id, user_id, name, status, points_total, estimated_time) VALUES 
(1, 2, 'Midterm Exam', 'Draft', 100, 60),
(2, 3, 'Final Exam', 'Draft', 120, 90);

-- 6️⃣ Link Questions to Tests
INSERT INTO Test_MetaData (test_id, question_id, points, order_num) VALUES 
(1, 1, 5, 1),
(1, 2, 10, 2),
(2, 3, 5, 1);

-- 7️⃣ Verify Constraints and Foreign Keys
-- Trying to insert a question with an invalid type (Should Fail)
INSERT INTO Questions (course_id, textbook_id, question_text, type, default_points, owner_id, is_published) 
VALUES (1, NULL, 'This should fail', 'InvalidType', 5, 2, FALSE);

-- 8️⃣ Prevent Modification of a Published Question (Should Fail)
UPDATE Questions 
SET question_text = 'Updated text'
WHERE id = (SELECT id FROM Questions WHERE is_published = TRUE LIMIT 1);

-- 9️⃣ Prevent Deletion of a Question Used in a Published Test (Should Fail)
DELETE FROM Questions 
WHERE id = (SELECT question_id FROM Test_MetaData tm 
JOIN Tests t ON tm.test_id = t.tests_id 
WHERE t.status = 'Published' LIMIT 1);

-- 🔟 Retrieve All Questions Associated with a Test
SELECT q.* FROM Questions q
JOIN Test_MetaData tm ON q.id = tm.question_id
WHERE tm.test_id = 1;

-- 🔟✅ Verify Points and Estimated Time are Stored Correctly
SELECT name, points_total, estimated_time FROM Tests;
