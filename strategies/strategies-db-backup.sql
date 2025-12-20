--
-- PostgreSQL database dump
--

\restrict Vg5OFvt5eOsnNeWNlqbxWUwYhodkzbNt9z2YKUKgjKJ3VobCcFIj8BCYSitpwXa

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
-- Name: general_message; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.general_message (
    id integer NOT NULL,
    username character varying(100) NOT NULL,
    content text NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    message_id integer NOT NULL
);


ALTER TABLE public.general_message OWNER TO "user";

--
-- Name: general_message_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.general_message_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.general_message_id_seq OWNER TO "user";

--
-- Name: general_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.general_message_id_seq OWNED BY public.general_message.id;


--
-- Name: message; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.message (
    id integer NOT NULL
);


ALTER TABLE public.message OWNER TO "user";

--
-- Name: message_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.message_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.message_id_seq OWNER TO "user";

--
-- Name: message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.message_id_seq OWNED BY public.message.id;


--
-- Name: private_message; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.private_message (
    id integer NOT NULL,
    sender_id integer NOT NULL,
    username character varying(80) NOT NULL,
    target_username character varying(80) NOT NULL,
    content text NOT NULL,
    "timestamp" timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    message_id integer NOT NULL
);


ALTER TABLE public.private_message OWNER TO "user";

--
-- Name: private_message_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.private_message_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.private_message_id_seq OWNER TO "user";

--
-- Name: private_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.private_message_id_seq OWNED BY public.private_message.id;


--
-- Name: strategies; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.strategies (
    id integer NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.strategies OWNER TO "user";

--
-- Name: strategies_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.strategies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.strategies_id_seq OWNER TO "user";

--
-- Name: strategies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.strategies_id_seq OWNED BY public.strategies.id;


--
-- Name: tactics; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.tactics (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    "time" double precision,
    chat_id integer,
    strategy_id integer NOT NULL
);


ALTER TABLE public.tactics OWNER TO "user";

--
-- Name: tactics_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.tactics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tactics_id_seq OWNER TO "user";

--
-- Name: tactics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.tactics_id_seq OWNED BY public.tactics.id;


--
-- Name: general_message id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.general_message ALTER COLUMN id SET DEFAULT nextval('public.general_message_id_seq'::regclass);


--
-- Name: message id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.message ALTER COLUMN id SET DEFAULT nextval('public.message_id_seq'::regclass);


--
-- Name: private_message id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.private_message ALTER COLUMN id SET DEFAULT nextval('public.private_message_id_seq'::regclass);


--
-- Name: strategies id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.strategies ALTER COLUMN id SET DEFAULT nextval('public.strategies_id_seq'::regclass);


--
-- Name: tactics id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.tactics ALTER COLUMN id SET DEFAULT nextval('public.tactics_id_seq'::regclass);


--
-- Data for Name: general_message; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.general_message (id, username, content, "timestamp", message_id) FROM stdin;
1	kelvin123	aviso - kelvin123 entrou na sala geral.	2025-12-06 00:50:05.133227	2
2	kelvin123	aviso - kelvin123 entrou na sala geral.	2025-12-06 00:51:04.762456	2
3	kelvin123	aviso - kelvin123 entrou na sala geral.	2025-12-06 00:59:27.285803	2
\.


--
-- Data for Name: message; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.message (id) FROM stdin;
1
2
\.


--
-- Data for Name: private_message; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.private_message (id, sender_id, username, target_username, content, "timestamp", message_id) FROM stdin;
\.


--
-- Data for Name: strategies; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.strategies (id, name) FROM stdin;
1	estra 1
2	estra 2
\.


--
-- Data for Name: tactics; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.tactics (id, name, description, "time", chat_id, strategy_id) FROM stdin;
1	Reuso		22	\N	1
2	Debate Sincrono		22	1	1
3	Apresentacao Sincrona	https://meet.google.com/dxt-mbyg-gvs	22	\N	1
4	Envio de Informacao		22	\N	1
5	Debate Sincrono		33	2	2
6	Apresentacao Sincrona	https://meet.google.com/dxt-mbyg-gvs	33	\N	2
7	Envio de Informacao		33	\N	2
8	Reuso		33	\N	2
\.


--
-- Name: general_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.general_message_id_seq', 3, true);


--
-- Name: message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.message_id_seq', 2, true);


--
-- Name: private_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.private_message_id_seq', 1, false);


--
-- Name: strategies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.strategies_id_seq', 2, true);


--
-- Name: tactics_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.tactics_id_seq', 8, true);


--
-- Name: general_message general_message_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.general_message
    ADD CONSTRAINT general_message_pkey PRIMARY KEY (id);


--
-- Name: message message_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.message
    ADD CONSTRAINT message_pkey PRIMARY KEY (id);


--
-- Name: private_message private_message_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.private_message
    ADD CONSTRAINT private_message_pkey PRIMARY KEY (id);


--
-- Name: strategies strategies_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.strategies
    ADD CONSTRAINT strategies_pkey PRIMARY KEY (id);


--
-- Name: tactics tactics_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.tactics
    ADD CONSTRAINT tactics_pkey PRIMARY KEY (id);


--
-- Name: private_message fk_message_parent; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.private_message
    ADD CONSTRAINT fk_message_parent FOREIGN KEY (message_id) REFERENCES public.message(id) ON DELETE CASCADE;


--
-- Name: general_message fk_message_room; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.general_message
    ADD CONSTRAINT fk_message_room FOREIGN KEY (message_id) REFERENCES public.message(id) ON DELETE CASCADE;


--
-- Name: tactics fk_strategies; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.tactics
    ADD CONSTRAINT fk_strategies FOREIGN KEY (strategy_id) REFERENCES public.strategies(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict Vg5OFvt5eOsnNeWNlqbxWUwYhodkzbNt9z2YKUKgjKJ3VobCcFIj8BCYSitpwXa

