-- 1. (Optional) Create the database first if it doesn't exist
-- CREATE DATABASE game_db;

-- 2. Connect to the database (if running in psql terminal)
-- \c game_db

DROP TABLE IF EXISTS strategies CASCADE;
DROP TABLE IF EXISTS message CASCADE;
DROP TABLE IF EXISTS private_message CASCADE;

-- 3. Create the Strategies table
CREATE TABLE strategies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    -- JSONB is the Postgres replacement for PickleType
    -- We default it to an empty JSON array '[]'
    tatics JSONB NOT NULL DEFAULT '[]'::jsonb
);

-- 4. Create the Message table
CREATE TABLE message (
    id SERIAL PRIMARY KEY,
    -- Stores the general messages list as JSON
    messages JSONB NOT NULL DEFAULT '[]'::jsonb
);

-- 5. Create the PrivateMessage table
CREATE TABLE private_message (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL,
    username VARCHAR(80) NOT NULL,
    target_username VARCHAR(80) NOT NULL,
    content TEXT NOT NULL,
    -- "TIMESTAMP WITH TIME ZONE" corresponds to timezone=True in SQLAlchemy
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    message_id INTEGER NOT NULL,
    
    -- This creates the relationship to the Message table
    -- ON DELETE CASCADE ensures that if a Message is deleted, 
    -- its private messages are also deleted (matching your Python cascade rule)
    CONSTRAINT fk_message_parent
        FOREIGN KEY (message_id) 
        REFERENCES message(id)
        ON DELETE CASCADE
);