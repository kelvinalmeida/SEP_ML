-- Limpa tabelas antigas se existirem (para recriação limpa)
DROP TABLE IF EXISTS verified_answers CASCADE;
DROP TABLE IF EXISTS extra_notes CASCADE;
DROP TABLE IF EXISTS session CASCADE;

-- 1. Tabela Session (Tabela Pai)
CREATE TABLE session (
    id SERIAL PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    
    -- Colunas que eram PickleType viram JSONB.
    -- O padrão '[]'::jsonb garante que comece com uma lista vazia, igual ao default=list do Python.
    strategies JSONB NOT NULL DEFAULT '[]'::jsonb,
    teachers JSONB NOT NULL DEFAULT '[]'::jsonb,
    students JSONB NOT NULL DEFAULT '[]'::jsonb,
    domains JSONB NOT NULL DEFAULT '[]'::jsonb,
    
    code VARCHAR(50) NOT NULL UNIQUE,
    start_time TIMESTAMP
);

-- 2. Tabela ExtraNotes
CREATE TABLE extra_notes (
    id SERIAL PRIMARY KEY,
    estudante_username VARCHAR(100) NOT NULL,
    student_id INTEGER NOT NULL,
    extra_notes FLOAT NOT NULL DEFAULT 0.0,
    session_id INTEGER NOT NULL,
    
    CONSTRAINT fk_session_extra_notes
        FOREIGN KEY (session_id)
        REFERENCES session (id)
        ON DELETE CASCADE
);

-- 3. Tabela VerifiedAnswers
CREATE TABLE verified_answers (
    id SERIAL PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    -- Nota: No seu modelo Python, student_id aqui é String(50), diferente de ExtraNotes (Integer)
    student_id VARCHAR(50) NOT NULL, 
    answers JSONB NOT NULL,
    score INTEGER NOT NULL DEFAULT 0,
    session_id INTEGER NOT NULL,
    
    CONSTRAINT fk_session_verified_answers
        FOREIGN KEY (session_id)
        REFERENCES session (id)
        ON DELETE CASCADE
);