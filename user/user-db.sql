-- ==========================================================
-- 1. DDL: CRIAÇÃO DA ESTRUTURA (SCHEMA)
-- ==========================================================

DROP TABLE IF EXISTS student CASCADE;
DROP TABLE IF EXISTS teacher CASCADE;

CREATE TABLE student(
    student_id INT GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(100),
    course VARCHAR(100),
    type VARCHAR(20),
    age SMALLINT,
    username VARCHAR(80),
    email VARCHAR(80),
    password_hash VARCHAR(128),
    PRIMARY KEY (student_id)
);

CREATE TABLE teacher(
    teacher_id INT GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(100),
    course VARCHAR(100),
    type VARCHAR(20),
    age SMALLINT,
    username VARCHAR(80),
    email VARCHAR(80),
    password_hash VARCHAR(128),
    PRIMARY KEY (teacher_id)
);

-- ==========================================================
-- 2. DML: POPULAÇÃO DOS DADOS (INSERTS)
-- ==========================================================

-- Inserindo Student (ID 1)
INSERT INTO student (student_id, name, course, type, age, username, email, password_hash)
OVERRIDING SYSTEM VALUE 
VALUES (1, 'kelvin', 'CC', 'student', 22, 'kelvin', 'kelvinsantos13@hotmail.com', '88092018');

-- Inserindo Teacher (ID 1)
INSERT INTO teacher (teacher_id, name, course, type, age, username, email, password_hash)
OVERRIDING SYSTEM VALUE 
VALUES (1, 'kelvin123', NULL, 'teacher', 33, 'kelvin123', 'ksal@ic.ufal.br', '88092018');

-- ==========================================================
-- 3. RESET DE SEQUÊNCIAS
-- ==========================================================
-- Importante para garantir que o próximo insert automático seja ID 2, e não tente usar o 1 de novo.

SELECT setval(pg_get_serial_sequence('student', 'student_id'), (SELECT MAX(student_id) FROM student));
SELECT setval(pg_get_serial_sequence('teacher', 'teacher_id'), (SELECT MAX(teacher_id) FROM teacher));