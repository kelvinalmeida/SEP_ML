-- Limpeza inicial (opcional: remove as tabelas se já existirem para recriar do zero)
DROP TABLE IF EXISTS video_youtube CASCADE;
DROP TABLE IF EXISTS video_upload CASCADE;
DROP TABLE IF EXISTS pdf CASCADE;
DROP TABLE IF EXISTS exercise CASCADE;
DROP TABLE IF EXISTS domain CASCADE;

-- 1. Tabela Domain (Tabela Pai)
CREATE TABLE domain (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT
);

-- 2. Tabela Exercise
CREATE TABLE exercise (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    -- Recomendo usar JSONB no Postgres. Se preferir texto puro, mude para TEXT.
    options JSONB NOT NULL, 
    correct VARCHAR(10) NOT NULL,
    domain_id INTEGER NOT NULL,
    
    CONSTRAINT fk_domain_exercise 
        FOREIGN KEY (domain_id) 
        REFERENCES domain (id) 
        ON DELETE CASCADE
);

-- 3. Tabela VideoUpload
CREATE TABLE video_upload (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    path VARCHAR(255) NOT NULL,
    domain_id INTEGER NOT NULL,

    CONSTRAINT fk_domain_video_upload 
        FOREIGN KEY (domain_id) 
        REFERENCES domain (id) 
        ON DELETE CASCADE
);

-- 4. Tabela VideoYoutube
CREATE TABLE video_youtube (
    id SERIAL PRIMARY KEY,
    url VARCHAR(500) NOT NULL,
    domain_id INTEGER NOT NULL,

    CONSTRAINT fk_domain_video_youtube 
        FOREIGN KEY (domain_id) 
        REFERENCES domain (id) 
        ON DELETE CASCADE
);

-- 5. Tabela PDF
CREATE TABLE pdf (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    path VARCHAR(255) NOT NULL,
    domain_id INTEGER NOT NULL,

    CONSTRAINT fk_domain_pdf 
        FOREIGN KEY (domain_id) 
        REFERENCES domain (id) 
        ON DELETE CASCADE
);