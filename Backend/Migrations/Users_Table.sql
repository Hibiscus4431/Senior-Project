
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN 
        CREATE TYPE user_role AS ENUM ('teacher', 'publisher', 'webmaster'); 
    END IF; 
END $$;


CREATE TABLE IF NOT EXISTS Users (
    user_id SERIAL PRIMARY KEY,
    role user_role NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    password BYTEA NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
