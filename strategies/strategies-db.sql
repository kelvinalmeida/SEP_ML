-- 1. (Optional) Create the database first if it doesn't exist
-- CREATE DATABASE game_db;

-- 2. Connect to the database (if running in psql terminal)
-- \c game_db

DROP TABLE IF EXISTS strategies CASCADE;
DROP TABLE IF EXISTS message CASCADE;
DROP TABLE IF EXISTS private_message CASCADE;
DROP TABLE IF EXISTS tactics CASCADE;
DROP TABLE IF EXISTS general_message CASCADE;

-- 3. Create the Strategies table
CREATE TABLE strategies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE tactics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    time FLOAT,
    chat_id INTEGER, -- Pode ser nulo conforme seu JSON
    strategy_id INTEGER NOT NULL, -- O relacionamento (Chave Estrangeira)
    
    CONSTRAINT fk_strategies
      FOREIGN KEY(strategy_id) 
      REFERENCES strategies(id)
      ON DELETE CASCADE -- Se deletar a estratégia, deleta as táticas dela
);

-- 4. Create the Message table
CREATE TABLE message (
    id SERIAL PRIMARY KEY
);

CREATE TABLE general_message (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Bom ter horário da mensagem
    message_id INTEGER NOT NULL, -- Chave estrangeira para a tabela pai (sala)
    
    CONSTRAINT fk_message_room
      FOREIGN KEY(message_id) 
      REFERENCES message(id)
      ON DELETE CASCADE
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