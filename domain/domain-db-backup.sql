--
-- PostgreSQL database dump
--

\restrict my1EIXwigBUR2eoiOxgqE0fay4FNbxzzj0XgxdMQanWmym7tBdZftb9fVCBhGf5

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
-- Name: domain; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.domain (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text
);


ALTER TABLE public.domain OWNER TO "user";

--
-- Name: domain_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.domain_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.domain_id_seq OWNER TO "user";

--
-- Name: domain_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.domain_id_seq OWNED BY public.domain.id;


--
-- Name: exercise; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.exercise (
    id integer NOT NULL,
    question text NOT NULL,
    options jsonb NOT NULL,
    correct character varying(10) NOT NULL,
    domain_id integer NOT NULL
);


ALTER TABLE public.exercise OWNER TO "user";

--
-- Name: exercise_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.exercise_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.exercise_id_seq OWNER TO "user";

--
-- Name: exercise_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.exercise_id_seq OWNED BY public.exercise.id;


--
-- Name: pdf; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.pdf (
    id integer NOT NULL,
    filename character varying(255) NOT NULL,
    path character varying(255) NOT NULL,
    domain_id integer NOT NULL
);


ALTER TABLE public.pdf OWNER TO "user";

--
-- Name: pdf_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.pdf_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pdf_id_seq OWNER TO "user";

--
-- Name: pdf_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.pdf_id_seq OWNED BY public.pdf.id;


--
-- Name: video_upload; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.video_upload (
    id integer NOT NULL,
    filename character varying(255) NOT NULL,
    path character varying(255) NOT NULL,
    domain_id integer NOT NULL
);


ALTER TABLE public.video_upload OWNER TO "user";

--
-- Name: video_upload_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.video_upload_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.video_upload_id_seq OWNER TO "user";

--
-- Name: video_upload_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.video_upload_id_seq OWNED BY public.video_upload.id;


--
-- Name: video_youtube; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.video_youtube (
    id integer NOT NULL,
    url character varying(500) NOT NULL,
    domain_id integer NOT NULL
);


ALTER TABLE public.video_youtube OWNER TO "user";

--
-- Name: video_youtube_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.video_youtube_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.video_youtube_id_seq OWNER TO "user";

--
-- Name: video_youtube_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.video_youtube_id_seq OWNED BY public.video_youtube.id;


--
-- Name: domain id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.domain ALTER COLUMN id SET DEFAULT nextval('public.domain_id_seq'::regclass);


--
-- Name: exercise id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.exercise ALTER COLUMN id SET DEFAULT nextval('public.exercise_id_seq'::regclass);


--
-- Name: pdf id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pdf ALTER COLUMN id SET DEFAULT nextval('public.pdf_id_seq'::regclass);


--
-- Name: video_upload id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.video_upload ALTER COLUMN id SET DEFAULT nextval('public.video_upload_id_seq'::regclass);


--
-- Name: video_youtube id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.video_youtube ALTER COLUMN id SET DEFAULT nextval('public.video_youtube_id_seq'::regclass);


--
-- Data for Name: domain; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.domain (id, name, description) FROM stdin;
3	Fremeworks	Como aprender um framework?\r\nPor isso, vamos abordar neste artigo alguns pontos sobre quando é o momento ideal para se aventurar nos frameworks.\r\n\r\n    Construa primeiro uma base sólida na linguagem. ...\r\n    Tente resolver problemas sem utilizar frameworks. ...\r\n    Identifique a necessidade. ...\r\n    Não se esqueça do equilíbrio
4	C++	C++ é uma linguagem de programação poderosa, de propósito geral e de alto desempenho, criada como uma extensão da linguagem C, oferecendo controle de baixo nível sobre o hardware e suporte multi-paradigma (orientada a objetos, genérica, imperativa).
\.


--
-- Data for Name: exercise; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.exercise (id, question, options, correct, domain_id) FROM stdin;
3	Em frameworks front-end modernos (como React, Vue ou Angular), o conceito de "reatividade" é central. Qual das alternativas abaixo descreve corretamente o comportamento de um framework reativo ao detectar uma mudança no estado (state) de um componente?	["O framework exige que o desenvolvedor manipule manualmente o DOM para inserir os novos dados.", "A página inteira é recarregada pelo navegador para buscar a nova versão do HTML no servidor.", "O framework identifica a mudança e atualiza automaticamente apenas as partes da interface que dependem daquele dado específico.", "O estado é armazenado apenas em variáveis globais do navegador (window), sem relação direta com a interface.", " A atualização da interface ocorre apenas se o usuário clicar em um botão de \\"refresh\\" implementado no framework."]	2	3
4	Ao utilizar frameworks de back-end como Spring Boot (Java) ou NestJS (Node.js) para criar APIs REST, o desenvolvedor frequentemente utiliza "Decorators" ou "Annotations" (ex: @GetMapping, @Post). Qual é a principal função desse recurso?	["Definir o estilo CSS que será aplicado aos dados retornados pela API.", "Mapear automaticamente uma função do código a uma rota HTTP e um método específico (ex: GET ou POST).", "Criptografar o código-fonte para que outros desenvolvedores não consigam lê-lo.", "Substituir a necessidade de um banco de dados, armazenando os dados diretamente nas anotações.", "Aumentar a velocidade de download do framework durante a instalação."]	1	3
5	Frameworks de estilização como o Tailwind CSS ganharam muita popularidade em 2024 e 2025. Qual é a característica principal da abordagem "Utility-First" proposta por esse tipo de ferramenta?	["Escrever todo o código CSS em arquivos separados e importá-los via link HTML tradicional.", "Criar componentes visuais usando apenas tags XML personalizadas sem classes.", "Utilizar classes pré-definidas diretamente no HTML (ex: flex, pt-4, text-center) para construir o design sem sair do arquivo de marcação.", "Gerar automaticamente um design diferente para cada usuário baseado em inteligência artificial.", "Impedir que o desenvolvedor utilize propriedades como margin ou padding para evitar erros de layout."]	2	3
6	Qual será a saída do seguinte trecho de código em C++?	["2.5", "2.0", "2", "3", "Erro de compilação"]	2	4
7	No contexto de Programação Orientada a Objetos em C++, o que define uma classe abstrata?	["Uma classe que possui apenas métodos privados.", "Uma classe que não pode ter atributos, apenas métodos.", "Uma classe que possui pelo menos um método virtual puro (declarado com = 0).", "Uma classe que é declarada dentro do escopo de outra classe.", "Uma classe que herdou características de mais de duas classes base."]	2	4
8	Considere o uso de Smart Pointers (Ponteiros Inteligentes) introduzidos a partir do C++11. Qual das alternativas descreve corretamente o comportamento do std::unique_ptr?	["Permite que múltiplos ponteiros compartilhem a propriedade do mesmo objeto através de contagem de referência.", "Deve ser liberado manualmente usando o comando delete para evitar vazamento de memória.", "É um ponteiro que não pode ser movido (move), apenas copiado para outras funções.", "Mantém a posse exclusiva de um objeto e desaloca a memória automaticamente quando o ponteiro sai de escopo.", " É utilizado exclusivamente para apontar para endereços de memória de tipos primitivos (int, char, bool)."]	3	4
\.


--
-- Data for Name: pdf; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.pdf (id, filename, path, domain_id) FROM stdin;
4	Paper-2024-AgentDesignPatternCatalogue.pdf	/app/app/uploads/Paper-2024-AgentDesignPatternCatalogue.pdf	3
5	Paper-Agents-2024-Ignise.pdf	/app/app/uploads/Paper-Agents-2024-Ignise.pdf	3
6	Le_Prototype_BIRDS.pdf	/app/app/uploads/Le_Prototype_BIRDS.pdf	4
7	Relatorio_Reuso-comLinkVideo.pdf	/app/app/uploads/Relatorio_Reuso-comLinkVideo.pdf	4
\.


--
-- Data for Name: video_upload; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.video_upload (id, filename, path, domain_id) FROM stdin;
2	2025-12-19_09-57-13.mp4	/app/app/uploads/2025-12-19_09-57-13.mp4	3
3	2025-12-19_10-13-32.mp4	/app/app/uploads/2025-12-19_10-13-32.mp4	4
\.


--
-- Data for Name: video_youtube; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.video_youtube (id, url, domain_id) FROM stdin;
3	https://www.youtube.com/watch?v=BQ35b4b8qi4&t=616s	3
4	https://www.youtube.com/watch?v=MQUP3ML8Sjs	3
5	https://www.youtube.com/watch?v=35dJZOY6Sdo	4
6	https://www.youtube.com/watch?v=OYdi6TFfPNA	4
\.


--
-- Name: domain_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.domain_id_seq', 4, true);


--
-- Name: exercise_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.exercise_id_seq', 8, true);


--
-- Name: pdf_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.pdf_id_seq', 7, true);


--
-- Name: video_upload_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.video_upload_id_seq', 3, true);


--
-- Name: video_youtube_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.video_youtube_id_seq', 6, true);


--
-- Name: domain domain_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.domain
    ADD CONSTRAINT domain_pkey PRIMARY KEY (id);


--
-- Name: exercise exercise_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.exercise
    ADD CONSTRAINT exercise_pkey PRIMARY KEY (id);


--
-- Name: pdf pdf_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pdf
    ADD CONSTRAINT pdf_pkey PRIMARY KEY (id);


--
-- Name: video_upload video_upload_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.video_upload
    ADD CONSTRAINT video_upload_pkey PRIMARY KEY (id);


--
-- Name: video_youtube video_youtube_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.video_youtube
    ADD CONSTRAINT video_youtube_pkey PRIMARY KEY (id);


--
-- Name: exercise fk_domain_exercise; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.exercise
    ADD CONSTRAINT fk_domain_exercise FOREIGN KEY (domain_id) REFERENCES public.domain(id) ON DELETE CASCADE;


--
-- Name: pdf fk_domain_pdf; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pdf
    ADD CONSTRAINT fk_domain_pdf FOREIGN KEY (domain_id) REFERENCES public.domain(id) ON DELETE CASCADE;


--
-- Name: video_upload fk_domain_video_upload; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.video_upload
    ADD CONSTRAINT fk_domain_video_upload FOREIGN KEY (domain_id) REFERENCES public.domain(id) ON DELETE CASCADE;


--
-- Name: video_youtube fk_domain_video_youtube; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.video_youtube
    ADD CONSTRAINT fk_domain_video_youtube FOREIGN KEY (domain_id) REFERENCES public.domain(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict my1EIXwigBUR2eoiOxgqE0fay4FNbxzzj0XgxdMQanWmym7tBdZftb9fVCBhGf5

