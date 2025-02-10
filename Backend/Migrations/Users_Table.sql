CREATE TYPE user_role as ENUM ('Teacher', 'Publisher', 'Webmaster');

CREATE TABLE IF NOT EXISTS Users (
    user_id SERIAL PRIMARY KEY,
    role user_role NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    password BYTEA NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
