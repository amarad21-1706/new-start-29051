--
-- PostgreSQL database dump
--

-- Dumped from database version 14.12 (Homebrew)
-- Dumped by pg_dump version 14.12 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: lifespan_types; Type: TYPE; Schema: public; Owner: aradulescu
--

CREATE TYPE public.lifespan_types AS ENUM (
    'one-off',
    'persistent'
);


ALTER TYPE public.lifespan_types OWNER TO audit_postgres_30051_user;

--
-- Name: message_types; Type: TYPE; Schema: public; Owner: aradulescu
--

CREATE TYPE public.message_types AS ENUM (
    'noticeboard',
    'email',
    'service_message'
);


ALTER TYPE public.message_types OWNER TO audit_postgres_30051_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO audit_postgres_30051_user;

--
-- Name: answer; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.answer (
    id bigint NOT NULL,
    company_id integer,
    user_id integer,
    questionnaire_id integer,
    question_id integer,
    "timestamp" timestamp with time zone,
    submitted boolean,
    answer_data json DEFAULT 'null'::json
);


ALTER TABLE public.answer OWNER TO audit_postgres_30051_user;

--
-- Name: answer_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.answer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.answer_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: answer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.answer_id_seq OWNED BY public.answer.id;


--
-- Name: area; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.area (
    id integer NOT NULL,
    name character varying(64),
    description character varying(255)
);


ALTER TABLE public.area OWNER TO audit_postgres_30051_user;

--
-- Name: area_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.area_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.area_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: area_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.area_id_seq OWNED BY public.area.id;


--
-- Name: area_subareas; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.area_subareas (
    id integer NOT NULL,
    area_id integer,
    subarea_id integer,
    status_id integer,
    interval_id integer,
    caption character varying(255)
);


ALTER TABLE public.area_subareas OWNER TO audit_postgres_30051_user;

--
-- Name: area_subareas_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.area_subareas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.area_subareas_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: area_subareas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.area_subareas_id_seq OWNED BY public.area_subareas.id;


--
-- Name: audit_log; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.audit_log (
    id bigint NOT NULL,
    "timestamp" character varying(32),
    company_id integer,
    user_id integer,
    base_data_id integer,
    workflow_id integer,
    step_id integer,
    action character varying(255),
    details text
);


ALTER TABLE public.audit_log OWNER TO audit_postgres_30051_user;

--
-- Name: audit_log_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.audit_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.audit_log_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: audit_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.audit_log_id_seq OWNED BY public.audit_log.id;


--
-- Name: base_data; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.base_data (
    id bigint NOT NULL,
    user_id integer,
    company_id integer,
    interval_id integer,
    interval_ord integer,
    status_id integer,
    record_type character varying(64),
    subject_id integer,
    legal_document_id integer,
    data_type character varying(128),
    area_id integer,
    subarea_id integer,
    lexic_id integer,
    created_on timestamp with time zone,
    updated_on timestamp with time zone,
    deadline date,
    created_by character varying(128),
    number_of_doc character varying(255),
    date_of_doc date,
    ft1 character varying(255),
    fb1 text,
    fc1 text,
    fc2 text,
    fc3 text,
    fc4 character varying(255),
    fc5 character varying(255),
    fc6 character varying(255),
    fi0 bigint,
    fi1 bigint,
    fi2 bigint,
    fi3 bigint,
    fi4 bigint,
    fi5 bigint,
    fi6 bigint,
    fi7 bigint,
    fi8 bigint,
    fi9 bigint,
    fi10 bigint,
    fi11 bigint,
    fi12 bigint,
    fi13 bigint,
    fi14 bigint,
    fi15 bigint,
    fi16 bigint,
    fn0 numeric,
    fn1 numeric,
    fn2 numeric,
    fn3 numeric,
    fn4 numeric,
    fn5 numeric,
    fn6 numeric,
    fn7 numeric,
    fn8 numeric,
    fn9 numeric,
    file_path text,
    no_action integer
);


ALTER TABLE public.base_data OWNER TO audit_postgres_30051_user;

--
-- Name: base_data_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.base_data_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.base_data_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: base_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.base_data_id_seq OWNED BY public.base_data.id;


--
-- Name: basedata_flussi; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.basedata_flussi (
    id bigint NOT NULL,
    lexic_id integer,
    fn1 numeric,
    fn2 numeric,
    fn3 numeric,
    fc1 character varying(128)
);


ALTER TABLE public.basedata_flussi OWNER TO audit_postgres_30051_user;

--
-- Name: basedata_flussi_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.basedata_flussi_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.basedata_flussi_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: basedata_flussi_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.basedata_flussi_id_seq OWNED BY public.basedata_flussi.id;


--
-- Name: basedata_partial; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.basedata_partial (
    id bigint NOT NULL,
    lexic_id integer,
    fn1 numeric,
    fn2 numeric,
    fn3 numeric,
    fc1 character varying(128)
);


ALTER TABLE public.basedata_partial OWNER TO audit_postgres_30051_user;

--
-- Name: basedata_partial_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.basedata_partial_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.basedata_partial_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: basedata_partial_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.basedata_partial_id_seq OWNED BY public.basedata_partial.id;


--
-- Name: central_data; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.central_data (
    id bigint NOT NULL,
    reference_date timestamp with time zone,
    interval_id integer,
    status_id integer,
    user_id integer,
    type_id character varying(255),
    topic_id character varying(255),
    topic1_id character varying(255),
    topic2_id character varying(255),
    topic3_id character varying(255),
    dimension1_id integer,
    dimension2_id integer,
    dimension3_id integer,
    dimension4_id integer,
    dimension5_id integer,
    dimension6_id integer,
    dimension7_id integer,
    extended_data json,
    created_on timestamp with time zone,
    created_by text
);


ALTER TABLE public.central_data OWNER TO audit_postgres_30051_user;

--
-- Name: central_data_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.central_data_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.central_data_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: central_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.central_data_id_seq OWNED BY public.central_data.id;


--
-- Name: company; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.company (
    id integer NOT NULL,
    name character varying(100),
    description character varying(255),
    address character varying(255),
    phone_number character varying(20),
    email character varying(100),
    website character varying(100),
    tax_code character varying(24),
    created_on character varying(255),
    updated_on character varying(255),
    end_of_registration character varying(255)
);


ALTER TABLE public.company OWNER TO audit_postgres_30051_user;

--
-- Name: company_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.company_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.company_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: company_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.company_id_seq OWNED BY public.company.id;


--
-- Name: company_users; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.company_users (
    id integer NOT NULL,
    company_id integer NOT NULL,
    user_id integer,
    created_on character varying(255),
    updated_on character varying(255),
    end_of_registration text
);


ALTER TABLE public.company_users OWNER TO audit_postgres_30051_user;

--
-- Name: company_users_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.company_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.company_users_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: company_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.company_users_id_seq OWNED BY public.company_users.id;


--
-- Name: config; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.config (
    id integer NOT NULL,
    config_type character varying(64),
    company_id integer,
    area_id integer,
    subarea_id integer,
    config_integer integer,
    config_number numeric,
    config_text character varying(255),
    config_date date
);


ALTER TABLE public.config OWNER TO audit_postgres_30051_user;

--
-- Name: config_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.config_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.config_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.config_id_seq OWNED BY public.config.id;


--
-- Name: deadline; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.deadline (
    id integer NOT NULL,
    company_id integer,
    area_id integer,
    subarea_id integer,
    interval_id integer,
    status_id integer,
    status_start character varying(255),
    status_end text
);


ALTER TABLE public.deadline OWNER TO audit_postgres_30051_user;

--
-- Name: deadline_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.deadline_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.deadline_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: deadline_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.deadline_id_seq OWNED BY public.deadline.id;


--
-- Name: employee; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.employee (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    "position" character varying(100),
    company_id integer NOT NULL
);


ALTER TABLE public.employee OWNER TO audit_postgres_30051_user;

--
-- Name: employee_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.employee_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.employee_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: employee_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.employee_id_seq OWNED BY public.employee.id;


--
-- Name: inline_fields; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.inline_fields (
    id bigint NOT NULL,
    question_id integer,
    answer_text character varying(255),
    answer_score integer,
    answer_file character varying(255),
    comment_text character varying(255)
);


ALTER TABLE public.inline_fields OWNER TO audit_postgres_30051_user;

--
-- Name: inline_fields_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.inline_fields_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.inline_fields_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: inline_fields_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.inline_fields_id_seq OWNED BY public.inline_fields.id;


--
-- Name: interval; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public."interval" (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description character varying(255),
    interval_id integer
);


ALTER TABLE public."interval" OWNER TO audit_postgres_30051_user;

--
-- Name: interval_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.interval_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.interval_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: interval_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.interval_id_seq OWNED BY public."interval".id;


--
-- Name: legal_document; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.legal_document (
    id integer NOT NULL,
    name character varying(255),
    tier_1 character varying(255),
    tier_2 character varying(255),
    tier_3 text
);


ALTER TABLE public.legal_document OWNER TO audit_postgres_30051_user;

--
-- Name: legal_document_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.legal_document_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.legal_document_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: legal_document_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.legal_document_id_seq OWNED BY public.legal_document.id;


--
-- Name: lexic; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.lexic (
    id integer NOT NULL,
    category character varying(64),
    name character varying(64)
);


ALTER TABLE public.lexic OWNER TO audit_postgres_30051_user;

--
-- Name: lexic_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.lexic_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lexic_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: lexic_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.lexic_id_seq OWNED BY public.lexic.id;


--
-- Name: possible_answers; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.possible_answers (
    id bigint NOT NULL,
    question_id character varying(64),
    text text,
    next_question_id integer
);


ALTER TABLE public.possible_answers OWNER TO audit_postgres_30051_user;

--
-- Name: possible_answers_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.possible_answers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.possible_answers_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: possible_answers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.possible_answers_id_seq OWNED BY public.possible_answers.id;


--
-- Name: post; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.post (
    id bigint NOT NULL,
    company_id integer,
    user_id integer,
    sender character varying(255),
    message_type character varying(15),
    subject character varying(255),
    body character varying,
    created_at timestamp with time zone,
    marked_as_read boolean,
    lifespan character varying(10)
);


ALTER TABLE public.post OWNER TO audit_postgres_30051_user;

--
-- Name: post_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.post_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.post_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: post_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.post_id_seq OWNED BY public.post.id;


--
-- Name: question; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.question (
    id bigint NOT NULL,
    question_id character varying(64),
    text text,
    answer_type character varying(64),
    answer_width character varying(255),
    answer_fields json DEFAULT 'null'::json
);


ALTER TABLE public.question OWNER TO audit_postgres_30051_user;

--
-- Name: question_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.question_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.question_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: question_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.question_id_seq OWNED BY public.question.id;


--
-- Name: questionnaire; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.questionnaire (
    id bigint NOT NULL,
    questionnaire_id character varying(255),
    questionnaire_type character varying(24) DEFAULT 'Questionnaire'::character varying,
    name text,
    "interval" character varying(12),
    deadline_date timestamp with time zone,
    status_id integer,
    created_on timestamp with time zone,
    updated_on timestamp with time zone,
    headers json DEFAULT 'null'::json
);


ALTER TABLE public.questionnaire OWNER TO audit_postgres_30051_user;

--
-- Name: questionnaire_companies; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.questionnaire_companies (
    id bigint NOT NULL,
    questionnaire_id integer,
    company_id integer,
    status_id integer
);


ALTER TABLE public.questionnaire_companies OWNER TO audit_postgres_30051_user;

--
-- Name: questionnaire_companies_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.questionnaire_companies_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.questionnaire_companies_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: questionnaire_companies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.questionnaire_companies_id_seq OWNED BY public.questionnaire_companies.id;


--
-- Name: questionnaire_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.questionnaire_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.questionnaire_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: questionnaire_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.questionnaire_id_seq OWNED BY public.questionnaire.id;


--
-- Name: questionnaire_questions; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.questionnaire_questions (
    id bigint NOT NULL,
    questionnaire_id integer,
    question_id integer,
    extra_data character varying(600)
);


ALTER TABLE public.questionnaire_questions OWNER TO audit_postgres_30051_user;

--
-- Name: questionnaire_questions_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.questionnaire_questions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.questionnaire_questions_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: questionnaire_questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.questionnaire_questions_id_seq OWNED BY public.questionnaire_questions.id;


--
-- Name: role; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.role (
    id integer NOT NULL,
    role_id integer,
    name character varying(255) NOT NULL,
    description text
);


ALTER TABLE public.role OWNER TO audit_postgres_30051_user;

--
-- Name: role_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.role_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.role_id_seq OWNED BY public.role.id;


--
-- Name: status; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.status (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description character varying(255)
);


ALTER TABLE public.status OWNER TO audit_postgres_30051_user;

--
-- Name: status_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.status_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.status_id_seq OWNED BY public.status.id;


--
-- Name: step; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.step (
    id integer NOT NULL,
    name character varying(50),
    description character varying(255),
    action character varying(50),
    "order" integer,
    next_step_id integer,
    deadline_date date,
    reminder_date date
);


ALTER TABLE public.step OWNER TO audit_postgres_30051_user;

--
-- Name: step_base_data; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.step_base_data (
    id integer NOT NULL,
    base_data_id bigint,
    workflow_id integer,
    step_id integer,
    status_id integer,
    start_date date,
    deadline_date date,
    auto_move integer,
    end_date date,
    hidden_data character varying(255),
    start_recall integer,
    deadline_recall integer,
    end_recall integer,
    recall_unit character varying(24),
    open_action integer
);


ALTER TABLE public.step_base_data OWNER TO audit_postgres_30051_user;

--
-- Name: step_base_data_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.step_base_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.step_base_data_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: step_base_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.step_base_data_id_seq OWNED BY public.step_base_data.id;


--
-- Name: step_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.step_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.step_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: step_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.step_id_seq OWNED BY public.step.id;


--
-- Name: step_questionnaire; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.step_questionnaire (
    id bigint NOT NULL,
    questionnaire_id integer,
    workflow_id integer,
    step_id integer,
    status_id integer,
    start_date date,
    deadline_date date,
    auto_move integer,
    end_date date,
    hidden_data character varying(255),
    start_recall integer,
    deadline_recall integer,
    end_recall integer,
    recall_unit character varying(24),
    open_action smallint DEFAULT 1
);


ALTER TABLE public.step_questionnaire OWNER TO audit_postgres_30051_user;

--
-- Name: step_questionnaire_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.step_questionnaire_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.step_questionnaire_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: step_questionnaire_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.step_questionnaire_id_seq OWNED BY public.step_questionnaire.id;


--
-- Name: subarea; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.subarea (
    id integer NOT NULL,
    name character varying(64),
    description character varying(255),
    data_type character varying(64)
);


ALTER TABLE public.subarea OWNER TO audit_postgres_30051_user;

--
-- Name: subarea_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.subarea_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.subarea_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: subarea_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.subarea_id_seq OWNED BY public.subarea.id;


--
-- Name: subject; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.subject (
    id bigint NOT NULL,
    name character varying(255),
    tier_1 character varying(255),
    tier_2 character varying(255),
    tier_3 character varying(255)
);


ALTER TABLE public.subject OWNER TO audit_postgres_30051_user;

--
-- Name: subject_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.subject_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.subject_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: subject_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.subject_id_seq OWNED BY public.subject.id;


--
-- Name: table; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public."table" (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description character varying,
    user_id integer NOT NULL,
    subject_id integer,
    column1 character varying(100),
    column2 character varying(100),
    created_on timestamp without time zone
);


ALTER TABLE public."table" OWNER TO audit_postgres_30051_user;

--
-- Name: table_base; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.table_base (
    id bigint NOT NULL,
    name character varying(255) NOT NULL,
    description character varying(255),
    subject_id integer,
    company_id integer,
    user_id integer,
    column1 character varying(255),
    column2 character varying(255),
    created_on character varying(255)
);


ALTER TABLE public.table_base OWNER TO audit_postgres_30051_user;

--
-- Name: table_base_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.table_base_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.table_base_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: table_base_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.table_base_id_seq OWNED BY public.table_base.id;


--
-- Name: table_gen; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.table_gen (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    description character varying,
    user_id integer NOT NULL,
    subject_id integer,
    column1 character varying(100),
    column2 character varying(100),
    created_on timestamp with time zone
);


ALTER TABLE public.table_gen OWNER TO audit_postgres_30051_user;

--
-- Name: table_gen_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.table_gen_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.table_gen_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: table_gen_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.table_gen_id_seq OWNED BY public.table_gen.id;


--
-- Name: table_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.table_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.table_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: table_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.table_id_seq OWNED BY public."table".id;


--
-- Name: task; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.task (
    id bigint NOT NULL,
    name character varying(128) NOT NULL,
    status character varying(50),
    workflow_id integer NOT NULL
);


ALTER TABLE public.task OWNER TO audit_postgres_30051_user;

--
-- Name: task_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.task_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.task_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: task_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.task_id_seq OWNED BY public.task.id;


--
-- Name: test_table; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.test_table (
    id integer NOT NULL,
    name character varying(50)
);


ALTER TABLE public.test_table OWNER TO audit_postgres_30051_user;

--
-- Name: test_table_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.test_table_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.test_table_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: test_table_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.test_table_id_seq OWNED BY public.test_table.id;


--
-- Name: ticket; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.ticket (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    subject_id integer NOT NULL,
    subject character varying(128) NOT NULL,
    description text NOT NULL,
    status_id integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    marked_as_read boolean,
    lifespan character varying(10)
);


ALTER TABLE public.ticket OWNER TO audit_postgres_30051_user;

--
-- Name: ticket_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.ticket_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ticket_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: ticket_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.ticket_id_seq OWNED BY public.ticket.id;


--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.user_roles (
    id integer NOT NULL,
    user_id integer,
    role_id integer,
    created_on character varying(255),
    updated_on character varying(255),
    end_of_registration text
);


ALTER TABLE public.user_roles OWNER TO audit_postgres_30051_user;

--
-- Name: user_roles_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.user_roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_roles_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: user_roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.user_roles_id_seq OWNED BY public.user_roles.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(255) NOT NULL,
    user_2fa_secret character varying(255),
    title character varying(32),
    first_name character varying(128),
    mid_name character varying(128),
    last_name character varying(128),
    company character varying(128),
    company_id integer,
    address character varying(128),
    address1 character varying(128),
    city character varying(128),
    province character varying(64),
    region character varying(64),
    zip_code character varying(24),
    country character varying(64),
    tax_code character varying(128),
    mobile_phone character varying(32),
    work_phone character varying(32),
    created_on timestamp with time zone,
    updated_on timestamp with time zone,
    end_of_registration date
);


ALTER TABLE public.users OWNER TO audit_postgres_30051_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: workflow; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.workflow (
    id integer NOT NULL,
    name character varying(50),
    description character varying(255),
    status character varying(128),
    restricted integer,
    deadline_date timestamp with time zone,
    reminder_date timestamp with time zone
);


ALTER TABLE public.workflow OWNER TO audit_postgres_30051_user;

--
-- Name: workflow_base_data; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.workflow_base_data (
    id bigint NOT NULL,
    workflow_id integer,
    base_data_id integer,
    created_on character varying(255),
    updated_on character varying(255),
    end_of_registration text
);


ALTER TABLE public.workflow_base_data OWNER TO audit_postgres_30051_user;

--
-- Name: workflow_base_data_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.workflow_base_data_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workflow_base_data_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: workflow_base_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.workflow_base_data_id_seq OWNED BY public.workflow_base_data.id;


--
-- Name: workflow_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.workflow_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workflow_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: workflow_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.workflow_id_seq OWNED BY public.workflow.id;


--
-- Name: workflow_steps; Type: TABLE; Schema: public; Owner: aradulescu
--

CREATE TABLE public.workflow_steps (
    id integer NOT NULL,
    workflow_id integer,
    step_id integer
);


ALTER TABLE public.workflow_steps OWNER TO audit_postgres_30051_user;

--
-- Name: workflow_steps_id_seq; Type: SEQUENCE; Schema: public; Owner: aradulescu
--

CREATE SEQUENCE public.workflow_steps_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workflow_steps_id_seq OWNER TO audit_postgres_30051_user;

--
-- Name: workflow_steps_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aradulescu
--

ALTER SEQUENCE public.workflow_steps_id_seq OWNED BY public.workflow_steps.id;


--
-- Name: answer id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.answer ALTER COLUMN id SET DEFAULT nextval('public.answer_id_seq'::regclass);


--
-- Name: area id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.area ALTER COLUMN id SET DEFAULT nextval('public.area_id_seq'::regclass);


--
-- Name: area_subareas id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.area_subareas ALTER COLUMN id SET DEFAULT nextval('public.area_subareas_id_seq'::regclass);


--
-- Name: audit_log id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.audit_log ALTER COLUMN id SET DEFAULT nextval('public.audit_log_id_seq'::regclass);


--
-- Name: base_data id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.base_data ALTER COLUMN id SET DEFAULT nextval('public.base_data_id_seq'::regclass);


--
-- Name: basedata_flussi id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.basedata_flussi ALTER COLUMN id SET DEFAULT nextval('public.basedata_flussi_id_seq'::regclass);


--
-- Name: basedata_partial id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.basedata_partial ALTER COLUMN id SET DEFAULT nextval('public.basedata_partial_id_seq'::regclass);


--
-- Name: central_data id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.central_data ALTER COLUMN id SET DEFAULT nextval('public.central_data_id_seq'::regclass);


--
-- Name: company id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.company ALTER COLUMN id SET DEFAULT nextval('public.company_id_seq'::regclass);


--
-- Name: company_users id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.company_users ALTER COLUMN id SET DEFAULT nextval('public.company_users_id_seq'::regclass);


--
-- Name: config id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.config ALTER COLUMN id SET DEFAULT nextval('public.config_id_seq'::regclass);


--
-- Name: deadline id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.deadline ALTER COLUMN id SET DEFAULT nextval('public.deadline_id_seq'::regclass);


--
-- Name: employee id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.employee ALTER COLUMN id SET DEFAULT nextval('public.employee_id_seq'::regclass);


--
-- Name: inline_fields id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.inline_fields ALTER COLUMN id SET DEFAULT nextval('public.inline_fields_id_seq'::regclass);


--
-- Name: interval id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public."interval" ALTER COLUMN id SET DEFAULT nextval('public.interval_id_seq'::regclass);


--
-- Name: legal_document id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.legal_document ALTER COLUMN id SET DEFAULT nextval('public.legal_document_id_seq'::regclass);


--
-- Name: lexic id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.lexic ALTER COLUMN id SET DEFAULT nextval('public.lexic_id_seq'::regclass);


--
-- Name: possible_answers id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.possible_answers ALTER COLUMN id SET DEFAULT nextval('public.possible_answers_id_seq'::regclass);


--
-- Name: post id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.post ALTER COLUMN id SET DEFAULT nextval('public.post_id_seq'::regclass);


--
-- Name: question id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.question ALTER COLUMN id SET DEFAULT nextval('public.question_id_seq'::regclass);


--
-- Name: questionnaire id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.questionnaire ALTER COLUMN id SET DEFAULT nextval('public.questionnaire_id_seq'::regclass);


--
-- Name: questionnaire_companies id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.questionnaire_companies ALTER COLUMN id SET DEFAULT nextval('public.questionnaire_companies_id_seq'::regclass);


--
-- Name: questionnaire_questions id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.questionnaire_questions ALTER COLUMN id SET DEFAULT nextval('public.questionnaire_questions_id_seq'::regclass);


--
-- Name: role id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.role ALTER COLUMN id SET DEFAULT nextval('public.role_id_seq'::regclass);


--
-- Name: status id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.status ALTER COLUMN id SET DEFAULT nextval('public.status_id_seq'::regclass);


--
-- Name: step id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.step ALTER COLUMN id SET DEFAULT nextval('public.step_id_seq'::regclass);


--
-- Name: step_base_data id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.step_base_data ALTER COLUMN id SET DEFAULT nextval('public.step_base_data_id_seq'::regclass);


--
-- Name: step_questionnaire id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.step_questionnaire ALTER COLUMN id SET DEFAULT nextval('public.step_questionnaire_id_seq'::regclass);


--
-- Name: subarea id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.subarea ALTER COLUMN id SET DEFAULT nextval('public.subarea_id_seq'::regclass);


--
-- Name: subject id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.subject ALTER COLUMN id SET DEFAULT nextval('public.subject_id_seq'::regclass);


--
-- Name: table id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public."table" ALTER COLUMN id SET DEFAULT nextval('public.table_id_seq'::regclass);


--
-- Name: table_base id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.table_base ALTER COLUMN id SET DEFAULT nextval('public.table_base_id_seq'::regclass);


--
-- Name: table_gen id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.table_gen ALTER COLUMN id SET DEFAULT nextval('public.table_gen_id_seq'::regclass);


--
-- Name: task id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.task ALTER COLUMN id SET DEFAULT nextval('public.task_id_seq'::regclass);


--
-- Name: test_table id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.test_table ALTER COLUMN id SET DEFAULT nextval('public.test_table_id_seq'::regclass);


--
-- Name: ticket id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.ticket ALTER COLUMN id SET DEFAULT nextval('public.ticket_id_seq'::regclass);


--
-- Name: user_roles id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.user_roles ALTER COLUMN id SET DEFAULT nextval('public.user_roles_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: workflow id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.workflow ALTER COLUMN id SET DEFAULT nextval('public.workflow_id_seq'::regclass);


--
-- Name: workflow_base_data id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.workflow_base_data ALTER COLUMN id SET DEFAULT nextval('public.workflow_base_data_id_seq'::regclass);


--
-- Name: workflow_steps id; Type: DEFAULT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.workflow_steps ALTER COLUMN id SET DEFAULT nextval('public.workflow_steps_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.alembic_version (version_num) FROM stdin;
\.


--
-- Data for Name: answer; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.answer (id, company_id, user_id, questionnaire_id, question_id, "timestamp", submitted, answer_data) FROM stdin;
1	0	1	1	45	2024-05-23 09:36:17.398928+02	f	"[{\\"type\\": \\"BYN\\", \\"value\\": \\"Yes\\", \\"width\\": \\"\\"}]"
2	0	1	1	47	2024-05-23 09:36:17.398928+02	f	"[{\\"type\\": \\"BYN\\", \\"value\\": \\"No\\", \\"width\\": \\"\\"}]"
3	0	1	1	48	2024-05-23 09:36:17.398928+02	f	"[{\\"type\\": \\"BYN\\", \\"value\\": \\"Yes\\", \\"width\\": \\"\\"}]"
4	0	1	1	49	2024-05-23 09:36:17.398928+02	f	"[{\\"type\\": \\"BYN\\", \\"value\\": \\"No\\", \\"width\\": \\"\\"}]"
5	0	1	1	50	2024-05-23 09:36:17.398928+02	f	"[{\\"type\\": \\"FILE\\", \\"value\\": \\"LeicaM11_IT.pdf\\", \\"width\\": \\"\\"}]"
6	0	1	1	51	2024-05-23 09:36:17.398928+02	f	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"adsfadfgw\\", \\"width\\": \\"\\"}]"
7	0	1	1	52	2024-05-23 09:36:17.398928+02	f	"[{\\"type\\": \\"DD\\", \\"value\\": \\"2024-06-30\\", \\"width\\": \\"\\"}]"
8	0	1	6	1	2024-05-24 00:03:57.15581+02	f	"[{\\"type\\": \\"CB\\", \\"value\\": \\"\\", \\"width\\": \\"\\"}, {\\"type\\": \\"CB\\", \\"value\\": \\"on\\", \\"width\\": \\"\\"}, {\\"type\\": \\"CB\\", \\"value\\": \\"\\", \\"width\\": \\"\\"}, {\\"type\\": \\"TST\\", \\"value\\": \\"sdfsdf\\", \\"width\\": \\"\\"}, {\\"type\\": \\"NUM\\", \\"value\\": \\"0.03\\", \\"width\\": \\"\\"}, {\\"type\\": \\"HML\\", \\"value\\": \\"M\\", \\"width\\": \\"\\"}, {\\"type\\": \\"TLT\\", \\"value\\": \\"g1\\", \\"width\\": \\"\\"}, {\\"type\\": \\"TLT\\", \\"value\\": \\"a1\\", \\"width\\": \\"\\"}, {\\"type\\": \\"TLT\\", \\"value\\": \\"s1\\", \\"width\\": \\"\\"}]"
9	0	1	6	2	2024-05-24 00:03:57.15581+02	f	"[{\\"type\\": \\"CB\\", \\"value\\": \\"on\\", \\"width\\": \\"\\"}, {\\"type\\": \\"CB\\", \\"value\\": \\"\\", \\"width\\": \\"\\"}, {\\"type\\": \\"CB\\", \\"value\\": \\"on\\", \\"width\\": \\"\\"}, {\\"type\\": \\"TST\\", \\"value\\": \\"sdfsd\\", \\"width\\": \\"\\"}, {\\"type\\": \\"NUM\\", \\"value\\": \\"0.04\\", \\"width\\": \\"\\"}, {\\"type\\": \\"HML\\", \\"value\\": \\"L\\", \\"width\\": \\"\\"}, {\\"type\\": \\"TLT\\", \\"value\\": \\"g2\\", \\"width\\": \\"\\"}, {\\"type\\": \\"TLT\\", \\"value\\": \\"a2\\", \\"width\\": \\"\\"}, {\\"type\\": \\"TLT\\", \\"value\\": \\"s2\\", \\"width\\": \\"\\"}]"
\.


--
-- Data for Name: area; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.area (id, name, description) FROM stdin;
1	Area di controllo 1	Area di controllo 1
2	Area di controllo 2	Area di controllo 2
3	Area di controllo 3	Area di controllo 3
\.


--
-- Data for Name: area_subareas; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.area_subareas (id, area_id, subarea_id, status_id, interval_id, caption) FROM stdin;
1	1	1	1	3	\N
2	1	2	1	3	\N
3	1	3	1	3	\N
4	1	4	1	3	\N
5	1	5	1	3	\N
6	1	6	1	3	\N
7	1	7	1	3	\N
8	1	8	1	3	\N
9	2	9	1	1	\N
10	2	10	1	1	\N
11	2	11	1	1	\N
12	2	12	1	1	\N
13	2	13	1	1	\N
14	2	14	1	1	\N
15	2	15	1	1	\N
\.


--
-- Data for Name: audit_log; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.audit_log (id, "timestamp", company_id, user_id, base_data_id, workflow_id, step_id, action, details) FROM stdin;
\.


--
-- Data for Name: base_data; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.base_data (id, user_id, company_id, interval_id, interval_ord, status_id, record_type, subject_id, legal_document_id, data_type, area_id, subarea_id, lexic_id, created_on, updated_on, deadline, created_by, number_of_doc, date_of_doc, ft1, fb1, fc1, fc2, fc3, fc4, fc5, fc6, fi0, fi1, fi2, fi3, fi4, fi5, fi6, fi7, fi8, fi9, fi10, fi11, fi12, fi13, fi14, fi15, fi16, fn0, fn1, fn2, fn3, fn4, fn5, fn6, fn7, fn8, fn9, file_path, no_action) FROM stdin;
8	1	0	2	1	1	control_area	\N	\N	area contendibilità	2	10	\N	2024-05-21 22:56:55.013691+02	2024-05-21 22:56:55.025992+02	2024-05-21	\N	\N	\N	\N	\N	n3344552	\N	\N	\N	\N	\N	2024	314	442	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0
12	1	0	2	1	1	control_area	\N	\N	area contendibilità	2	10	\N	2024-05-21 22:59:45.329868+02	2024-05-21 22:59:45.335334+02	2024-05-21	\N	\N	\N	\N	\N	n2233	\N	\N	\N	\N	\N	2023	2	2	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0
14	1	0	2	1	1	control_area	\N	\N	grado contendibilità	2	11	\N	2024-05-21 23:00:12.999775+02	2024-05-21 23:00:13.004325+02	2024-05-21	\N	\N	\N	\N	\N	n333	\N	\N	\N	\N	\N	2024	6	3	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	3	3	\N	\N	\N	\N	\N	\N	\N	\N	0
15	1	0	2	1	1	control_area	\N	\N	accesso venditori	2	12	\N	2024-05-21 23:00:46.526069+02	2024-05-21 23:00:46.532833+02	2024-05-21	\N	\N	\N	\N	\N	n5423	\N	\N	\N	\N	\N	2024	54	50	4	23	32	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0
17	1	0	2	1	1	control_area	8	\N	quote mercato ivi	2	13	\N	2024-05-21 23:01:38.184567+02	2024-05-21 23:01:38.189504+02	2024-05-21	\N	\N	\N	\N	\N	n56	\N	\N	\N	\N	\N	2024	34	23	57	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	43	32	\N	\N	\N	\N	\N	\N	\N	\N	0
23	1	0	3	2	1	control_area	7	\N	flussi	1	1	1	2024-05-25 10:48:05.832522+02	2024-05-25 10:48:05.853533+02	\N	\N	\N	\N	\N	\N	nome venditore uno	\N	\N	\N	\N	\N	2024	100	80	20	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0
9	1	0	2	1	1	control_area	\N	\N	struttura offerta	2	9	\N	2024-05-21 22:59:13.07829+02	2024-05-25 10:49:04.806382+02	2024-05-21	\N	\N	\N	\N	\N	n11	\N	\N	\N	\N	\N	2024	2	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0
21	1	0	2	1	1	control_area	\N	\N	livello contendibilità	2	15	\N	2024-05-21 23:17:46.594203+02	2024-05-25 10:50:35.468808+02	2024-05-21	\N	\N	\N	\N	\N	n12	\N	\N	\N	\N	\N	2024	100	60	30	10	12	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	12	12	12	12	\N	\N	\N	\N	\N	\N	0
\.


--
-- Data for Name: basedata_flussi; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.basedata_flussi (id, lexic_id, fn1, fn2, fn3, fc1) FROM stdin;
\.


--
-- Data for Name: basedata_partial; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.basedata_partial (id, lexic_id, fn1, fn2, fn3, fc1) FROM stdin;
\.


--
-- Data for Name: central_data; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.central_data (id, reference_date, interval_id, status_id, user_id, type_id, topic_id, topic1_id, topic2_id, topic3_id, dimension1_id, dimension2_id, dimension3_id, dimension4_id, dimension5_id, dimension6_id, dimension7_id, extended_data, created_on, created_by) FROM stdin;
\.


--
-- Data for Name: company; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.company (id, name, description, address, phone_number, email, website, tax_code, created_on, updated_on, end_of_registration) FROM stdin;
0	Admin	Admin	address admin 112	02-	\N	www.etc	123...000	2024-01-21	2024-03-20	2099-12-31
5	LeReti	LeReti Acqua e Gas	None5	\N	\N	\N	None5	2024-01-21	2024-01-21	\N
6	Centria	Centria	Centria address etc	\N	\N	\N	\N	2024-01-21	2024-03-03	\N
7	Novareti	NOVARETI	\N	\N	\N	\N	\N	2024-01-21	2024-01-21	\N
8	GEI	Gei	\N	\N	\N	\N	\N	2024-01-21	2024-01-21	\N
9	SET	SET	Address of SET	123	emailset@gmail.com	set.it	TaxSet123	2024-01-21	2024-01-21	\N
10	AES	AET	\N	\N	\N	\N	\N	2024-01-21	2024-01-21	\N
11	COGESER	COGESER	\N	\N	\N	\N	\N	2024-01-21	2024-01-21	\N
12	\N	\N	\N	\N	\N	\N	\N	2024-05-15	2024-05-15	\N
\.


--
-- Data for Name: company_users; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.company_users (id, company_id, user_id, created_on, updated_on, end_of_registration) FROM stdin;
1	0	1	2024-05-21 23:10:03.033871+02	2024-05-21 23:10:03.033871+02	\N
\.


--
-- Data for Name: config; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.config (id, config_type, company_id, area_id, subarea_id, config_integer, config_number, config_text, config_date) FROM stdin;
1	extra_time	\N	\N	\N	0	0	\N	\N
2	area_interval	\N	1	\N	3	\N	\N	\N
3	area_interval	\N	2	\N	2	\N	\N	\N
4	area_interval	\N	3	\N	1	\N	\N	\N
\.


--
-- Data for Name: deadline; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.deadline (id, company_id, area_id, subarea_id, interval_id, status_id, status_start, status_end) FROM stdin;
1	0	1	1	3	3	2000-01-01 00:00:00.000000	2023-12-31 23:59:59.000000
2	0	1	2	3	3	2000-01-01 00:00:00.000000	2023-12-31 23:59:59.000000
3	0	1	3	3	3	2000-01-01 00:00:00.000000	2023-12-31 23:59:59.000000
4	0	1	4	3	3	2000-01-01 00:00:00.000000	2023-12-31 23:59:59.000000
5	0	1	5	3	3	2000-01-01 00:00:00.000000	2023-12-31 23:59:59.000000
6	0	1	6	3	3	2000-01-01 00:00:00.000000	2023-12-31 23:59:59.000000
7	0	1	7	3	3	2000-01-01 00:00:00.000000	2023-12-31 23:59:59.000000
8	0	1	8	3	3	2000-01-01 00:00:00.000000	2023-12-31 23:59:59.000000
9	0	1	1	3	1	2024-01-01 00:00:00.000000	2024-04-30 23:59:59.000000
10	0	1	2	3	1	2024-01-01 00:00:00.000000	2024-04-30 23:59:59.000000
11	0	1	3	3	1	2024-01-01 00:00:00.000000	2024-04-30 23:59:59.000000
12	0	1	4	3	1	2024-01-01 00:00:00.000000	2024-04-30 23:59:59.000000
13	0	1	5	3	1	2024-01-01 00:00:00.000000	2024-04-30 23:59:59.000000
14	0	1	6	3	1	2024-01-01 00:00:00.000000	2024-04-30 23:59:59.000000
15	0	1	7	3	1	2024-01-01 00:00:00.000000	2024-04-30 23:59:59.000000
16	0	1	8	3	1	2024-01-01 00:00:00.000000	2024-04-30 23:59:59.000000
\.


--
-- Data for Name: employee; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.employee (id, name, "position", company_id) FROM stdin;
\.


--
-- Data for Name: inline_fields; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.inline_fields (id, question_id, answer_text, answer_score, answer_file, comment_text) FROM stdin;
\.


--
-- Data for Name: interval; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public."interval" (id, name, description, interval_id) FROM stdin;
1	Y	Year	1
2	H	Semester	2
3	S	Quadrimester	3
4	Q	Quarter	4
5	M	Month	12
6	F	Fortnight	26
7	W	Week	52
\.


--
-- Data for Name: legal_document; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.legal_document (id, name, tier_1, tier_2, tier_3) FROM stdin;
5	Citazione in giudizio	Atti	A9	1
6	Altro	Atti	A9	6
7	Lettera da autorità	Atti	A9	2
8	Lettera da utente	Atti	A9	3
9	Lettera da fornitore	Atti	A9	4
10	Esposto all'autorità	Atti	A9	5
\.


--
-- Data for Name: lexic; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.lexic (id, category, name) FROM stdin;
1	Precomplaint	Da utente su questioni proprie
2	Precomplaint	Da utente per conto del cliente
3	Precomplaint	Cliente finale per proprio conto
4	Precomplaint	Cliente finale che si rivolge allo sportello del consumatore
\.


--
-- Data for Name: possible_answers; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.possible_answers (id, question_id, text, next_question_id) FROM stdin;
\.


--
-- Data for Name: post; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.post (id, company_id, user_id, sender, message_type, subject, body, created_at, marked_as_read, lifespan) FROM stdin;
1	\N	1	System	email	Security check	È stato rilevato un nuovo accesso al tuo account il 2024-05-29. Se eri tu, non devi fare nulla. In caso contrario, ti aiuteremo a proteggere il tuo account; non rispondere a questa mail e contatta l'amministratore del sistema. 	2024-05-29 20:03:53.491189+02	f	one-off
\.


--
-- Data for Name: question; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.question (id, question_id, text, answer_type, answer_width, answer_fields) FROM stdin;
17	S11-A11	Governance - Struttura gestore - Struttura ordinaria	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
23	S11-A13	Soluzione spuria con rilevanti distonie rispetto al quadro regolatorio di riferimento (es. monocratico senza personale con funzioni dirigenziali etc.)	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
34	S11-A4121	Pieno rispetto, in continuità, delle cadenze e tempistiche previste dal TIUF - nel caso di discontinuità, formalizzazione di motivazioni adeguate rispetto alla situazione formalmente derogatoria in termini di cause indipendenti dalla volontà del DSO o comunque non disponibili al DSO  	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
2	Q2CCLR-A4.1	Impatto della pianificazione non valutabile senza controllo effettivo su procedura e contenuti della decisione	CB, CB, CB, TST, NUM, HML, TLT, TLT, TLT	40, 40, 40, 200, 150, 100, 250, 250, 250	"[{\\"type\\": \\"CB\\", \\"value\\": \\"\\", \\"width\\": 40}, {\\"type\\": \\"CB\\", \\"value\\": \\"\\", \\"width\\": 40}, {\\"type\\": \\"CB\\", \\"value\\": \\"\\", \\"width\\": 40}, {\\"type\\": \\"TST\\", \\"value\\": \\"\\", \\"width\\": 200}, {\\"type\\": \\"NUM\\", \\"value\\": \\"\\", \\"width\\": 150}, {\\"type\\": \\"HML\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 250}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 250}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 250}]"
51	QA1-7	Altre informazioni	TLT	1200	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}]"
52	QA1-8	Scadenza	DD	150	"[{\\"type\\": \\"DD\\", \\"value\\": \\"\\", \\"width\\": 150}]"
18	S11-A12	Governance - Struttura gestore - Struttura derogatoria	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
35	S11-A4122	Sporadiche alterazioni della cadenza legale della predisposizione/trasmissione della singola sessione annuale - assenza di motivazioni obiettive indipendenti dalla volontà del DSO (ritardi da meri condizionamenti organizzativi interni comunque disponibili al DSO)	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
36	S11-A4123	Irregolarità costante del processo e dei conseguenti apporti ad ARERA - omissione di scadenze senza motivazioni obiettive a supporto indipendenti dalla volontà del DSO 	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
45	QA1-1	Indicare se nel periodo di riferimento sono stati segnalati malfunzionamenti o guasti delle apparecchiature che hanno comportato la necessità di stimare i quantitativi immessi.	BYN	75	"[{\\"type\\": \\"BYN\\", \\"value\\": \\"\\", \\"width\\": 75}]"
49	QA1-5	(Se sì) Specificare se uno o più utenti hanno lamentato problemi di incoerenza tra la quantità di gas fatturato e allocato ai propri clienti, chiedendo alla vostra Società di effettuare verifiche sulla correttezza dei processi di settlement fisico	BYN	75	"[{\\"type\\": \\"BYN\\", \\"value\\": \\"\\", \\"width\\": 75}]"
24	S11-A21	Governance - Singolo componente - Piena trasparenza e completezza della documentazione in ordine alla situazione individuale rispetto ai requisiti di compatibilità – assenza di situazioni dubbie da inquadrare e controllare specificamente. 	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
25	S11-A22	Governance - Singolo componente - Piena trasparenza e completezza della documentazione in ordine alla situazione individuale rispetto ai requisiti di compatibilità – singole situazioni di non chiara integrazione dei requisiti con connessa esigenza di approfondimenti o di controlli specifici sulle nomine adottate  in situazioni limite – esito positivo degli approfondimenti	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
26	S11-A23	Governance - Singolo componente - Carenze o opacità del quadro documentale - situazioni di possibile contrasto con le disposizioni sui requisiti - esigenza di controllo capillare sulle modalità concrete di funzionamento del gestore indipendente	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
27	S11-A31	Governance - Singolo componente - Gestione coerente dell’organo amministrativo duplice (differenziazione delle sfere decisionali di pertinenza del CDA e del Comitato-gestore indipendente; gestione effettiva delle attività segregate da parte della componente strutturale del DSO riportabile al gestore indipendente con una catena decisionale e operativa segregata riportabile al gestore indipendente.) 	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
1	Q2CCLR-A1-A3	Impatto non valutabile senza controllo sulla gestione del servizio – bassa compliance accresce i livelli di rischio potenziale	CB, CB, CB, TST, NUM, HML, TLT, TLT, TLT	40, 40, 40, 200, 150, 100, 250, 250, 250	"[{\\"type\\": \\"CB\\", \\"value\\": \\"\\", \\"width\\": 40}, {\\"type\\": \\"CB\\", \\"value\\": \\"\\", \\"width\\": 40}, {\\"type\\": \\"CB\\", \\"value\\": \\"\\", \\"width\\": 40}, {\\"type\\": \\"TST\\", \\"value\\": \\"\\", \\"width\\": 200}, {\\"type\\": \\"NUM\\", \\"value\\": \\"\\", \\"width\\": 150}, {\\"type\\": \\"HML\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 250}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 250}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 250}]"
30	S11-A4111	Esercizio effettivo della responsabilità – valutazioni e assemblaggio da parte del gestore indipendente e della struttura segregata del DSO alle sue dirette ed esclusive dipendenze; supporti esterni da parte di strutture del gruppo solo per la raccolta di elementi conoscitivi utili all’istruttoria – nel caso di parziale o totale mancata approvazione da parte del cda della proposta, formalizzazione di parere motivato in ordine alla applicabilità o inapplicabilità delle indicazioni del gruppo e gestione conseguente del procedimento informativo del regolatore – riscontri documentali adeguati degli elementi di questa valutazione. 	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
47	QA1-3	(Se sì)  Specificare se tale criterio è stato concordato con la vostra Società	BYN	75	"[{\\"type\\": \\"BYN\\", \\"value\\": \\"\\", \\"width\\": 75}]"
19	S11-A121	Governance - Struttura gestore - Struttura derogatoria monocratica (amministratore unico con inclusione del personale con funzioni dirigenziali)	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
20	S11-A1221	Governance - Struttura gestore - Struttura derogatoria pluripersonale – comitato esecutivo - inclusione del personale con funzioni dirigenziali e piena applicazione della governance duale	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
21	S11-A1222	Governance - Struttura gestore - Struttura derogatoria pluripersonale – comitato esecutivo - parziale (inclusione del personale con funzioni dirigenziali più inapplicazione della governance duale) 	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
22	S11-A1223	Governance - Struttura gestore - Struttura derogatoria pluripersonale – comitato esecutivo - ridotta (parziale o totale esclusione del personale con funzioni manageriali apicali – inapplicazione della governance duale) 	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
28	S11-A32	Governance - Singolo componente - Gestione non coerente dell’organo amministrativo duplice e del segmento operativo segregato (carenze su alcuni dei punti indicati sub A.3.1 – 6 Pt; carenze su tutti i punti indicati sub A.3.1 – 2 pt)	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
32	S11-A4113	Esercizio solo formale delle responsabilità (decisione/delibera meramente notarile di approvazione della proposta da rimettere alla capogruppo) 	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
33	S11-A412	Cadenze e tempistiche	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
38	S11-A4131	Documentabilità della completezza ed effettività dei flows conoscitivi da cui sono estratte le esigenze di intervento - adeguatezza della metodica costi-benefici applicata per selezionare ed ordinare le scelte operate sul piano del set di interventi inseriti nel singolo piano 	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
39	S11-A4132	Parzialità, incompletezza dei flows conoscitivi da cui sono estratte le esigenze di intervento; base documentabile, ma non completa o comunque tale da evidenziare carenze di elementi e approfondimenti potenzialmente utili alla gestione del piano - adeguatezza della metodica costi-benefici applicata per selezionare ed ordinare le scelte operate sul piano del set di interventi inseriti nel singolo piano 	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
40	S11-A4133	Opacità dei flows informativi utilizzati per estrarre le ipotesi di intervento da cui selezionare ed ordinare i punti del piano - centralità e visibilità di apporti eteronomi non direttamente individuati ed analizzati dal gestore indipendente (piano sostanzialmente eteronomo) - inadeguatezza, o comunque opacità e non valutabilità della metodica costi-benefici o comunque impossibilità di apprezzare le motivazioni alla base della costruzione dell’ordine di priorità con cui è stato declinato il piano 	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
46	QA1-2	(Se sì) Specificare quale criterio ha seguito la società di trasporto per l'effettuazione della stima dei quantitativi immessi	TST	1000	"[{\\"type\\": \\"TST\\", \\"value\\": \\"\\", \\"width\\": 1000}]"
48	QA1-4	Indicare se nel periodo di riferimento si sono verificati scostamenti nei quantitativi tra gas immesso nella singola RE.MI. e gas complessivamente distribuito nell’impianto in consegna ai clienti finali	BYN	75	"[{\\"type\\": \\"BYN\\", \\"value\\": \\"\\", \\"width\\": 75}]"
50	QA1-6	(Se sì) In caso positivo fornire riscontri sulle verifiche effettuate e sugli esiti che hanno prodotto	FILE	800	"[{\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 800}]"
31	S11-A4112	Esercizio effettivo della responsabilità,  ma con supporti da parte delle strutture esterne del gruppo direttamente impattanti sul processo decisionale (pre-istruttoria e inquadramento/costruzione di parametri vincolanti per la decisione, ad eccezione di quelli espressamente previsti dal TIUF e da ARERA); autonomia e corretta gestione procedurale dell’iter informativo di ARERA nel caso di decisioni del gruppo di rigetto totale o parziale della proposta  	TLT,  NI(0-10),  FILE,  TLT	1200, 100, 700, 1150	"[{\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1200}, {\\"type\\": \\"NI(0-10)\\", \\"value\\": \\"\\", \\"width\\": 100}, {\\"type\\": \\"FILE\\", \\"value\\": \\"\\", \\"width\\": 700}, {\\"type\\": \\"TLT\\", \\"value\\": \\"\\", \\"width\\": 1150}]"
\.


--
-- Data for Name: questionnaire; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.questionnaire (id, questionnaire_id, questionnaire_type, name, "interval", deadline_date, status_id, created_on, updated_on, headers) FROM stdin;
5	S11_QCSF	Questionnaire	Survey sulla qualità della compliance alla separazione funzionale	S1 2024	2024-12-31 00:00:00+01	1	2024-03-29 00:00:00+01	2024-03-29 00:00:00+01	[{"title": "1. Dichiarazioni impresa", "tooltip": "Specificare il contenuto delle comunicazioni e dichiarazione impresa relativamente al punto specifico", "width": 350},\n {"title": "2. Punteggio", "tooltip": "Puntegio stimato sulla base delle dichiarazioni impresa.", "width": 150},\n {"title": "3. Documentazione a supporto", "tooltip": "Documentazione a supporto delle dichiarazioni presentate.", "width": 150},\n {"title": "4. Commenti auditor", "tooltip": "Commenti auditor", "width": 350}]
1	ADC1Q1	Questionnaire	Area di controllo 1	Q1 2024	2024-12-31 00:00:00+01	1	2024-02-28 00:00:00+01	2024-03-29 00:00:00+01	[{"title": "Questions and answers", "tooltip": "Questions and answers", "width": 650}]
2	ADC1Q2	Questionnaire	Area di controllo 2	Q1 2024	2024-12-31 00:00:00+01	1	2024-02-28 00:00:00+01	2024-03-29 00:00:00+01	[{"title": "Questions and answers", "tooltip": "Questions and answers", "width": 650}]
3	ADC1Q3	Questionnaire	Area di controllo 3	Q1 2024	2024-12-31 00:00:00+01	1	2024-02-28 00:00:00+01	2024-03-29 00:00:00+01	[{"title": "Questions and answers", "tooltip": "Questions and answers", "width": 650}]
6	Q2_CCLR	QuestionnaireH	Check 2 Costi compliance per livello di rischio	S1 2024	2024-12-31 00:00:00+01	1	2024-04-19 00:00:00+02	2024-04-19 00:00:00+02	[{"title": "Segmento normativo", "tooltip": "Selezionare le aree impattate", "width": 120},\n {"title": "Aree di rischio e costi", "tooltip": "Costi della soluzione", "width": 250},\n {"title": "Livello compliance", "tooltip": "Livello accertato della compliance ai vincoli di separazione funzionale", "width": 100},\n {"title": "Rischi coperti: 1) Gestione discriminatoria reti; 2) Abuso di info sensibili; 3) Sussidi indebiti", "tooltip": "Livello effettivo da verifiche output based costantemente effettuate: 1.  Gestione discriminatoria delle reti; 2.  Abuso di informazioni commercialmente sensibili; 3.  Sussidi indebiti ad altre attività del gruppo a carico della tariffa", "width": 600}]
\.


--
-- Data for Name: questionnaire_companies; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.questionnaire_companies (id, questionnaire_id, company_id, status_id) FROM stdin;
1	1	12	2
2	1	10	2
3	2	10	2
4	3	10	2
5	1	8	2
6	1	5	2
7	1	6	2
8	1	7	2
9	1	9	2
10	1	11	2
12	1	0	2
13	2	0	2
14	3	0	2
17	5	0	2
18	5	6	2
19	5	7	2
20	5	8	2
21	6	0	2
22	6	5	2
23	6	6	2
24	6	7	2
25	6	8	2
26	6	9	2
27	6	10	2
28	6	11	2
\.


--
-- Data for Name: questionnaire_questions; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.questionnaire_questions (id, questionnaire_id, question_id, extra_data) FROM stdin;
9	5	17	\N
10	5	18	\N
11	5	19	\N
12	5	20	\N
13	5	21	\N
14	5	22	\N
15	5	23	\N
16	5	24	\N
17	5	25	\N
18	5	26	\N
19	5	28	\N
1	1	45	\N
2	1	49	\N
3	1	47	\N
4	1	48	\N
5	1	50	\N
6	1	51	\N
7	1	52	\N
8	6	1	\N
20	6	2	\N
\.


--
-- Data for Name: role; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.role (id, role_id, name, description) FROM stdin;
1	1	Admin	Administrator role
2	2	Authority	ARERA
3	3	Manager	Company Superuser
4	4	Employee	Authorised company user
5	5	Guest	Public area only
6	6	Provider	(e.g. External Audit)
\.


--
-- Data for Name: status; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.status (id, name, description) FROM stdin;
1	Initiate	The item is active and can be edited or submitted.
2	Open	The data record is open for further processing or approval.
3	Closed	The record cannot be edited at this stage.
4	Pending	The data record is pending processing or approval.
5	Delayed	The data record deadline is postponed for processing,  submission or approval.
6	Overdue	The data record is overdue.
7	Processing	The data record is currently being processed.
8	Approved	The data record has been approved.
9	Rejected	The data record has been rejected and needs to be revised and submitted again.
10	Submitted	The data record is no longer active and is submitted for audit, authorisation or storage purposes.
11	Suspended	The data record is overdue.
12	Undefined	The status of this record can not be determined.
13	Extratime	The status is now re-open for a limited period of time.
\.


--
-- Data for Name: step; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.step (id, name, description, action, "order", next_step_id, deadline_date, reminder_date) FROM stdin;
15	Submitted	Survey Submitted	Submitted	15	\N	\N	\N
1	Creazione documento	Fase iniziale	Create document	1	2	\N	\N
2	Revisione documento	Fase di revisione	Review document	2	3	\N	\N
3	Coinvolgimento auditor esterno	Fase di verifica	Avvio benchmarking	3	4	\N	\N
4	Compilazione prospetto	Fase di verifica	Compilazione prospetto	4	5	\N	\N
5	Valutazione auditor esterno	Fase di verifica	Compilazione benchmark	5	6	\N	\N
6	Commenti società	Fase di verifica	Commenti società	6	7	\N	\N
7	Chiusura audit	Fase finale	Chiusura audit	7	8	\N	\N
8	Relazione finale audit	Fase finale	Relazione finale audit	8	9	\N	\N
9	Creazione documento 2	Creazione documento interno	Crea documento	9	10	\N	\N
10	Inizio procedura	Inizio procedura regolamentare, di verifica o conoscitiva	Fase iniziale	10	11	\N	\N
11	Fine procedura	Fine della procedura regolamentare	Conclusione della procedura	11	12	\N	\N
12	Creazione Survey	Predisposizione per la distribuzione ai soggetti destinatari	Preparazione	12	13	\N	\N
13	Fase di compilazione	La survey è disponibile per la compilazione	Compilazione	13	14	\N	\N
16	End of workflow	EOW	EOW	99	\N	\N	\N
14	Save for later	Survey salvata	Save for later	14	14	\N	\N
\.


--
-- Data for Name: step_base_data; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.step_base_data (id, base_data_id, workflow_id, step_id, status_id, start_date, deadline_date, auto_move, end_date, hidden_data, start_recall, deadline_recall, end_recall, recall_unit, open_action) FROM stdin;
\.


--
-- Data for Name: step_questionnaire; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.step_questionnaire (id, questionnaire_id, workflow_id, step_id, status_id, start_date, deadline_date, auto_move, end_date, hidden_data, start_recall, deadline_recall, end_recall, recall_unit, open_action) FROM stdin;
\.


--
-- Data for Name: subarea; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.subarea (id, name, description, data_type) FROM stdin;
1	flussi	1)  Flussi di pre-complaint	Table
2	atti	2) Atti di complaint	Table
3	contenziosi	3) Contenziosi	Table
4	contingencies	4) Contingencies	Table
5	settlement	5) Settlement fisico	Questionnaire
6	iniziative_dso_as	6) Iniziative DSO verso AS	Table
7	inziative_as_dso	7) Iniziative AS verso DSO	Table
8	iniziative_dso_dso	8) Iniziative DSO verso DSO	Table
9	struttura offerta	1) Liberalizzazione del segmento di mercato rilevante gestito dal DSO per il settlement fisico	Table
10	area contendibilità	2) Area di contendibilità della domanda nel SMR	Table
11	grado contendibilità	3) Grado di contendibilità per fasce di domanda	Table
12	accesso venditori	4) Accesso dei venditori operativi nel SMR alle prestazioni del DSO strumentali alla gestione dell'attività di commercializzazione	Table
13	quote mercato ivi	5) Quote di mercato della IVI nel settore vendita del SMR	Table
14	trattamento switching	6) Switching (trattamento della vendita dell'IVI rispetto agli altri operatori)	Table
15	livello contendibilità	7) Livello effettivo di contendendibilità dei clienti finali condizionabili	Table
\.


--
-- Data for Name: subject; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.subject (id, name, tier_1, tier_2, tier_3) FROM stdin;
1	Servizi generali	Servizi	A	B
2	Servizi legali	Servizi	A	C
3	Gestione parco auto	Servizi	A	D
4	Gestione personale	Servizi	A	D
6	Altro servizio	Servizi	A	E
7	Domestici	Utenti	U	1
8	Condominio	Utenti	U	2
9	Pubblica amministrazione	Utenti	U	4
10	Altri usi	Utenti	U	3
11	Citazione in giudizio	Legale	L	1
12	Lettera da autorità	Legale	L	2
13	Esposto all'autorità	Legale	L	3
14	Lettera da utente	Legale	L	4
15	Lettera da fornitore	Legale	L	5
16	Altro documento	Legale	L	8
17	Corrispondenza per audit	Legale	L	7
18	Documento interno	Legale	L	6
19	Altro utente	Utenti	\N	\N
\.


--
-- Data for Name: table; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public."table" (id, name, description, user_id, subject_id, column1, column2, created_on) FROM stdin;
\.


--
-- Data for Name: table_base; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.table_base (id, name, description, subject_id, company_id, user_id, column1, column2, created_on) FROM stdin;
8	Tabella 1	Description of table 1	1	8	\N	ABC 0	ABC 123456	2023-12-24 00:00:00.000000
9	Tabella 2	Description of table 1	2	8	\N	ABC 123	5555	2023-12-24 00:00:00.000000
10	Tabella 3	Description of table 1	3	8	\N	abc	12345678654321	2023-12-24 00:00:00.000000
11	Tabella 1	Description of table 1	4	8	\N	ABC 3	ABC 321 etc	2023-12-24 00:00:00.000000
12	Tabella 3	Description of table 1	1	8	\N	ABC 4	23245959	2023-12-24 00:00:00.000000
13	Tabella 1	Description of table 1	2	8	\N	ABC 5	ABC 5	2023-12-24 00:00:00.000000
15	Tabella 1	Description of table 1	3	8	\N	ABC 7	77	2023-12-24 00:00:00.000000
16	Tabella 1	Description of table 1	4	8	\N	ABC 8	96	2023-12-24 00:00:00.000000
17	Tabella 3	Description of table 1	1	8	\N	ABC 9	2132341234	2023-12-24 00:00:00.000000
18	Tabella 1	Description of table 1	2	8	\N	ABC 0	Editing card nr 18	2023-12-24 00:00:00.000000
19	Tabella 1	Description of table 1	3	8	\N	ABC 1	5	2023-12-24 00:00:00.000000
20	Tabella 3	Description of table 1	4	8	\N	ABC 2	112234	2023-12-24 00:00:00.000000
21	Tabella 1	Description of table 1	1	8	\N	ABC 3	21	2023-12-24 00:00:00.000000
22	Tabella 1	Description of table 1	2	8	\N	ABC 4	32	2023-12-24 00:00:00.000000
23	Tabella 1	Description of table 1	3	8	\N	ABC 5	45	2023-12-24 00:00:00.000000
24	Tabella 1	Description of table 1	4	8	\N	ABC 6	ABC 621	2023-12-24 00:00:00.000000
25	Tabella 2	Description of table 1	\N	8	\N	99ABC 7788	777788	2023-12-24 00:00:00.000000
26	Tabella 1	Description of table 1	\N	8	\N	ABC 8	ABC 821	2023-12-24 00:00:00.000000
27	Tabella 1	Description of table 1	\N	8	\N	ABC 9	ABC 9	2023-12-24 00:00:00.000000
28	Tabella 1	Description of table 1	\N	8	\N	ABC 0	0	2023-12-24 00:00:00.000000
29	Tabella 1	Description of table 1	\N	8	\N	ABC 1	15	2023-12-24 00:00:00.000000
30	Tabella 1	Description of table 1	\N	8	\N	ABC 2	36	2023-12-24 00:00:00.000000
31	Tabella 2	Description of table 1	\N	8	\N	ABC 3	69	2023-12-24 00:00:00.000000
32	Tabella 1	Description of table 1	\N	8	\N	ABC 4	120	2023-12-24 00:00:00.000000
33	Tabella 1	Description of table 1	\N	8	\N	ABC 5	195	2023-12-24 00:00:00.000000
34	Tabella 1	Description of table 1	\N	8	\N	ABC 6	300	2023-12-24 00:00:00.000000
35	Tabella 1	Description of table 1	\N	8	\N	ABC 7	441	2023-12-24 00:00:00.000000
36	Tabella 1	Description of table 1	\N	8	\N	ABC 8	624	2023-12-24 00:00:00.000000
37	Tabella 1	Description of table 1	\N	8	\N	ABC 9	855	2023-12-24 00:00:00.000000
38	Tabella 1	Description of table 1	\N	8	\N	ABC 0	0	2023-12-24 00:00:00.000000
39	Tabella 1	Description of table 1	\N	8	\N	ABC 1	15	2023-12-24 00:00:00.000000
40	Tabella 1	Description of table 1	\N	8	\N	ABC 2	36	2023-12-24 00:00:00.000000
41	Tabella 1	Description of table 1	\N	8	\N	ABC 3	69	2023-12-24 00:00:00.000000
42	Tabella 1	Description of table 1	\N	8	\N	ABC 4	120	2023-12-24 00:00:00.000000
43	Tabella 1	Description of table 1	\N	8	\N	ABC 5	195	2023-12-24 00:00:00.000000
44	Tabella 1	Description of table 1	\N	8	\N	ABC 6	300	2023-12-24 00:00:00.000000
45	Tabella 1	Description of table 1	\N	8	\N	ABC 7	441	2023-12-24 00:00:00.000000
46	Tabella 1	Description of table 1	\N	8	\N	ABC 8	624	2023-12-24 00:00:00.000000
47	Tabella 1	Description of table 1	\N	8	\N	ABC 9	855	2023-12-24 00:00:00.000000
48	name 112	desc 112	\N	8	\N	col 112	1121122	2023-12-29 12:25:06.433135
49	n 13	\N	\N	8	\N	c 13	1313	2023-12-29 13:03:49
51	Tabella 2		\N	8	\N	bce 123	8888	2023-12-29 20:45:01
52	Tabella 2		\N	8	\N	bce 123	8888	2023-12-29 20:45:04
53	Tabella 2		\N	\N	\N	fgH 456	9999	2023-12-29 20:45:59
54	Tabella 2		\N	\N	\N	girt jay 1	1001001	2023-12-29 21:19:03
\.


--
-- Data for Name: table_gen; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.table_gen (id, name, description, user_id, subject_id, column1, column2, created_on) FROM stdin;
\.


--
-- Data for Name: task; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.task (id, name, status, workflow_id) FROM stdin;
\.


--
-- Data for Name: test_table; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.test_table (id, name) FROM stdin;
1	Test Name
2	Test Name
\.


--
-- Data for Name: ticket; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.ticket (id, user_id, subject_id, subject, description, status_id, created_at, marked_as_read, lifespan) FROM stdin;
\.


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.user_roles (id, user_id, role_id, created_on, updated_on, end_of_registration) FROM stdin;
1	1	1	\N	\N	\N
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.users (id, username, email, password_hash, user_2fa_secret, title, first_name, mid_name, last_name, company, company_id, address, address1, city, province, region, zip_code, country, tax_code, mobile_phone, work_phone, created_on, updated_on, end_of_registration) FROM stdin;
1	a08123456	a08@gmail.com	$2b$12$OI8iH7UwxRLw0Yf5sEBGC.aiY7UreabJXOctwP8u.09Po0Ru3FWCO	4C5APFKUIZ5HTSZL6TJONPACMMOQ3QYJ	\N				\N	\N											2024-05-21 11:54:26.054016+02	2024-05-21 11:54:26.054016+02	\N
\.


--
-- Data for Name: workflow; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.workflow (id, name, description, status, restricted, deadline_date, reminder_date) FROM stdin;
1	Creazione documento	Test-only workflow	Document Gathering Session Opened	0	2024-05-04 20:34:43.340101+02	\N
3	Verifica contratti infragruppo	Procedura di verifica dei contratti infragruppo	Active	1	2099-12-31 23:59:00+01	2024-12-15 07:00:00+01
4	Archivio interno	Archiviazione	Active	0	\N	\N
5	Procedura interna	Procedura interna	Active	0	\N	\N
6	Procedura regolamentare	Procedura avviata su iniziativa dell'autorità	Active	1	\N	\N
7	Procedura audit interno	Procedura avviata dall'audit interno	Active	0	\N	\N
8	Procedura audit esterno	Procedura avviata dall'audit esterno	Active	1	\N	\N
9	Procedura iniziata da terzi	Procedura specifica	Active	0	\N	\N
10	Procedura verso terzi	Procedura specifica	Active	0	\N	\N
11	Iniziative da parte dei fornitori	Procedura specifica	Active	0	\N	\N
14	Trasferimento documento	Trasmissione documento all'esterno	Active	0	2029-03-31 15:12:00+02	\N
15	Survey	Workflow specifico per creazione, compilazione, raccolta e analisi dei sondaggi	\N	0	\N	\N
\.


--
-- Data for Name: workflow_base_data; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.workflow_base_data (id, workflow_id, base_data_id, created_on, updated_on, end_of_registration) FROM stdin;
\.


--
-- Data for Name: workflow_steps; Type: TABLE DATA; Schema: public; Owner: aradulescu
--

COPY public.workflow_steps (id, workflow_id, step_id) FROM stdin;
16	3	3
17	3	4
18	3	5
19	3	6
21	3	8
22	3	1
23	3	2
24	3	7
25	1	1
26	1	2
27	1	3
28	1	5
29	1	6
31	1	8
32	4	1
33	14	9
34	6	10
35	6	10
37	15	12
38	15	13
39	15	14
40	15	15
\.


--
-- Name: answer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.answer_id_seq', 9, true);


--
-- Name: area_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.area_id_seq', 1, false);


--
-- Name: area_subareas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.area_subareas_id_seq', 1, false);


--
-- Name: audit_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.audit_log_id_seq', 1, false);


--
-- Name: base_data_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.base_data_id_seq', 25, true);


--
-- Name: basedata_flussi_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.basedata_flussi_id_seq', 1, false);


--
-- Name: basedata_partial_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.basedata_partial_id_seq', 1, false);


--
-- Name: central_data_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.central_data_id_seq', 1, false);


--
-- Name: company_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.company_id_seq', 1, false);


--
-- Name: company_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.company_users_id_seq', 1, true);


--
-- Name: config_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.config_id_seq', 1, false);


--
-- Name: deadline_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.deadline_id_seq', 1, false);


--
-- Name: employee_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.employee_id_seq', 1, false);


--
-- Name: inline_fields_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.inline_fields_id_seq', 1, false);


--
-- Name: interval_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.interval_id_seq', 1, false);


--
-- Name: legal_document_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.legal_document_id_seq', 1, false);


--
-- Name: lexic_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.lexic_id_seq', 1, false);


--
-- Name: possible_answers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.possible_answers_id_seq', 1, false);


--
-- Name: post_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.post_id_seq', 1, true);


--
-- Name: question_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.question_id_seq', 2, true);


--
-- Name: questionnaire_companies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.questionnaire_companies_id_seq', 1, false);


--
-- Name: questionnaire_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.questionnaire_id_seq', 1, false);


--
-- Name: questionnaire_questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.questionnaire_questions_id_seq', 21, true);


--
-- Name: role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.role_id_seq', 1, false);


--
-- Name: status_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.status_id_seq', 1, false);


--
-- Name: step_base_data_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.step_base_data_id_seq', 1, false);


--
-- Name: step_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.step_id_seq', 16, true);


--
-- Name: step_questionnaire_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.step_questionnaire_id_seq', 1, false);


--
-- Name: subarea_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.subarea_id_seq', 1, false);


--
-- Name: subject_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.subject_id_seq', 1, false);


--
-- Name: table_base_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.table_base_id_seq', 1, false);


--
-- Name: table_gen_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.table_gen_id_seq', 1, false);


--
-- Name: table_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.table_id_seq', 1, false);


--
-- Name: task_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.task_id_seq', 1, false);


--
-- Name: test_table_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.test_table_id_seq', 2, true);


--
-- Name: ticket_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.ticket_id_seq', 1, false);


--
-- Name: user_roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.user_roles_id_seq', 1, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: workflow_base_data_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.workflow_base_data_id_seq', 1, false);


--
-- Name: workflow_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.workflow_id_seq', 1, false);


--
-- Name: workflow_steps_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aradulescu
--

SELECT pg_catalog.setval('public.workflow_steps_id_seq', 1, false);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: answer answer_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.answer
    ADD CONSTRAINT answer_pkey PRIMARY KEY (id);


--
-- Name: area area_name_key; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.area
    ADD CONSTRAINT area_name_key UNIQUE (name);


--
-- Name: area area_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.area
    ADD CONSTRAINT area_pkey PRIMARY KEY (id);


--
-- Name: area_subareas area_subareas_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.area_subareas
    ADD CONSTRAINT area_subareas_pkey PRIMARY KEY (id);


--
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (id);


--
-- Name: base_data base_data_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.base_data
    ADD CONSTRAINT base_data_pkey PRIMARY KEY (id);


--
-- Name: basedata_flussi basedata_flussi_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.basedata_flussi
    ADD CONSTRAINT basedata_flussi_pkey PRIMARY KEY (id);


--
-- Name: basedata_partial basedata_partial_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.basedata_partial
    ADD CONSTRAINT basedata_partial_pkey PRIMARY KEY (id);


--
-- Name: central_data central_data_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.central_data
    ADD CONSTRAINT central_data_pkey PRIMARY KEY (id);


--
-- Name: company company_name_key; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.company
    ADD CONSTRAINT company_name_key UNIQUE (name);


--
-- Name: company company_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.company
    ADD CONSTRAINT company_pkey PRIMARY KEY (id);


--
-- Name: company_users company_users_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.company_users
    ADD CONSTRAINT company_users_pkey PRIMARY KEY (id);


--
-- Name: config config_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.config
    ADD CONSTRAINT config_pkey PRIMARY KEY (id);


--
-- Name: deadline deadline_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.deadline
    ADD CONSTRAINT deadline_pkey PRIMARY KEY (id);


--
-- Name: employee employee_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_pkey PRIMARY KEY (id);


--
-- Name: inline_fields inline_fields_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.inline_fields
    ADD CONSTRAINT inline_fields_pkey PRIMARY KEY (id);


--
-- Name: interval interval_name_key; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public."interval"
    ADD CONSTRAINT interval_name_key UNIQUE (name);


--
-- Name: interval interval_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public."interval"
    ADD CONSTRAINT interval_pkey PRIMARY KEY (id);


--
-- Name: legal_document legal_document_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.legal_document
    ADD CONSTRAINT legal_document_pkey PRIMARY KEY (id);


--
-- Name: lexic lexic_name_key; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.lexic
    ADD CONSTRAINT lexic_name_key UNIQUE (name);


--
-- Name: lexic lexic_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.lexic
    ADD CONSTRAINT lexic_pkey PRIMARY KEY (id);


--
-- Name: possible_answers possible_answers_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.possible_answers
    ADD CONSTRAINT possible_answers_pkey PRIMARY KEY (id);


--
-- Name: post post_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.post
    ADD CONSTRAINT post_pkey PRIMARY KEY (id);


--
-- Name: question question_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.question
    ADD CONSTRAINT question_pkey PRIMARY KEY (id);


--
-- Name: questionnaire_companies questionnaire_companies_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.questionnaire_companies
    ADD CONSTRAINT questionnaire_companies_pkey PRIMARY KEY (id);


--
-- Name: questionnaire questionnaire_name_key; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.questionnaire
    ADD CONSTRAINT questionnaire_name_key UNIQUE (name);


--
-- Name: questionnaire questionnaire_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.questionnaire
    ADD CONSTRAINT questionnaire_pkey PRIMARY KEY (id);


--
-- Name: questionnaire questionnaire_questionnaire_id_key; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.questionnaire
    ADD CONSTRAINT questionnaire_questionnaire_id_key UNIQUE (questionnaire_id);


--
-- Name: questionnaire_questions questionnaire_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.questionnaire_questions
    ADD CONSTRAINT questionnaire_questions_pkey PRIMARY KEY (id);


--
-- Name: role role_name_key; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.role
    ADD CONSTRAINT role_name_key UNIQUE (name);


--
-- Name: role role_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.role
    ADD CONSTRAINT role_pkey PRIMARY KEY (id);


--
-- Name: role role_role_id_key; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.role
    ADD CONSTRAINT role_role_id_key UNIQUE (role_id);


--
-- Name: status status_name_key; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.status
    ADD CONSTRAINT status_name_key UNIQUE (name);


--
-- Name: status status_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.status
    ADD CONSTRAINT status_pkey PRIMARY KEY (id);


--
-- Name: step_base_data step_base_data_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.step_base_data
    ADD CONSTRAINT step_base_data_pkey PRIMARY KEY (id);


--
-- Name: step step_name_key; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.step
    ADD CONSTRAINT step_name_key UNIQUE (name);


--
-- Name: step step_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.step
    ADD CONSTRAINT step_pkey PRIMARY KEY (id);


--
-- Name: step_questionnaire step_questionnaire_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.step_questionnaire
    ADD CONSTRAINT step_questionnaire_pkey PRIMARY KEY (id);


--
-- Name: subarea subarea_name_key; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.subarea
    ADD CONSTRAINT subarea_name_key UNIQUE (name);


--
-- Name: subarea subarea_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.subarea
    ADD CONSTRAINT subarea_pkey PRIMARY KEY (id);


--
-- Name: subject subject_name_key; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.subject
    ADD CONSTRAINT subject_name_key UNIQUE (name);


--
-- Name: subject subject_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.subject
    ADD CONSTRAINT subject_pkey PRIMARY KEY (id);


--
-- Name: table_base table_base_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.table_base
    ADD CONSTRAINT table_base_pkey PRIMARY KEY (id);


--
-- Name: table_gen table_gen_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.table_gen
    ADD CONSTRAINT table_gen_pkey PRIMARY KEY (id);


--
-- Name: table table_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public."table"
    ADD CONSTRAINT table_pkey PRIMARY KEY (id);


--
-- Name: task task_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.task
    ADD CONSTRAINT task_pkey PRIMARY KEY (id);


--
-- Name: test_table test_table_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.test_table
    ADD CONSTRAINT test_table_pkey PRIMARY KEY (id);


--
-- Name: ticket ticket_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.ticket
    ADD CONSTRAINT ticket_pkey PRIMARY KEY (id);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: workflow_base_data workflow_base_data_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.workflow_base_data
    ADD CONSTRAINT workflow_base_data_pkey PRIMARY KEY (id);


--
-- Name: workflow workflow_name_key; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.workflow
    ADD CONSTRAINT workflow_name_key UNIQUE (name);


--
-- Name: workflow workflow_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.workflow
    ADD CONSTRAINT workflow_pkey PRIMARY KEY (id);


--
-- Name: workflow_steps workflow_steps_pkey; Type: CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.workflow_steps
    ADD CONSTRAINT workflow_steps_pkey PRIMARY KEY (id);


--
-- Name: unique_three_key; Type: INDEX; Schema: public; Owner: aradulescu
--

CREATE INDEX unique_three_key ON public.step_base_data USING btree (base_data_id, workflow_id, step_id, status_id);


--
-- Name: answer answer_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.answer
    ADD CONSTRAINT answer_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.company(id);


--
-- Name: answer answer_company_id_fkey1; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.answer
    ADD CONSTRAINT answer_company_id_fkey1 FOREIGN KEY (company_id) REFERENCES public.company(id);


--
-- Name: answer answer_questionnaire_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.answer
    ADD CONSTRAINT answer_questionnaire_id_fkey FOREIGN KEY (questionnaire_id) REFERENCES public.questionnaire(id);


--
-- Name: answer answer_questionnaire_id_fkey1; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.answer
    ADD CONSTRAINT answer_questionnaire_id_fkey1 FOREIGN KEY (questionnaire_id) REFERENCES public.questionnaire(id);


--
-- Name: answer answer_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.answer
    ADD CONSTRAINT answer_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: answer answer_user_id_fkey1; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.answer
    ADD CONSTRAINT answer_user_id_fkey1 FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: area_subareas area_subareas_area_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.area_subareas
    ADD CONSTRAINT area_subareas_area_id_fkey FOREIGN KEY (area_id) REFERENCES public.area(id);


--
-- Name: area_subareas area_subareas_interval_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.area_subareas
    ADD CONSTRAINT area_subareas_interval_id_fkey FOREIGN KEY (interval_id) REFERENCES public."interval"(id);


--
-- Name: area_subareas area_subareas_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.area_subareas
    ADD CONSTRAINT area_subareas_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.status(id);


--
-- Name: area_subareas area_subareas_subarea_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.area_subareas
    ADD CONSTRAINT area_subareas_subarea_id_fkey FOREIGN KEY (subarea_id) REFERENCES public.subarea(id);


--
-- Name: audit_log audit_log_base_data_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_base_data_id_fkey FOREIGN KEY (base_data_id) REFERENCES public.base_data(id);


--
-- Name: audit_log audit_log_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.company(id);


--
-- Name: audit_log audit_log_step_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_step_id_fkey FOREIGN KEY (step_id) REFERENCES public.step(id);


--
-- Name: audit_log audit_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: audit_log audit_log_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow(id);


--
-- Name: base_data base_data_area_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.base_data
    ADD CONSTRAINT base_data_area_id_fkey FOREIGN KEY (area_id) REFERENCES public.area(id);


--
-- Name: base_data base_data_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.base_data
    ADD CONSTRAINT base_data_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.company(id);


--
-- Name: base_data base_data_interval_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.base_data
    ADD CONSTRAINT base_data_interval_id_fkey FOREIGN KEY (interval_id) REFERENCES public."interval"(id);


--
-- Name: base_data base_data_legal_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.base_data
    ADD CONSTRAINT base_data_legal_document_id_fkey FOREIGN KEY (legal_document_id) REFERENCES public.legal_document(id);


--
-- Name: base_data base_data_lexic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.base_data
    ADD CONSTRAINT base_data_lexic_id_fkey FOREIGN KEY (lexic_id) REFERENCES public.lexic(id);


--
-- Name: base_data base_data_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.base_data
    ADD CONSTRAINT base_data_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.status(id);


--
-- Name: base_data base_data_subarea_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.base_data
    ADD CONSTRAINT base_data_subarea_id_fkey FOREIGN KEY (subarea_id) REFERENCES public.subarea(id);


--
-- Name: base_data base_data_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.base_data
    ADD CONSTRAINT base_data_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subject(id);


--
-- Name: base_data base_data_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.base_data
    ADD CONSTRAINT base_data_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: company_users company_users_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.company_users
    ADD CONSTRAINT company_users_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.company(id);


--
-- Name: company_users company_users_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.company_users
    ADD CONSTRAINT company_users_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: deadline deadline_area_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.deadline
    ADD CONSTRAINT deadline_area_id_fkey FOREIGN KEY (area_id) REFERENCES public.area(id);


--
-- Name: deadline deadline_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.deadline
    ADD CONSTRAINT deadline_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.company(id);


--
-- Name: deadline deadline_interval_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.deadline
    ADD CONSTRAINT deadline_interval_id_fkey FOREIGN KEY (interval_id) REFERENCES public."interval"(id);


--
-- Name: deadline deadline_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.deadline
    ADD CONSTRAINT deadline_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.status(id);


--
-- Name: deadline deadline_subarea_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.deadline
    ADD CONSTRAINT deadline_subarea_id_fkey FOREIGN KEY (subarea_id) REFERENCES public.subarea(id);


--
-- Name: employee employee_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.company(id);


--
-- Name: possible_answers possible_answers_next_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.possible_answers
    ADD CONSTRAINT possible_answers_next_question_id_fkey FOREIGN KEY (next_question_id) REFERENCES public.question(id);


--
-- Name: post post_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.post
    ADD CONSTRAINT post_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.company(id);


--
-- Name: post post_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.post
    ADD CONSTRAINT post_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: questionnaire_companies questionnaire_companies_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.questionnaire_companies
    ADD CONSTRAINT questionnaire_companies_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.company(id);


--
-- Name: questionnaire_companies questionnaire_companies_questionnaire_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.questionnaire_companies
    ADD CONSTRAINT questionnaire_companies_questionnaire_id_fkey FOREIGN KEY (questionnaire_id) REFERENCES public.questionnaire(id);


--
-- Name: questionnaire_companies questionnaire_companies_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.questionnaire_companies
    ADD CONSTRAINT questionnaire_companies_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.status(id);


--
-- Name: questionnaire_questions questionnaire_questions_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.questionnaire_questions
    ADD CONSTRAINT questionnaire_questions_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.question(id);


--
-- Name: questionnaire_questions questionnaire_questions_questionnaire_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.questionnaire_questions
    ADD CONSTRAINT questionnaire_questions_questionnaire_id_fkey FOREIGN KEY (questionnaire_id) REFERENCES public.questionnaire(id);


--
-- Name: questionnaire questionnaire_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.questionnaire
    ADD CONSTRAINT questionnaire_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.status(id);


--
-- Name: step_base_data step_base_data_base_data_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.step_base_data
    ADD CONSTRAINT step_base_data_base_data_id_fkey FOREIGN KEY (base_data_id) REFERENCES public.base_data(id);


--
-- Name: step_base_data step_base_data_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.step_base_data
    ADD CONSTRAINT step_base_data_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.status(id);


--
-- Name: step_base_data step_base_data_step_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.step_base_data
    ADD CONSTRAINT step_base_data_step_id_fkey FOREIGN KEY (step_id) REFERENCES public.step(id);


--
-- Name: step_base_data step_base_data_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.step_base_data
    ADD CONSTRAINT step_base_data_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow(id);


--
-- Name: step step_next_step_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.step
    ADD CONSTRAINT step_next_step_id_fkey FOREIGN KEY (next_step_id) REFERENCES public.step(id);


--
-- Name: step_questionnaire step_questionnaire_questionnaire_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.step_questionnaire
    ADD CONSTRAINT step_questionnaire_questionnaire_id_fkey FOREIGN KEY (questionnaire_id) REFERENCES public.questionnaire(id);


--
-- Name: step_questionnaire step_questionnaire_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.step_questionnaire
    ADD CONSTRAINT step_questionnaire_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.status(id);


--
-- Name: step_questionnaire step_questionnaire_step_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.step_questionnaire
    ADD CONSTRAINT step_questionnaire_step_id_fkey FOREIGN KEY (step_id) REFERENCES public.step(id);


--
-- Name: step_questionnaire step_questionnaire_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.step_questionnaire
    ADD CONSTRAINT step_questionnaire_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow(id);


--
-- Name: table_base table_base_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.table_base
    ADD CONSTRAINT table_base_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.company(id);


--
-- Name: table_base table_base_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.table_base
    ADD CONSTRAINT table_base_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subject(id);


--
-- Name: table_base table_base_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.table_base
    ADD CONSTRAINT table_base_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: table_gen table_gen_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.table_gen
    ADD CONSTRAINT table_gen_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subject(id);


--
-- Name: table_gen table_gen_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.table_gen
    ADD CONSTRAINT table_gen_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: table table_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public."table"
    ADD CONSTRAINT table_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subject(id);


--
-- Name: table table_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public."table"
    ADD CONSTRAINT table_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: task task_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.task
    ADD CONSTRAINT task_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow(id);


--
-- Name: ticket ticket_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.ticket
    ADD CONSTRAINT ticket_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.subject(id);


--
-- Name: ticket ticket_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.ticket
    ADD CONSTRAINT ticket_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subject(id);


--
-- Name: ticket ticket_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.ticket
    ADD CONSTRAINT ticket_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_roles user_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.role(id);


--
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: workflow_base_data workflow_base_data_base_data_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.workflow_base_data
    ADD CONSTRAINT workflow_base_data_base_data_id_fkey FOREIGN KEY (base_data_id) REFERENCES public.base_data(id);


--
-- Name: workflow_base_data workflow_base_data_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.workflow_base_data
    ADD CONSTRAINT workflow_base_data_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow(id);


--
-- Name: workflow_steps workflow_steps_step_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.workflow_steps
    ADD CONSTRAINT workflow_steps_step_id_fkey FOREIGN KEY (step_id) REFERENCES public.step(id);


--
-- Name: workflow_steps workflow_steps_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aradulescu
--

ALTER TABLE ONLY public.workflow_steps
    ADD CONSTRAINT workflow_steps_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow(id);


--
-- PostgreSQL database dump complete
--

