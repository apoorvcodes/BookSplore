CREATE TABLE users(
id BIGSERIAL PRIMARY KEY,
first_name VARCHAR(100),
last_name VARCHAR(100),
email VARCHAR(255) NOT NULL UNIQUE,
avatar_url text,
followers json DEFAULT '[]',
following json DEFAULT '[]'
);

CREATE TABLE reviews(
    id BIGSERIAL PRIMARY KEY,
    book_id VARCHAR(150) NOT NULL,
    user_id INT NOT NULL,
    stay_anonymous BOOLEAN DEFAULT TRUE,
    content TEXT NOT NULL,
    "timestamp" TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW())::TIMESTAMP WITHOUT TIME ZONE,
    rating INTEGER CONSTRAINT rating_range CHECK (rating >= 0 AND rating <=5)
);