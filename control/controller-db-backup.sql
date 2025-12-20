--
-- PostgreSQL database dump
--

\restrict fCanJFsErwziQBAiKLjHV8sjA0pupK207Nf2is8CdQl4cVYTKfbbnB55Nt5eg8H

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
-- Name: extra_notes; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.extra_notes (
    id integer NOT NULL,
    estudante_username character varying(100) NOT NULL,
    student_id integer NOT NULL,
    extra_notes double precision DEFAULT 0.0 NOT NULL,
    session_id integer NOT NULL
);


ALTER TABLE public.extra_notes OWNER TO "user";

--
-- Name: extra_notes_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.extra_notes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.extra_notes_id_seq OWNER TO "user";

--
-- Name: extra_notes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.extra_notes_id_seq OWNED BY public.extra_notes.id;


--
-- Name: session; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.session (
    id integer NOT NULL,
    status character varying(50) NOT NULL,
    code character varying(50) NOT NULL,
    start_time timestamp without time zone,
    current_tactic_index integer DEFAULT 0,
    current_tactic_started_at timestamp without time zone
);


ALTER TABLE public.session OWNER TO "user";

--
-- Name: session_domains; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.session_domains (
    session_id integer NOT NULL,
    domain_id character varying(50) NOT NULL
);


ALTER TABLE public.session_domains OWNER TO "user";

--
-- Name: session_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.session_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.session_id_seq OWNER TO "user";

--
-- Name: session_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.session_id_seq OWNED BY public.session.id;


--
-- Name: session_strategies; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.session_strategies (
    session_id integer NOT NULL,
    strategy_id character varying(50) NOT NULL
);


ALTER TABLE public.session_strategies OWNER TO "user";

--
-- Name: session_students; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.session_students (
    session_id integer NOT NULL,
    student_id character varying(50) NOT NULL
);


ALTER TABLE public.session_students OWNER TO "user";

--
-- Name: session_teachers; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.session_teachers (
    session_id integer NOT NULL,
    teacher_id character varying(50) NOT NULL
);


ALTER TABLE public.session_teachers OWNER TO "user";

--
-- Name: verified_answers; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.verified_answers (
    id integer NOT NULL,
    student_name character varying(100) NOT NULL,
    student_id character varying(50) NOT NULL,
    answers jsonb NOT NULL,
    score integer DEFAULT 0 NOT NULL,
    session_id integer NOT NULL
);


ALTER TABLE public.verified_answers OWNER TO "user";

--
-- Name: verified_answers_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.verified_answers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.verified_answers_id_seq OWNER TO "user";

--
-- Name: verified_answers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.verified_answers_id_seq OWNED BY public.verified_answers.id;


--
-- Name: extra_notes id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.extra_notes ALTER COLUMN id SET DEFAULT nextval('public.extra_notes_id_seq'::regclass);


--
-- Name: session id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.session ALTER COLUMN id SET DEFAULT nextval('public.session_id_seq'::regclass);


--
-- Name: verified_answers id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.verified_answers ALTER COLUMN id SET DEFAULT nextval('public.verified_answers_id_seq'::regclass);


--
-- Data for Name: extra_notes; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.extra_notes (id, estudante_username, student_id, extra_notes, session_id) FROM stdin;
\.


--
-- Data for Name: session; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.session (id, status, code, start_time, current_tactic_index, current_tactic_started_at) FROM stdin;
2	aguardando	YDHIAZJQ	\N	0	\N
\.


--
-- Data for Name: session_domains; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.session_domains (session_id, domain_id) FROM stdin;
2	3
\.


--
-- Data for Name: session_strategies; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.session_strategies (session_id, strategy_id) FROM stdin;
2	1
\.


--
-- Data for Name: session_students; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.session_students (session_id, student_id) FROM stdin;
2	1
\.


--
-- Data for Name: session_teachers; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.session_teachers (session_id, teacher_id) FROM stdin;
2	1
\.


--
-- Data for Name: verified_answers; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.verified_answers (id, student_name, student_id, answers, score, session_id) FROM stdin;
\.


--
-- Name: extra_notes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.extra_notes_id_seq', 1, true);


--
-- Name: session_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.session_id_seq', 2, true);


--
-- Name: verified_answers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.verified_answers_id_seq', 1, true);


--
-- Name: extra_notes extra_notes_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.extra_notes
    ADD CONSTRAINT extra_notes_pkey PRIMARY KEY (id);


--
-- Name: session session_code_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.session
    ADD CONSTRAINT session_code_key UNIQUE (code);


--
-- Name: session_domains session_domains_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.session_domains
    ADD CONSTRAINT session_domains_pkey PRIMARY KEY (session_id, domain_id);


--
-- Name: session session_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.session
    ADD CONSTRAINT session_pkey PRIMARY KEY (id);


--
-- Name: session_strategies session_strategies_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.session_strategies
    ADD CONSTRAINT session_strategies_pkey PRIMARY KEY (session_id, strategy_id);


--
-- Name: session_students session_students_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.session_students
    ADD CONSTRAINT session_students_pkey PRIMARY KEY (session_id, student_id);


--
-- Name: session_teachers session_teachers_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.session_teachers
    ADD CONSTRAINT session_teachers_pkey PRIMARY KEY (session_id, teacher_id);


--
-- Name: verified_answers verified_answers_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.verified_answers
    ADD CONSTRAINT verified_answers_pkey PRIMARY KEY (id);


--
-- Name: session_domains fk_session_domains; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.session_domains
    ADD CONSTRAINT fk_session_domains FOREIGN KEY (session_id) REFERENCES public.session(id) ON DELETE CASCADE;


--
-- Name: extra_notes fk_session_extra_notes; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.extra_notes
    ADD CONSTRAINT fk_session_extra_notes FOREIGN KEY (session_id) REFERENCES public.session(id) ON DELETE CASCADE;


--
-- Name: session_strategies fk_session_strategies; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.session_strategies
    ADD CONSTRAINT fk_session_strategies FOREIGN KEY (session_id) REFERENCES public.session(id) ON DELETE CASCADE;


--
-- Name: session_students fk_session_students; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.session_students
    ADD CONSTRAINT fk_session_students FOREIGN KEY (session_id) REFERENCES public.session(id) ON DELETE CASCADE;


--
-- Name: session_teachers fk_session_teachers; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.session_teachers
    ADD CONSTRAINT fk_session_teachers FOREIGN KEY (session_id) REFERENCES public.session(id) ON DELETE CASCADE;


--
-- Name: verified_answers fk_session_verified_answers; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.verified_answers
    ADD CONSTRAINT fk_session_verified_answers FOREIGN KEY (session_id) REFERENCES public.session(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict fCanJFsErwziQBAiKLjHV8sjA0pupK207Nf2is8CdQl4cVYTKfbbnB55Nt5eg8H

