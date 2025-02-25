CREATE TABLE IF NOT EXISTS Feedback (
    feedback_id SERIAL PRIMARY KEY,
    test_id INT NOT NULL,
    question_id INT NOT NULL,
    comment_field TEXT,
    user_id INT NOT NULL
);