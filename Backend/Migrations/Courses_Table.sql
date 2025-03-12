CREATE TABLE IF NOT EXISTS Courses (
    course_id SERIAL PRIMARY KEY,
    course_name VARCHAR(255) NOT NULL,
    teacher_id UUID NOT NULL,
    textbook_id INT NOT NULL
);