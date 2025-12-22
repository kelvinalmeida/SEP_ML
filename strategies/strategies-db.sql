-- ==========================================================
-- 1. DDL: CRIAÇÃO DA ESTRUTURA (SCHEMA)
-- ==========================================================

DROP TABLE IF EXISTS private_message CASCADE;
DROP TABLE IF EXISTS general_message CASCADE;
DROP TABLE IF EXISTS tactics CASCADE;
DROP TABLE IF EXISTS strategies CASCADE;
DROP TABLE IF EXISTS message CASCADE;

-- Tabela Strategies
CREATE TABLE strategies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    score INTEGER DEFAULT 0
);

-- Tabela Message (Necessária para referências de chat)
CREATE TABLE message (
    id SERIAL PRIMARY KEY
);

-- Tabela Tactics
CREATE TABLE tactics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    time FLOAT,
    chat_id INTEGER, 
    strategy_id INTEGER NOT NULL, 
    
    CONSTRAINT fk_strategies
      FOREIGN KEY(strategy_id) 
      REFERENCES strategies(id)
      ON DELETE CASCADE
);

-- Tabela General Message
CREATE TABLE general_message (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    message_id INTEGER NOT NULL, 
    
    CONSTRAINT fk_message_room
      FOREIGN KEY(message_id) 
      REFERENCES message(id)
      ON DELETE CASCADE
);

-- Tabela Private Message
CREATE TABLE private_message (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL,
    username VARCHAR(80) NOT NULL,
    target_username VARCHAR(80) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    message_id INTEGER NOT NULL, 
    
    CONSTRAINT fk_message_parent
        FOREIGN KEY (message_id) 
        REFERENCES message(id)
        ON DELETE CASCADE
);

-- ==========================================================
-- 2. DML: POPULAÇÃO DOS DADOS (INSERTS)
-- ==========================================================

-- 1. Inserir Strategies
INSERT INTO strategies (id, name, score) VALUES
(1, 'estra 1', 8),
(2, 'estra 2', 7),
(3, 'strategia mudandanca de estrategia', 9);

-- 2. Inserir Messages (Placeholders para os chats)
-- Inserimos IDs 1, 2 e 3 pois são usados nas tabelas tactics e general_message
INSERT INTO message (id) VALUES (1), (2), (3);

-- 3. Inserir Tactics
INSERT INTO tactics (id, name, description, time, chat_id, strategy_id) VALUES 
(1, 'Reuso', '', 22, NULL, 1),
(2, 'Debate Sincrono', '', 22, 1, 1),
(3, 'Apresentacao Sincrona', 'https://meet.google.com/dxt-mbyg-gvs', 22, NULL, 1),
(4, 'Envio de Informacao', '', 22, NULL, 1),
(5, 'Debate Sincrono', '', 33, 2, 2),
(6, 'Apresentacao Sincrona', 'https://meet.google.com/dxt-mbyg-gvs', 33, NULL, 2),
(7, 'Envio de Informacao', '', 33, NULL, 2),
(8, 'Reuso', '', 33, NULL, 2),
(9, 'Debate Sincrono', '', 0.1, 3, 3),
(10, 'Mudanca de Estrategia', '1', 1, NULL, 3);

-- 4. Inserir General Messages
INSERT INTO general_message (id, username, content, timestamp, message_id) VALUES 
(1, 'kelvin123', 'aviso - kelvin123 entrou na sala geral.', '2025-12-06 00:50:05.133227', 2),
(2, 'kelvin123', 'aviso - kelvin123 entrou na sala geral.', '2025-12-06 00:51:04.762456', 2),
(3, 'kelvin123', 'aviso - kelvin123 entrou na sala geral.', '2025-12-06 00:59:27.285803', 2);

-- 5. Atualizar Sequências (IMPORTANTE)
-- Como inserimos IDs manualmente, precisamos dizer ao Postgres para continuar a partir do próximo número
SELECT setval('strategies_id_seq', (SELECT MAX(id) FROM strategies));
SELECT setval('tactics_id_seq', (SELECT MAX(id) FROM tactics));
SELECT setval('message_id_seq', (SELECT MAX(id) FROM message));
SELECT setval('general_message_id_seq', (SELECT MAX(id) FROM general_message));
SELECT setval('private_message_id_seq', (SELECT MAX(id) FROM private_message) + 1, false); -- Garante que comece do 1 se estiver vazio
