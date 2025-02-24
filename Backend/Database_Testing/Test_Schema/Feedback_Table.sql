CREATE TABLE IF NOT EXISTS Feedback (
    feedback_id SERIAL PRIMARY KEY,
    test_id INT NOT NULL,
    question_id INT NOT NULL,
    comment_field TEXT
);

ALTER TABLE feedback 
ADD COLUMN IF NOT EXISTS user_id INT NOT NULL;