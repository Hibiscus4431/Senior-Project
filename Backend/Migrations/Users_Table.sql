CREATE TYPE user_role as ENUM ('Teacher', 'Publisher', 'Webmaster');

CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    role user_role NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);
