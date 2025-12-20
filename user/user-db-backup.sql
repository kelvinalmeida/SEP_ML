--
-- PostgreSQL database dump
--

\restrict LJK65mtKckaOBTiYjfwRp3Q4TvSVKKE9ueebHfrPRv65A2N5EQo6gIEjwaf4cfH

-- Dumped from database version 18.1 (Debian 18.1-1.pgdg13+2)
-- Dumped by pg_dump version 18.1 (Debian 18.1-1.pgdg13+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: student; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.student (
    student_id integer NOT NULL,
    name character varying(100),
    course character varying(100),
    type character varying(20),
    age smallint,
    username character varying(80),
    email character varying(80),
    password_hash character varying(128)
);


ALTER TABLE public.student OWNER TO "user";

--
-- Name: student_student_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

ALTER TABLE public.student ALTER COLUMN student_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.student_student_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: teacher; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.teacher (
    teacher_id integer NOT NULL,
    name character varying(100),
    course character varying(100),
    type character varying(20),
    age smallint,
    username character varying(80),
    email character varying(80),
    password_hash character varying(128)
);


ALTER TABLE public.teacher OWNER TO "user";

--
-- Name: teacher_teacher_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

ALTER TABLE public.teacher ALTER COLUMN teacher_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.teacher_teacher_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Data for Name: student; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.student (student_id, name, course, type, age, username, email, password_hash) FROM stdin;
1	kelvin	CC	student	22	kelvin	kelvinsantos13@hotmail.com	88092018
\.


--
-- Data for Name: teacher; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.teacher (teacher_id, name, course, type, age, username, email, password_hash) FROM stdin;
1	kelvin123	\N	teacher	33	kelvin123	ksal@ic.ufal.br	88092018
\.


--
-- Name: student_student_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.student_student_id_seq', 1, true);


--
-- Name: teacher_teacher_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.teacher_teacher_id_seq', 1, true);


--
-- Name: student student_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.student
    ADD CONSTRAINT student_pkey PRIMARY KEY (student_id);


--
-- Name: teacher teacher_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.teacher
    ADD CONSTRAINT teacher_pkey PRIMARY KEY (teacher_id);


--
-- PostgreSQL database dump complete
--

\unrestrict LJK65mtKckaOBTiYjfwRp3Q4TvSVKKE9ueebHfrPRv65A2N5EQo6gIEjwaf4cfH

