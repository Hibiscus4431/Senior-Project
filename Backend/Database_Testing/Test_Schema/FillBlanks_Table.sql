CREATE TABLE IF NOT EXISTS QuestionFillBlanks (
    blank_id SERIAL PRIMARY KEY,
    question_id INT NOT NULL,
    correct_text TEXT NOT NULL  
);
