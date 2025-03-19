CREATE TABLE IF NOT EXISTS QuestionMatches (
    match_id SERIAL PRIMARY KEY,
    question_id INT NOT NULL,
    prompt_text TEXT NOT NULL,  
    match_text TEXT NOT NULL  
);
