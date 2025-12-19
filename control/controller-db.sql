-- Limpa tabelas antigas se existirem (para recriação limpa)
DROP TABLE IF EXISTS verified_answers CASCADE;
DROP TABLE IF EXISTS extra_notes CASCADE;
DROP TABLE IF EXISTS session_strategies CASCADE;
DROP TABLE IF EXISTS session_teachers CASCADE;
DROP TABLE IF EXISTS session_students CASCADE;
DROP TABLE IF EXISTS session_domains CASCADE;
DROP TABLE IF EXISTS session CASCADE;

-- 1. Tabela Session (Tabela Pai)
CREATE TABLE session (
    id SERIAL PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    start_time TIMESTAMP,
    current_tactic_index INTEGER DEFAULT 0,
    current_tactic_started_at TIMESTAMP,
    original_strategy_id VARCHAR(50)
);

-- 2. Tabelas normalizadas (Relacionamentos)

CREATE TABLE session_strategies (
    session_id INTEGER NOT NULL,
    strategy_id VARCHAR(50) NOT NULL,
    PRIMARY KEY (session_id, strategy_id),
    CONSTRAINT fk_session_strategies
        FOREIGN KEY (session_id)
        REFERENCES session (id)
        ON DELETE CASCADE
);

CREATE TABLE session_teachers (
    session_id INTEGER NOT NULL,
    teacher_id VARCHAR(50) NOT NULL,
    PRIMARY KEY (session_id, teacher_id),
    CONSTRAINT fk_session_teachers
        FOREIGN KEY (session_id)
        REFERENCES session (id)
        ON DELETE CASCADE
);

CREATE TABLE session_students (
    session_id INTEGER NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    PRIMARY KEY (session_id, student_id),
    CONSTRAINT fk_session_students
        FOREIGN KEY (session_id)
        REFERENCES session (id)
        ON DELETE CASCADE
);

CREATE TABLE session_domains (
    session_id INTEGER NOT NULL,
    domain_id VARCHAR(50) NOT NULL,
    PRIMARY KEY (session_id, domain_id),
    CONSTRAINT fk_session_domains
        FOREIGN KEY (session_id)
        REFERENCES session (id)
        ON DELETE CASCADE
);

-- 3. Tabela ExtraNotes
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

-- 4. Tabela VerifiedAnswers
CREATE TABLE verified_answers (
    id SERIAL PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    -- Nota: Mantendo VARCHAR(50) conforme original
    student_id VARCHAR(50) NOT NULL, 
    answers JSONB NOT NULL,
    score INTEGER NOT NULL DEFAULT 0,
    session_id INTEGER NOT NULL,
    
    CONSTRAINT fk_session_verified_answers
        FOREIGN KEY (session_id)
        REFERENCES session (id)
        ON DELETE CASCADE
);
