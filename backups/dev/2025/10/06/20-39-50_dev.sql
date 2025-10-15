--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2 (Debian 17.2-1.pgdg120+1)
-- Dumped by pg_dump version 17.2 (Debian 17.2-1.pgdg120+1)

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

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

-- *not* creating schema, since initdb creates it


--
-- Name: btree_gin; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS btree_gin WITH SCHEMA public;


--
-- Name: EXTENSION btree_gin; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION btree_gin IS 'support for indexing common datatypes in GIN';


--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: age_court_restrictions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.age_court_restrictions (
    age_court_restriction_id integer NOT NULL,
    round_setting_id integer NOT NULL,
    age_id integer NOT NULL,
    court_time_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL
);


--
-- Name: age_court_restrictions_age_court_restriction_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.age_court_restrictions_age_court_restriction_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: age_court_restrictions_age_court_restriction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.age_court_restrictions_age_court_restriction_id_seq OWNED BY public.age_court_restrictions.age_court_restriction_id;


--
-- Name: age_round_constraints; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.age_round_constraints (
    age_round_constraint_id integer NOT NULL,
    round_setting_id integer NOT NULL,
    age_id integer NOT NULL,
    active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL
);


--
-- Name: age_round_constraints_age_round_constraint_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.age_round_constraints_age_round_constraint_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: age_round_constraints_age_round_constraint_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.age_round_constraints_age_round_constraint_id_seq OWNED BY public.age_round_constraints.age_round_constraint_id;


--
-- Name: ages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ages (
    age_id integer NOT NULL,
    season_day_id integer NOT NULL,
    age_code character varying(20) NOT NULL,
    age_name text NOT NULL,
    gender text,
    age_rank integer NOT NULL,
    age_required_games integer,
    active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL
);


--
-- Name: ages_age_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ages_age_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ages_age_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ages_age_id_seq OWNED BY public.ages.age_id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: allocation_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.allocation_settings (
    allocation_setting_id integer NOT NULL,
    round_setting_id integer NOT NULL,
    age_id integer NOT NULL,
    grade_id integer NOT NULL,
    restricted boolean DEFAULT false,
    restriction_type text DEFAULT 'NONE'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL,
    updated_at timestamp with time zone,
    updated_by_user_id integer,
    CONSTRAINT ck_allocation_settings_chk_allocation_settings_restriction_type CHECK ((restriction_type = ANY (ARRAY['NONE'::text, 'AGE'::text, 'GRADE'::text, 'DUAL'::text])))
);


--
-- Name: allocation_settings_allocation_setting_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.allocation_settings_allocation_setting_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: allocation_settings_allocation_setting_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.allocation_settings_allocation_setting_id_seq OWNED BY public.allocation_settings.allocation_setting_id;


--
-- Name: competitions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.competitions (
    competition_id integer NOT NULL,
    organisation_id integer NOT NULL,
    competition_name text NOT NULL,
    active boolean DEFAULT true,
    slug character varying(64) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL
);


--
-- Name: competitions_competition_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.competitions_competition_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: competitions_competition_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.competitions_competition_id_seq OWNED BY public.competitions.competition_id;


--
-- Name: court_rankings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.court_rankings (
    court_rank_id integer NOT NULL,
    court_id integer NOT NULL,
    season_day_id integer NOT NULL,
    round_setting_id integer NOT NULL,
    court_rank integer NOT NULL,
    overridden boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL,
    updated_at timestamp with time zone,
    updated_by_user_id integer
);


--
-- Name: court_rankings_court_rank_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.court_rankings_court_rank_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: court_rankings_court_rank_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.court_rankings_court_rank_id_seq OWNED BY public.court_rankings.court_rank_id;


--
-- Name: court_times; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.court_times (
    court_time_id integer NOT NULL,
    season_day_id integer NOT NULL,
    round_setting_id integer NOT NULL,
    court_id integer NOT NULL,
    time_slot_id integer NOT NULL,
    availability_status text DEFAULT 'AVAILABLE'::text NOT NULL,
    lock_state text DEFAULT 'OPEN'::text NOT NULL,
    block_reason text,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL,
    updated_at timestamp with time zone,
    updated_by_user_id integer
);


--
-- Name: court_times_court_time_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.court_times_court_time_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: court_times_court_time_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.court_times_court_time_id_seq OWNED BY public.court_times.court_time_id;


--
-- Name: courts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.courts (
    court_id integer NOT NULL,
    venue_id integer NOT NULL,
    court_code character varying(20) NOT NULL,
    court_name text NOT NULL,
    display_order integer NOT NULL,
    surface text,
    indoor boolean DEFAULT true,
    active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL
);


--
-- Name: courts_court_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.courts_court_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: courts_court_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.courts_court_id_seq OWNED BY public.courts.court_id;


--
-- Name: dates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dates (
    date_id integer NOT NULL,
    date_value date NOT NULL,
    date_day text NOT NULL,
    calendar_year integer NOT NULL,
    iso_week_int integer NOT NULL,
    is_weekend boolean NOT NULL,
    is_public_holiday boolean NOT NULL
);


--
-- Name: dates_date_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.dates_date_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dates_date_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.dates_date_id_seq OWNED BY public.dates.date_id;


--
-- Name: default_times; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.default_times (
    time_id integer NOT NULL,
    time_value time without time zone NOT NULL
);


--
-- Name: default_times_time_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.default_times_time_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: default_times_time_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.default_times_time_id_seq OWNED BY public.default_times.time_id;


--
-- Name: final_bye_schedule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.final_bye_schedule (
    final_bye_schedule_id integer NOT NULL,
    run_id integer NOT NULL,
    round_id integer NOT NULL,
    age_id integer NOT NULL,
    grade_id integer NOT NULL,
    team_id integer NOT NULL,
    bye_date date NOT NULL,
    bye_name text NOT NULL,
    organisation_name text NOT NULL,
    competition_name text NOT NULL,
    season_name text NOT NULL,
    gender text,
    age_name text NOT NULL,
    grade_name text NOT NULL,
    team_name text NOT NULL,
    bye_reason text NOT NULL,
    published_at timestamp with time zone,
    published_by_user_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL,
    CONSTRAINT ck_final_bye_schedule_chk_final_byes_reason CHECK ((bye_reason = ANY (ARRAY['ODD_TEAMS'::text, 'ERROR_LOOP'::text, 'CONSTRAINT'::text, 'MANUAL_OVERRIDE'::text])))
);


--
-- Name: final_bye_schedule_final_bye_schedule_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.final_bye_schedule_final_bye_schedule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: final_bye_schedule_final_bye_schedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.final_bye_schedule_final_bye_schedule_id_seq OWNED BY public.final_bye_schedule.final_bye_schedule_id;


--
-- Name: final_game_schedule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.final_game_schedule (
    final_game_schedule_id integer NOT NULL,
    run_id integer NOT NULL,
    round_id integer NOT NULL,
    age_id integer NOT NULL,
    grade_id integer NOT NULL,
    team_a_id integer NOT NULL,
    team_b_id integer NOT NULL,
    court_time_id integer NOT NULL,
    game_date date NOT NULL,
    game_name text NOT NULL,
    organisation_name text NOT NULL,
    competition_name text NOT NULL,
    season_name text NOT NULL,
    gender text,
    venue_name text NOT NULL,
    court_name text NOT NULL,
    start_time time without time zone NOT NULL,
    age_name text NOT NULL,
    grade_name text NOT NULL,
    team_a_name text NOT NULL,
    team_b_name text NOT NULL,
    game_status text DEFAULT 'FINALISED'::text,
    published_at timestamp with time zone,
    published_by_user_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL,
    CONSTRAINT ck_final_game_schedule_chk_final_games_game_status CHECK (((game_status IS NULL) OR (game_status = ANY (ARRAY['FINALISED'::text, 'CANCELLED'::text, 'FORFEITED'::text, 'COMPLETED'::text]))))
);


--
-- Name: final_game_schedule_final_game_schedule_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.final_game_schedule_final_game_schedule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: final_game_schedule_final_game_schedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.final_game_schedule_final_game_schedule_id_seq OWNED BY public.final_game_schedule.final_game_schedule_id;


--
-- Name: grade_court_restrictions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.grade_court_restrictions (
    grade_court_restriction_id integer NOT NULL,
    round_setting_id integer NOT NULL,
    grade_id integer NOT NULL,
    court_time_id integer NOT NULL,
    restriction_type text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL,
    CONSTRAINT ck_grade_court_restrictions_chk_grade_court_restrictions_type CHECK ((restriction_type = ANY (ARRAY['GRADE'::text, 'DUAL'::text])))
);


--
-- Name: grade_court_restrictions_grade_court_restriction_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.grade_court_restrictions_grade_court_restriction_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: grade_court_restrictions_grade_court_restriction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.grade_court_restrictions_grade_court_restriction_id_seq OWNED BY public.grade_court_restrictions.grade_court_restriction_id;


--
-- Name: grade_round_constraints; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.grade_round_constraints (
    grade_round_constraint_id integer NOT NULL,
    round_setting_id integer NOT NULL,
    age_id integer NOT NULL,
    grade_id integer NOT NULL,
    active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL
);


--
-- Name: grade_round_constraints_grade_round_constraint_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.grade_round_constraints_grade_round_constraint_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: grade_round_constraints_grade_round_constraint_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.grade_round_constraints_grade_round_constraint_id_seq OWNED BY public.grade_round_constraints.grade_round_constraint_id;


--
-- Name: grades; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.grades (
    grade_id integer NOT NULL,
    age_id integer NOT NULL,
    grade_code character varying(20) NOT NULL,
    grade_name text NOT NULL,
    grade_rank integer NOT NULL,
    grade_required_games integer,
    bye_requirement boolean DEFAULT false,
    active boolean DEFAULT true,
    display_colour text,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL
);


--
-- Name: grades_grade_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.grades_grade_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: grades_grade_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.grades_grade_id_seq OWNED BY public.grades.grade_id;


--
-- Name: organisations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.organisations (
    organisation_id integer NOT NULL,
    organisation_name text NOT NULL,
    time_zone text,
    country_code text,
    slug character varying(64) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL
);


--
-- Name: organisations_organisation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.organisations_organisation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: organisations_organisation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.organisations_organisation_id_seq OWNED BY public.organisations.organisation_id;


--
-- Name: p2_allocations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.p2_allocations (
    p2_allocation_id integer NOT NULL,
    run_id integer NOT NULL,
    round_id integer NOT NULL,
    age_id integer NOT NULL,
    grade_id integer NOT NULL,
    court_time_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL
);


--
-- Name: p2_allocations_p2_allocation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.p2_allocations_p2_allocation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: p2_allocations_p2_allocation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.p2_allocations_p2_allocation_id_seq OWNED BY public.p2_allocations.p2_allocation_id;


--
-- Name: p3_bye_allocations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.p3_bye_allocations (
    p3_bye_allocation_id integer NOT NULL,
    run_id integer NOT NULL,
    round_id integer NOT NULL,
    age_id integer NOT NULL,
    grade_id integer NOT NULL,
    team_id integer NOT NULL,
    bye_reason text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL,
    CONSTRAINT ck_p3_bye_allocations_chk_p3_byes_reason CHECK ((bye_reason = ANY (ARRAY['ODD_TEAMS'::text, 'ERROR_LOOP'::text, 'CONSTRAINT'::text, 'MANUAL_OVERRIDE'::text])))
);


--
-- Name: p3_bye_allocations_p3_bye_allocation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.p3_bye_allocations_p3_bye_allocation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: p3_bye_allocations_p3_bye_allocation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.p3_bye_allocations_p3_bye_allocation_id_seq OWNED BY public.p3_bye_allocations.p3_bye_allocation_id;


--
-- Name: p3_game_allocations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.p3_game_allocations (
    p3_game_allocation_id integer NOT NULL,
    run_id integer NOT NULL,
    p2_allocation_id integer,
    round_id integer NOT NULL,
    age_id integer NOT NULL,
    grade_id integer NOT NULL,
    team_a_id integer NOT NULL,
    team_b_id integer NOT NULL,
    court_time_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL
);


--
-- Name: p3_game_allocations_p3_game_allocation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.p3_game_allocations_p3_game_allocation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: p3_game_allocations_p3_game_allocation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.p3_game_allocations_p3_game_allocation_id_seq OWNED BY public.p3_game_allocations.p3_game_allocation_id;


--
-- Name: public_holidays; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.public_holidays (
    public_holiday_id integer NOT NULL,
    date_id integer NOT NULL,
    holiday_name text NOT NULL,
    holiday_region text NOT NULL
);


--
-- Name: public_holidays_public_holiday_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.public_holidays_public_holiday_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: public_holidays_public_holiday_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.public_holidays_public_holiday_id_seq OWNED BY public.public_holidays.public_holiday_id;


--
-- Name: round_dates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.round_dates (
    round_date_id integer NOT NULL,
    date_id integer NOT NULL,
    round_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL
);


--
-- Name: round_dates_round_date_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.round_dates_round_date_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: round_dates_round_date_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.round_dates_round_date_id_seq OWNED BY public.round_dates.round_date_id;


--
-- Name: round_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.round_groups (
    round_group_id integer NOT NULL,
    round_id integer NOT NULL,
    round_setting_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL
);


--
-- Name: round_groups_round_group_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.round_groups_round_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: round_groups_round_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.round_groups_round_group_id_seq OWNED BY public.round_groups.round_group_id;


--
-- Name: round_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.round_settings (
    round_setting_id integer NOT NULL,
    season_day_id integer NOT NULL,
    round_settings_number integer NOT NULL,
    rules jsonb,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL
);


--
-- Name: round_settings_round_setting_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.round_settings_round_setting_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: round_settings_round_setting_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.round_settings_round_setting_id_seq OWNED BY public.round_settings.round_setting_id;


--
-- Name: rounds; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rounds (
    round_id integer NOT NULL,
    season_id integer NOT NULL,
    round_number integer NOT NULL,
    round_label text NOT NULL,
    round_type text NOT NULL,
    round_status text DEFAULT 'PLANNED'::text NOT NULL,
    published_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL,
    CONSTRAINT ck_rounds_chk_rounds_round_status CHECK ((round_status = ANY (ARRAY['PLANNED'::text, 'SCHEDULED'::text, 'PUBLISHED'::text, 'COMPLETED'::text, 'CANCELLED'::text]))),
    CONSTRAINT ck_rounds_chk_rounds_round_type CHECK ((round_type = ANY (ARRAY['GRADING'::text, 'REGULAR'::text, 'FINALS'::text])))
);


--
-- Name: rounds_round_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.rounds_round_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: rounds_round_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.rounds_round_id_seq OWNED BY public.rounds.round_id;


--
-- Name: run_constraints_snapshot; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.run_constraints_snapshot (
    snapshot_id integer NOT NULL,
    run_id integer NOT NULL,
    phase text NOT NULL,
    constraints_json jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT ck_run_constraints_snapshot_chk_run_constraints_snapshot_phase CHECK ((phase = ANY (ARRAY['P2'::text, 'P3'::text, 'COMPOSITE'::text])))
);


--
-- Name: run_constraints_snapshot_snapshot_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.run_constraints_snapshot_snapshot_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: run_constraints_snapshot_snapshot_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.run_constraints_snapshot_snapshot_id_seq OWNED BY public.run_constraints_snapshot.snapshot_id;


--
-- Name: run_exports; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.run_exports (
    export_id integer NOT NULL,
    run_id integer NOT NULL,
    export_type text NOT NULL,
    file_path text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT ck_run_exports_chk_run_exports_export_type CHECK ((export_type = ANY (ARRAY['CSV'::text, 'PDF'::text, 'ZIP'::text, 'XLSX'::text])))
);


--
-- Name: run_exports_export_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.run_exports_export_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: run_exports_export_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.run_exports_export_id_seq OWNED BY public.run_exports.export_id;


--
-- Name: saved_byes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.saved_byes (
    saved_bye_id integer NOT NULL,
    run_id integer NOT NULL,
    round_id integer NOT NULL,
    age_id integer NOT NULL,
    grade_id integer NOT NULL,
    team_id integer NOT NULL,
    bye_reason text,
    game_status text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL,
    CONSTRAINT ck_saved_byes_chk_saved_byes_bye_reason CHECK (((bye_reason IS NULL) OR (bye_reason = ANY (ARRAY['ODD_TEAMS'::text, 'ERROR_LOOP'::text, 'CONSTRAINT'::text, 'MANUAL_OVERRIDE'::text])))),
    CONSTRAINT ck_saved_byes_chk_saved_byes_game_status CHECK ((game_status = ANY (ARRAY['AFTER_P2_BEFORE_P3'::text, 'AFTER_P3_BEFORE_FINALISE'::text, 'FINALISED'::text])))
);


--
-- Name: saved_byes_saved_bye_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.saved_byes_saved_bye_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: saved_byes_saved_bye_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.saved_byes_saved_bye_id_seq OWNED BY public.saved_byes.saved_bye_id;


--
-- Name: saved_games; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.saved_games (
    saved_game_id integer NOT NULL,
    run_id integer NOT NULL,
    round_id integer NOT NULL,
    age_id integer NOT NULL,
    grade_id integer NOT NULL,
    team_a_id integer NOT NULL,
    team_b_id integer NOT NULL,
    court_time_id integer NOT NULL,
    game_status text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL,
    CONSTRAINT ck_saved_games_chk_saved_games_game_status CHECK ((game_status = ANY (ARRAY['AFTER_P2_BEFORE_P3'::text, 'AFTER_P3_BEFORE_FINALISE'::text, 'FINALISED'::text])))
);


--
-- Name: saved_games_saved_game_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.saved_games_saved_game_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: saved_games_saved_game_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.saved_games_saved_game_id_seq OWNED BY public.saved_games.saved_game_id;


--
-- Name: scheduling_locks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.scheduling_locks (
    lock_id integer NOT NULL,
    season_day_id integer NOT NULL,
    run_id integer NOT NULL,
    locked_at timestamp with time zone DEFAULT now(),
    locked_by_user_id integer NOT NULL
);


--
-- Name: scheduling_locks_lock_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.scheduling_locks_lock_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: scheduling_locks_lock_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.scheduling_locks_lock_id_seq OWNED BY public.scheduling_locks.lock_id;


--
-- Name: scheduling_run_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.scheduling_run_events (
    event_id integer NOT NULL,
    run_id integer NOT NULL,
    event_time timestamp with time zone DEFAULT now(),
    stage text NOT NULL,
    severity text NOT NULL,
    event_message text NOT NULL,
    context jsonb,
    CONSTRAINT ck_scheduling_run_events_chk_run_events_severity CHECK ((severity = ANY (ARRAY['INFO'::text, 'WARN'::text, 'ERROR'::text]))),
    CONSTRAINT ck_scheduling_run_events_chk_run_events_stage CHECK ((stage = ANY (ARRAY['STEP1'::text, 'STEP2'::text, 'STEP3'::text, 'STEP4'::text, 'STEP5'::text, 'FINALISE'::text])))
);


--
-- Name: scheduling_run_events_event_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.scheduling_run_events_event_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: scheduling_run_events_event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.scheduling_run_events_event_id_seq OWNED BY public.scheduling_run_events.event_id;


--
-- Name: scheduling_runs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.scheduling_runs (
    run_id integer NOT NULL,
    season_id integer NOT NULL,
    season_day_id integer NOT NULL,
    run_status text NOT NULL,
    process_type text NOT NULL,
    run_type text,
    s1_check_results text NOT NULL,
    round_ids jsonb NOT NULL,
    seed_master text NOT NULL,
    resume_checkpoint text NOT NULL,
    config_hash text,
    idempotency_key text NOT NULL,
    metrics jsonb,
    error_code text,
    error_details jsonb,
    started_at timestamp with time zone,
    finished_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL,
    CONSTRAINT ck_scheduling_runs_chk_scheduling_runs_process_type CHECK ((process_type = ANY (ARRAY['INITIAL'::text, 'MID'::text]))),
    CONSTRAINT ck_scheduling_runs_chk_scheduling_runs_resume_checkpoint CHECK ((resume_checkpoint = ANY (ARRAY['BEFORE_P2'::text, 'AFTER_P2_BEFORE_P3'::text, 'AFTER_P3_BEFORE_FINALISE'::text, 'FINALISED'::text]))),
    CONSTRAINT ck_scheduling_runs_chk_scheduling_runs_run_status CHECK ((run_status = ANY (ARRAY['PENDING'::text, 'RUNNING'::text, 'FAILED'::text, 'SUCCEEDED'::text, 'ABANDONED'::text]))),
    CONSTRAINT ck_scheduling_runs_chk_scheduling_runs_run_type CHECK (((run_type IS NULL) OR (run_type = ANY (ARRAY['I_RUN_1'::text, 'I_RUN_2'::text, 'M_RUN_1'::text, 'M_RUN_2'::text, 'M_RUN_3'::text]))))
);


--
-- Name: scheduling_runs_run_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.scheduling_runs_run_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: scheduling_runs_run_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.scheduling_runs_run_id_seq OWNED BY public.scheduling_runs.run_id;


--
-- Name: season_days; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.season_days (
    season_day_id integer NOT NULL,
    season_id integer NOT NULL,
    season_day_name text NOT NULL,
    season_day_label text,
    week_day integer NOT NULL,
    window_start time without time zone NOT NULL,
    window_end time without time zone NOT NULL,
    active boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL,
    CONSTRAINT ck_season_days_chk_season_days_week_day_range CHECK (((week_day >= 1) AND (week_day <= 7)))
);


--
-- Name: season_days_season_day_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.season_days_season_day_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: season_days_season_day_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.season_days_season_day_id_seq OWNED BY public.season_days.season_day_id;


--
-- Name: seasons; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.seasons (
    season_id integer NOT NULL,
    competition_id integer NOT NULL,
    season_name text NOT NULL,
    starting_date date,
    ending_date date,
    visibility text NOT NULL,
    active boolean DEFAULT true,
    slug character varying(64) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL
);


--
-- Name: seasons_season_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.seasons_season_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: seasons_season_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.seasons_season_id_seq OWNED BY public.seasons.season_id;


--
-- Name: staging_diffs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.staging_diffs (
    diff_id integer NOT NULL,
    run_id integer NOT NULL,
    entity_type text NOT NULL,
    entity_id text NOT NULL,
    change_type text NOT NULL,
    before_json jsonb,
    after_json jsonb,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL,
    CONSTRAINT ck_staging_diffs_chk_staging_diffs_change_type CHECK ((change_type = ANY (ARRAY['ADD'::text, 'CHANGE'::text, 'REMOVE'::text]))),
    CONSTRAINT ck_staging_diffs_chk_staging_diffs_entity_type CHECK ((entity_type = ANY (ARRAY['P2_ALLOCATION'::text, 'P3_ALLOCATION'::text, 'COMPOSITE_ALLOCATION'::text])))
);


--
-- Name: staging_diffs_diff_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.staging_diffs_diff_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: staging_diffs_diff_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.staging_diffs_diff_id_seq OWNED BY public.staging_diffs.diff_id;


--
-- Name: teams; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.teams (
    team_id integer NOT NULL,
    grade_id integer NOT NULL,
    team_code character varying(20) NOT NULL,
    team_name text,
    active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL
);


--
-- Name: teams_team_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.teams_team_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: teams_team_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.teams_team_id_seq OWNED BY public.teams.team_id;


--
-- Name: time_slots; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.time_slots (
    time_slot_id integer NOT NULL,
    season_day_id integer NOT NULL,
    start_time_id integer NOT NULL,
    end_time_id integer NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    time_slot_label text NOT NULL,
    buffer_minutes integer NOT NULL,
    duration_minutes integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL
);


--
-- Name: time_slots_time_slot_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.time_slots_time_slot_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: time_slots_time_slot_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.time_slots_time_slot_id_seq OWNED BY public.time_slots.time_slot_id;


--
-- Name: user_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_permissions (
    permission_id integer NOT NULL,
    user_account_id integer NOT NULL,
    organisation_id integer NOT NULL,
    can_schedule boolean DEFAULT true NOT NULL,
    can_approve boolean DEFAULT true NOT NULL,
    can_export boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: user_permissions_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_permissions_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_permissions_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_permissions_permission_id_seq OWNED BY public.user_permissions.permission_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    user_account_id integer NOT NULL,
    display_name text NOT NULL,
    email text NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: users_user_account_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_user_account_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_user_account_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_user_account_id_seq OWNED BY public.users.user_account_id;


--
-- Name: venues; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.venues (
    venue_id integer NOT NULL,
    organisation_id integer NOT NULL,
    venue_name text NOT NULL,
    venue_address text NOT NULL,
    display_order integer NOT NULL,
    latitude numeric(9,6),
    longitude numeric(9,6),
    indoor boolean DEFAULT true,
    accessible boolean DEFAULT true,
    total_courts integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    created_by_user_id integer NOT NULL
);


--
-- Name: venues_venue_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.venues_venue_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: venues_venue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.venues_venue_id_seq OWNED BY public.venues.venue_id;


--
-- Name: age_court_restrictions age_court_restriction_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.age_court_restrictions ALTER COLUMN age_court_restriction_id SET DEFAULT nextval('public.age_court_restrictions_age_court_restriction_id_seq'::regclass);


--
-- Name: age_round_constraints age_round_constraint_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.age_round_constraints ALTER COLUMN age_round_constraint_id SET DEFAULT nextval('public.age_round_constraints_age_round_constraint_id_seq'::regclass);


--
-- Name: ages age_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ages ALTER COLUMN age_id SET DEFAULT nextval('public.ages_age_id_seq'::regclass);


--
-- Name: allocation_settings allocation_setting_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.allocation_settings ALTER COLUMN allocation_setting_id SET DEFAULT nextval('public.allocation_settings_allocation_setting_id_seq'::regclass);


--
-- Name: competitions competition_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.competitions ALTER COLUMN competition_id SET DEFAULT nextval('public.competitions_competition_id_seq'::regclass);


--
-- Name: court_rankings court_rank_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.court_rankings ALTER COLUMN court_rank_id SET DEFAULT nextval('public.court_rankings_court_rank_id_seq'::regclass);


--
-- Name: court_times court_time_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.court_times ALTER COLUMN court_time_id SET DEFAULT nextval('public.court_times_court_time_id_seq'::regclass);


--
-- Name: courts court_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courts ALTER COLUMN court_id SET DEFAULT nextval('public.courts_court_id_seq'::regclass);


--
-- Name: dates date_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dates ALTER COLUMN date_id SET DEFAULT nextval('public.dates_date_id_seq'::regclass);


--
-- Name: default_times time_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.default_times ALTER COLUMN time_id SET DEFAULT nextval('public.default_times_time_id_seq'::regclass);


--
-- Name: final_bye_schedule final_bye_schedule_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_bye_schedule ALTER COLUMN final_bye_schedule_id SET DEFAULT nextval('public.final_bye_schedule_final_bye_schedule_id_seq'::regclass);


--
-- Name: final_game_schedule final_game_schedule_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_game_schedule ALTER COLUMN final_game_schedule_id SET DEFAULT nextval('public.final_game_schedule_final_game_schedule_id_seq'::regclass);


--
-- Name: grade_court_restrictions grade_court_restriction_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grade_court_restrictions ALTER COLUMN grade_court_restriction_id SET DEFAULT nextval('public.grade_court_restrictions_grade_court_restriction_id_seq'::regclass);


--
-- Name: grade_round_constraints grade_round_constraint_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grade_round_constraints ALTER COLUMN grade_round_constraint_id SET DEFAULT nextval('public.grade_round_constraints_grade_round_constraint_id_seq'::regclass);


--
-- Name: grades grade_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grades ALTER COLUMN grade_id SET DEFAULT nextval('public.grades_grade_id_seq'::regclass);


--
-- Name: organisations organisation_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.organisations ALTER COLUMN organisation_id SET DEFAULT nextval('public.organisations_organisation_id_seq'::regclass);


--
-- Name: p2_allocations p2_allocation_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p2_allocations ALTER COLUMN p2_allocation_id SET DEFAULT nextval('public.p2_allocations_p2_allocation_id_seq'::regclass);


--
-- Name: p3_bye_allocations p3_bye_allocation_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_bye_allocations ALTER COLUMN p3_bye_allocation_id SET DEFAULT nextval('public.p3_bye_allocations_p3_bye_allocation_id_seq'::regclass);


--
-- Name: p3_game_allocations p3_game_allocation_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_game_allocations ALTER COLUMN p3_game_allocation_id SET DEFAULT nextval('public.p3_game_allocations_p3_game_allocation_id_seq'::regclass);


--
-- Name: public_holidays public_holiday_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.public_holidays ALTER COLUMN public_holiday_id SET DEFAULT nextval('public.public_holidays_public_holiday_id_seq'::regclass);


--
-- Name: round_dates round_date_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_dates ALTER COLUMN round_date_id SET DEFAULT nextval('public.round_dates_round_date_id_seq'::regclass);


--
-- Name: round_groups round_group_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_groups ALTER COLUMN round_group_id SET DEFAULT nextval('public.round_groups_round_group_id_seq'::regclass);


--
-- Name: round_settings round_setting_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_settings ALTER COLUMN round_setting_id SET DEFAULT nextval('public.round_settings_round_setting_id_seq'::regclass);


--
-- Name: rounds round_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rounds ALTER COLUMN round_id SET DEFAULT nextval('public.rounds_round_id_seq'::regclass);


--
-- Name: run_constraints_snapshot snapshot_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.run_constraints_snapshot ALTER COLUMN snapshot_id SET DEFAULT nextval('public.run_constraints_snapshot_snapshot_id_seq'::regclass);


--
-- Name: run_exports export_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.run_exports ALTER COLUMN export_id SET DEFAULT nextval('public.run_exports_export_id_seq'::regclass);


--
-- Name: saved_byes saved_bye_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_byes ALTER COLUMN saved_bye_id SET DEFAULT nextval('public.saved_byes_saved_bye_id_seq'::regclass);


--
-- Name: saved_games saved_game_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_games ALTER COLUMN saved_game_id SET DEFAULT nextval('public.saved_games_saved_game_id_seq'::regclass);


--
-- Name: scheduling_locks lock_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduling_locks ALTER COLUMN lock_id SET DEFAULT nextval('public.scheduling_locks_lock_id_seq'::regclass);


--
-- Name: scheduling_run_events event_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduling_run_events ALTER COLUMN event_id SET DEFAULT nextval('public.scheduling_run_events_event_id_seq'::regclass);


--
-- Name: scheduling_runs run_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduling_runs ALTER COLUMN run_id SET DEFAULT nextval('public.scheduling_runs_run_id_seq'::regclass);


--
-- Name: season_days season_day_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.season_days ALTER COLUMN season_day_id SET DEFAULT nextval('public.season_days_season_day_id_seq'::regclass);


--
-- Name: seasons season_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.seasons ALTER COLUMN season_id SET DEFAULT nextval('public.seasons_season_id_seq'::regclass);


--
-- Name: staging_diffs diff_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staging_diffs ALTER COLUMN diff_id SET DEFAULT nextval('public.staging_diffs_diff_id_seq'::regclass);


--
-- Name: teams team_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teams ALTER COLUMN team_id SET DEFAULT nextval('public.teams_team_id_seq'::regclass);


--
-- Name: time_slots time_slot_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_slots ALTER COLUMN time_slot_id SET DEFAULT nextval('public.time_slots_time_slot_id_seq'::regclass);


--
-- Name: user_permissions permission_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_permissions ALTER COLUMN permission_id SET DEFAULT nextval('public.user_permissions_permission_id_seq'::regclass);


--
-- Name: users user_account_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN user_account_id SET DEFAULT nextval('public.users_user_account_id_seq'::regclass);


--
-- Name: venues venue_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.venues ALTER COLUMN venue_id SET DEFAULT nextval('public.venues_venue_id_seq'::regclass);


--
-- Data for Name: age_court_restrictions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.age_court_restrictions (age_court_restriction_id, round_setting_id, age_id, court_time_id, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: age_round_constraints; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.age_round_constraints (age_round_constraint_id, round_setting_id, age_id, active, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: ages; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ages (age_id, season_day_id, age_code, age_name, gender, age_rank, age_required_games, active, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
ddc1645c7dfa
\.


--
-- Data for Name: allocation_settings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.allocation_settings (allocation_setting_id, round_setting_id, age_id, grade_id, restricted, restriction_type, created_at, created_by_user_id, updated_at, updated_by_user_id) FROM stdin;
\.


--
-- Data for Name: competitions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.competitions (competition_id, organisation_id, competition_name, active, slug, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: court_rankings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.court_rankings (court_rank_id, court_id, season_day_id, round_setting_id, court_rank, overridden, created_at, created_by_user_id, updated_at, updated_by_user_id) FROM stdin;
\.


--
-- Data for Name: court_times; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.court_times (court_time_id, season_day_id, round_setting_id, court_id, time_slot_id, availability_status, lock_state, block_reason, created_at, created_by_user_id, updated_at, updated_by_user_id) FROM stdin;
\.


--
-- Data for Name: courts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.courts (court_id, venue_id, court_code, court_name, display_order, surface, indoor, active, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: dates; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dates (date_id, date_value, date_day, calendar_year, iso_week_int, is_weekend, is_public_holiday) FROM stdin;
\.


--
-- Data for Name: default_times; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.default_times (time_id, time_value) FROM stdin;
\.


--
-- Data for Name: final_bye_schedule; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.final_bye_schedule (final_bye_schedule_id, run_id, round_id, age_id, grade_id, team_id, bye_date, bye_name, organisation_name, competition_name, season_name, gender, age_name, grade_name, team_name, bye_reason, published_at, published_by_user_id, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: final_game_schedule; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.final_game_schedule (final_game_schedule_id, run_id, round_id, age_id, grade_id, team_a_id, team_b_id, court_time_id, game_date, game_name, organisation_name, competition_name, season_name, gender, venue_name, court_name, start_time, age_name, grade_name, team_a_name, team_b_name, game_status, published_at, published_by_user_id, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: grade_court_restrictions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.grade_court_restrictions (grade_court_restriction_id, round_setting_id, grade_id, court_time_id, restriction_type, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: grade_round_constraints; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.grade_round_constraints (grade_round_constraint_id, round_setting_id, age_id, grade_id, active, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: grades; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.grades (grade_id, age_id, grade_code, grade_name, grade_rank, grade_required_games, bye_requirement, active, display_colour, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: organisations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.organisations (organisation_id, organisation_name, time_zone, country_code, slug, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: p2_allocations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.p2_allocations (p2_allocation_id, run_id, round_id, age_id, grade_id, court_time_id, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: p3_bye_allocations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.p3_bye_allocations (p3_bye_allocation_id, run_id, round_id, age_id, grade_id, team_id, bye_reason, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: p3_game_allocations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.p3_game_allocations (p3_game_allocation_id, run_id, p2_allocation_id, round_id, age_id, grade_id, team_a_id, team_b_id, court_time_id, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: public_holidays; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.public_holidays (public_holiday_id, date_id, holiday_name, holiday_region) FROM stdin;
\.


--
-- Data for Name: round_dates; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.round_dates (round_date_id, date_id, round_id, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: round_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.round_groups (round_group_id, round_id, round_setting_id, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: round_settings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.round_settings (round_setting_id, season_day_id, round_settings_number, rules, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: rounds; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.rounds (round_id, season_id, round_number, round_label, round_type, round_status, published_at, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: run_constraints_snapshot; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.run_constraints_snapshot (snapshot_id, run_id, phase, constraints_json, created_at) FROM stdin;
\.


--
-- Data for Name: run_exports; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.run_exports (export_id, run_id, export_type, file_path, created_at) FROM stdin;
\.


--
-- Data for Name: saved_byes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.saved_byes (saved_bye_id, run_id, round_id, age_id, grade_id, team_id, bye_reason, game_status, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: saved_games; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.saved_games (saved_game_id, run_id, round_id, age_id, grade_id, team_a_id, team_b_id, court_time_id, game_status, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: scheduling_locks; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.scheduling_locks (lock_id, season_day_id, run_id, locked_at, locked_by_user_id) FROM stdin;
\.


--
-- Data for Name: scheduling_run_events; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.scheduling_run_events (event_id, run_id, event_time, stage, severity, event_message, context) FROM stdin;
\.


--
-- Data for Name: scheduling_runs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.scheduling_runs (run_id, season_id, season_day_id, run_status, process_type, run_type, s1_check_results, round_ids, seed_master, resume_checkpoint, config_hash, idempotency_key, metrics, error_code, error_details, started_at, finished_at, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: season_days; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.season_days (season_day_id, season_id, season_day_name, season_day_label, week_day, window_start, window_end, active, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: seasons; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.seasons (season_id, competition_id, season_name, starting_date, ending_date, visibility, active, slug, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: staging_diffs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.staging_diffs (diff_id, run_id, entity_type, entity_id, change_type, before_json, after_json, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: teams; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.teams (team_id, grade_id, team_code, team_name, active, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: time_slots; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.time_slots (time_slot_id, season_day_id, start_time_id, end_time_id, start_time, end_time, time_slot_label, buffer_minutes, duration_minutes, created_at, created_by_user_id) FROM stdin;
\.


--
-- Data for Name: user_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_permissions (permission_id, user_account_id, organisation_id, can_schedule, can_approve, can_export, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (user_account_id, display_name, email, is_active, created_at) FROM stdin;
\.


--
-- Data for Name: venues; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.venues (venue_id, organisation_id, venue_name, venue_address, display_order, latitude, longitude, indoor, accessible, total_courts, created_at, created_by_user_id) FROM stdin;
\.


--
-- Name: age_court_restrictions_age_court_restriction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.age_court_restrictions_age_court_restriction_id_seq', 1, false);


--
-- Name: age_round_constraints_age_round_constraint_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.age_round_constraints_age_round_constraint_id_seq', 1, false);


--
-- Name: ages_age_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ages_age_id_seq', 1, false);


--
-- Name: allocation_settings_allocation_setting_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.allocation_settings_allocation_setting_id_seq', 1, false);


--
-- Name: competitions_competition_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.competitions_competition_id_seq', 1, false);


--
-- Name: court_rankings_court_rank_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.court_rankings_court_rank_id_seq', 1, false);


--
-- Name: court_times_court_time_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.court_times_court_time_id_seq', 1, false);


--
-- Name: courts_court_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.courts_court_id_seq', 1, false);


--
-- Name: dates_date_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dates_date_id_seq', 1, false);


--
-- Name: default_times_time_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.default_times_time_id_seq', 1, false);


--
-- Name: final_bye_schedule_final_bye_schedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.final_bye_schedule_final_bye_schedule_id_seq', 1, false);


--
-- Name: final_game_schedule_final_game_schedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.final_game_schedule_final_game_schedule_id_seq', 1, false);


--
-- Name: grade_court_restrictions_grade_court_restriction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.grade_court_restrictions_grade_court_restriction_id_seq', 1, false);


--
-- Name: grade_round_constraints_grade_round_constraint_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.grade_round_constraints_grade_round_constraint_id_seq', 1, false);


--
-- Name: grades_grade_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.grades_grade_id_seq', 1, false);


--
-- Name: organisations_organisation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.organisations_organisation_id_seq', 1, false);


--
-- Name: p2_allocations_p2_allocation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.p2_allocations_p2_allocation_id_seq', 1, false);


--
-- Name: p3_bye_allocations_p3_bye_allocation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.p3_bye_allocations_p3_bye_allocation_id_seq', 1, false);


--
-- Name: p3_game_allocations_p3_game_allocation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.p3_game_allocations_p3_game_allocation_id_seq', 1, false);


--
-- Name: public_holidays_public_holiday_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.public_holidays_public_holiday_id_seq', 1, false);


--
-- Name: round_dates_round_date_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.round_dates_round_date_id_seq', 1, false);


--
-- Name: round_groups_round_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.round_groups_round_group_id_seq', 1, false);


--
-- Name: round_settings_round_setting_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.round_settings_round_setting_id_seq', 1, false);


--
-- Name: rounds_round_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.rounds_round_id_seq', 1, false);


--
-- Name: run_constraints_snapshot_snapshot_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.run_constraints_snapshot_snapshot_id_seq', 1, false);


--
-- Name: run_exports_export_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.run_exports_export_id_seq', 1, false);


--
-- Name: saved_byes_saved_bye_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.saved_byes_saved_bye_id_seq', 1, false);


--
-- Name: saved_games_saved_game_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.saved_games_saved_game_id_seq', 1, false);


--
-- Name: scheduling_locks_lock_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.scheduling_locks_lock_id_seq', 1, false);


--
-- Name: scheduling_run_events_event_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.scheduling_run_events_event_id_seq', 1, false);


--
-- Name: scheduling_runs_run_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.scheduling_runs_run_id_seq', 1, false);


--
-- Name: season_days_season_day_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.season_days_season_day_id_seq', 1, false);


--
-- Name: seasons_season_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.seasons_season_id_seq', 1, false);


--
-- Name: staging_diffs_diff_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.staging_diffs_diff_id_seq', 1, false);


--
-- Name: teams_team_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.teams_team_id_seq', 1, false);


--
-- Name: time_slots_time_slot_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.time_slots_time_slot_id_seq', 1, false);


--
-- Name: user_permissions_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.user_permissions_permission_id_seq', 1, false);


--
-- Name: users_user_account_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_user_account_id_seq', 1, false);


--
-- Name: venues_venue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.venues_venue_id_seq', 1, false);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: age_court_restrictions pk_age_court_restrictions; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.age_court_restrictions
    ADD CONSTRAINT pk_age_court_restrictions PRIMARY KEY (age_court_restriction_id);


--
-- Name: age_round_constraints pk_age_round_constraints; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.age_round_constraints
    ADD CONSTRAINT pk_age_round_constraints PRIMARY KEY (age_round_constraint_id);


--
-- Name: ages pk_ages; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ages
    ADD CONSTRAINT pk_ages PRIMARY KEY (age_id);


--
-- Name: allocation_settings pk_allocation_settings; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.allocation_settings
    ADD CONSTRAINT pk_allocation_settings PRIMARY KEY (allocation_setting_id);


--
-- Name: competitions pk_competitions; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.competitions
    ADD CONSTRAINT pk_competitions PRIMARY KEY (competition_id);


--
-- Name: court_rankings pk_court_rankings; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.court_rankings
    ADD CONSTRAINT pk_court_rankings PRIMARY KEY (court_rank_id);


--
-- Name: court_times pk_court_times; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.court_times
    ADD CONSTRAINT pk_court_times PRIMARY KEY (court_time_id);


--
-- Name: courts pk_courts; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courts
    ADD CONSTRAINT pk_courts PRIMARY KEY (court_id);


--
-- Name: dates pk_dates; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dates
    ADD CONSTRAINT pk_dates PRIMARY KEY (date_id);


--
-- Name: default_times pk_default_times; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.default_times
    ADD CONSTRAINT pk_default_times PRIMARY KEY (time_id);


--
-- Name: final_bye_schedule pk_final_bye_schedule; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_bye_schedule
    ADD CONSTRAINT pk_final_bye_schedule PRIMARY KEY (final_bye_schedule_id);


--
-- Name: final_game_schedule pk_final_game_schedule; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_game_schedule
    ADD CONSTRAINT pk_final_game_schedule PRIMARY KEY (final_game_schedule_id);


--
-- Name: grade_court_restrictions pk_grade_court_restrictions; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grade_court_restrictions
    ADD CONSTRAINT pk_grade_court_restrictions PRIMARY KEY (grade_court_restriction_id);


--
-- Name: grade_round_constraints pk_grade_round_constraints; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grade_round_constraints
    ADD CONSTRAINT pk_grade_round_constraints PRIMARY KEY (grade_round_constraint_id);


--
-- Name: grades pk_grades; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grades
    ADD CONSTRAINT pk_grades PRIMARY KEY (grade_id);


--
-- Name: organisations pk_organisations; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.organisations
    ADD CONSTRAINT pk_organisations PRIMARY KEY (organisation_id);


--
-- Name: p2_allocations pk_p2_allocations; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p2_allocations
    ADD CONSTRAINT pk_p2_allocations PRIMARY KEY (p2_allocation_id);


--
-- Name: p3_bye_allocations pk_p3_bye_allocations; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_bye_allocations
    ADD CONSTRAINT pk_p3_bye_allocations PRIMARY KEY (p3_bye_allocation_id);


--
-- Name: p3_game_allocations pk_p3_game_allocations; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_game_allocations
    ADD CONSTRAINT pk_p3_game_allocations PRIMARY KEY (p3_game_allocation_id);


--
-- Name: public_holidays pk_public_holidays; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.public_holidays
    ADD CONSTRAINT pk_public_holidays PRIMARY KEY (public_holiday_id);


--
-- Name: round_dates pk_round_dates; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_dates
    ADD CONSTRAINT pk_round_dates PRIMARY KEY (round_date_id);


--
-- Name: round_groups pk_round_groups; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_groups
    ADD CONSTRAINT pk_round_groups PRIMARY KEY (round_group_id);


--
-- Name: round_settings pk_round_settings; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_settings
    ADD CONSTRAINT pk_round_settings PRIMARY KEY (round_setting_id);


--
-- Name: rounds pk_rounds; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rounds
    ADD CONSTRAINT pk_rounds PRIMARY KEY (round_id);


--
-- Name: run_constraints_snapshot pk_run_constraints_snapshot; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.run_constraints_snapshot
    ADD CONSTRAINT pk_run_constraints_snapshot PRIMARY KEY (snapshot_id);


--
-- Name: run_exports pk_run_exports; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.run_exports
    ADD CONSTRAINT pk_run_exports PRIMARY KEY (export_id);


--
-- Name: saved_byes pk_saved_byes; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_byes
    ADD CONSTRAINT pk_saved_byes PRIMARY KEY (saved_bye_id);


--
-- Name: saved_games pk_saved_games; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_games
    ADD CONSTRAINT pk_saved_games PRIMARY KEY (saved_game_id);


--
-- Name: scheduling_locks pk_scheduling_locks; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduling_locks
    ADD CONSTRAINT pk_scheduling_locks PRIMARY KEY (lock_id);


--
-- Name: scheduling_run_events pk_scheduling_run_events; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduling_run_events
    ADD CONSTRAINT pk_scheduling_run_events PRIMARY KEY (event_id);


--
-- Name: scheduling_runs pk_scheduling_runs; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduling_runs
    ADD CONSTRAINT pk_scheduling_runs PRIMARY KEY (run_id);


--
-- Name: season_days pk_season_days; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.season_days
    ADD CONSTRAINT pk_season_days PRIMARY KEY (season_day_id);


--
-- Name: seasons pk_seasons; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.seasons
    ADD CONSTRAINT pk_seasons PRIMARY KEY (season_id);


--
-- Name: staging_diffs pk_staging_diffs; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staging_diffs
    ADD CONSTRAINT pk_staging_diffs PRIMARY KEY (diff_id);


--
-- Name: teams pk_teams; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT pk_teams PRIMARY KEY (team_id);


--
-- Name: time_slots pk_time_slots; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_slots
    ADD CONSTRAINT pk_time_slots PRIMARY KEY (time_slot_id);


--
-- Name: user_permissions pk_user_permissions; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT pk_user_permissions PRIMARY KEY (permission_id);


--
-- Name: users pk_users; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT pk_users PRIMARY KEY (user_account_id);


--
-- Name: venues pk_venues; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.venues
    ADD CONSTRAINT pk_venues PRIMARY KEY (venue_id);


--
-- Name: age_court_restrictions uq_age_court_restrictions_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.age_court_restrictions
    ADD CONSTRAINT uq_age_court_restrictions_key UNIQUE (round_setting_id, age_id, court_time_id);


--
-- Name: age_round_constraints uq_age_round_constraints_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.age_round_constraints
    ADD CONSTRAINT uq_age_round_constraints_key UNIQUE (round_setting_id, age_id);


--
-- Name: ages uq_ages_code; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ages
    ADD CONSTRAINT uq_ages_code UNIQUE (season_day_id, age_code);


--
-- Name: ages uq_ages_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ages
    ADD CONSTRAINT uq_ages_name UNIQUE (season_day_id, age_name);


--
-- Name: ages uq_ages_rank; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ages
    ADD CONSTRAINT uq_ages_rank UNIQUE (season_day_id, age_rank);


--
-- Name: competitions uq_competitions_org_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.competitions
    ADD CONSTRAINT uq_competitions_org_name UNIQUE (organisation_id, competition_name);


--
-- Name: competitions uq_competitions_org_slug; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.competitions
    ADD CONSTRAINT uq_competitions_org_slug UNIQUE (organisation_id, slug);


--
-- Name: court_times uq_court_times_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.court_times
    ADD CONSTRAINT uq_court_times_key UNIQUE (season_day_id, round_setting_id, court_id, time_slot_id);


--
-- Name: courts uq_courts_venue_code; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courts
    ADD CONSTRAINT uq_courts_venue_code UNIQUE (venue_id, court_code);


--
-- Name: courts uq_courts_venue_display; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courts
    ADD CONSTRAINT uq_courts_venue_display UNIQUE (venue_id, display_order);


--
-- Name: courts uq_courts_venue_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courts
    ADD CONSTRAINT uq_courts_venue_name UNIQUE (venue_id, court_name);


--
-- Name: dates uq_dates_date_value; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dates
    ADD CONSTRAINT uq_dates_date_value UNIQUE (date_value);


--
-- Name: default_times uq_default_times_time_value; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.default_times
    ADD CONSTRAINT uq_default_times_time_value UNIQUE (time_value);


--
-- Name: final_bye_schedule uq_final_byes_round_team; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_bye_schedule
    ADD CONSTRAINT uq_final_byes_round_team UNIQUE (round_id, team_id);


--
-- Name: final_game_schedule uq_final_games_round_ct; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_game_schedule
    ADD CONSTRAINT uq_final_games_round_ct UNIQUE (round_id, court_time_id);


--
-- Name: grade_court_restrictions uq_grade_court_restrictions_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grade_court_restrictions
    ADD CONSTRAINT uq_grade_court_restrictions_key UNIQUE (round_setting_id, grade_id, court_time_id);


--
-- Name: grade_round_constraints uq_grade_round_constraints_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grade_round_constraints
    ADD CONSTRAINT uq_grade_round_constraints_key UNIQUE (round_setting_id, grade_id);


--
-- Name: grades uq_grades_code; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grades
    ADD CONSTRAINT uq_grades_code UNIQUE (age_id, grade_code);


--
-- Name: grades uq_grades_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grades
    ADD CONSTRAINT uq_grades_name UNIQUE (age_id, grade_name);


--
-- Name: grades uq_grades_rank; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grades
    ADD CONSTRAINT uq_grades_rank UNIQUE (age_id, grade_rank);


--
-- Name: organisations uq_organisations_organisation_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.organisations
    ADD CONSTRAINT uq_organisations_organisation_name UNIQUE (organisation_name);


--
-- Name: organisations uq_organisations_slug; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.organisations
    ADD CONSTRAINT uq_organisations_slug UNIQUE (slug);


--
-- Name: p2_allocations uq_p2_allocations_run_round_ct; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p2_allocations
    ADD CONSTRAINT uq_p2_allocations_run_round_ct UNIQUE (run_id, round_id, court_time_id);


--
-- Name: p3_bye_allocations uq_p3_byes_run_round_team; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_bye_allocations
    ADD CONSTRAINT uq_p3_byes_run_round_team UNIQUE (run_id, round_id, team_id);


--
-- Name: p3_game_allocations uq_p3_games_run_round_ct; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_game_allocations
    ADD CONSTRAINT uq_p3_games_run_round_ct UNIQUE (run_id, round_id, court_time_id);


--
-- Name: round_dates uq_round_dates_round_date; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_dates
    ADD CONSTRAINT uq_round_dates_round_date UNIQUE (round_id, date_id);


--
-- Name: round_groups uq_round_groups_round_setting; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_groups
    ADD CONSTRAINT uq_round_groups_round_setting UNIQUE (round_id, round_setting_id);


--
-- Name: round_settings uq_round_settings_day_number; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_settings
    ADD CONSTRAINT uq_round_settings_day_number UNIQUE (season_day_id, round_settings_number);


--
-- Name: rounds uq_rounds_season_label; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rounds
    ADD CONSTRAINT uq_rounds_season_label UNIQUE (season_id, round_label);


--
-- Name: rounds uq_rounds_season_number; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rounds
    ADD CONSTRAINT uq_rounds_season_number UNIQUE (season_id, round_number);


--
-- Name: run_exports uq_run_exports_file_path; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.run_exports
    ADD CONSTRAINT uq_run_exports_file_path UNIQUE (file_path);


--
-- Name: run_exports uq_run_exports_run_type; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.run_exports
    ADD CONSTRAINT uq_run_exports_run_type UNIQUE (run_id, export_type);


--
-- Name: saved_byes uq_saved_byes_run_round_team; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_byes
    ADD CONSTRAINT uq_saved_byes_run_round_team UNIQUE (run_id, round_id, team_id);


--
-- Name: saved_games uq_saved_games_run_round_ct; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_games
    ADD CONSTRAINT uq_saved_games_run_round_ct UNIQUE (run_id, round_id, court_time_id);


--
-- Name: scheduling_runs uq_scheduling_runs_idempotency_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduling_runs
    ADD CONSTRAINT uq_scheduling_runs_idempotency_key UNIQUE (idempotency_key);


--
-- Name: season_days uq_season_days_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.season_days
    ADD CONSTRAINT uq_season_days_name UNIQUE (season_id, season_day_name);


--
-- Name: season_days uq_season_days_weekday; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.season_days
    ADD CONSTRAINT uq_season_days_weekday UNIQUE (season_id, week_day);


--
-- Name: seasons uq_seasons_comp_slug; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.seasons
    ADD CONSTRAINT uq_seasons_comp_slug UNIQUE (competition_id, slug);


--
-- Name: seasons uq_seasons_competition_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.seasons
    ADD CONSTRAINT uq_seasons_competition_name UNIQUE (competition_id, season_name);


--
-- Name: teams uq_teams_grade_code; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT uq_teams_grade_code UNIQUE (grade_id, team_code);


--
-- Name: teams uq_teams_grade_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT uq_teams_grade_name UNIQUE (grade_id, team_name);


--
-- Name: time_slots uq_time_slots_day_label; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_slots
    ADD CONSTRAINT uq_time_slots_day_label UNIQUE (season_day_id, time_slot_label);


--
-- Name: time_slots uq_time_slots_day_window; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_slots
    ADD CONSTRAINT uq_time_slots_day_window UNIQUE (season_day_id, start_time, end_time);


--
-- Name: user_permissions uq_user_permissions_user_org; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT uq_user_permissions_user_org UNIQUE (user_account_id, organisation_id);


--
-- Name: users uq_users_email; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT uq_users_email UNIQUE (email);


--
-- Name: venues uq_venues_name_address; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.venues
    ADD CONSTRAINT uq_venues_name_address UNIQUE (venue_name, venue_address);


--
-- Name: idx_age_court_restrictions_keys; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_age_court_restrictions_keys ON public.age_court_restrictions USING btree (round_setting_id, age_id, court_time_id);


--
-- Name: idx_age_round_constraints_keys; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_age_round_constraints_keys ON public.age_round_constraints USING btree (round_setting_id, age_id);


--
-- Name: idx_ages_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ages_active ON public.ages USING btree (active);


--
-- Name: idx_competitions_created_by; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_competitions_created_by ON public.competitions USING btree (created_by_user_id);


--
-- Name: idx_competitions_org; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_competitions_org ON public.competitions USING btree (organisation_id);


--
-- Name: idx_court_times_court; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_court_times_court ON public.court_times USING btree (court_id);


--
-- Name: idx_court_times_day_setting; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_court_times_day_setting ON public.court_times USING btree (season_day_id, round_setting_id);


--
-- Name: idx_court_times_time_slot; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_court_times_time_slot ON public.court_times USING btree (time_slot_id);


--
-- Name: idx_courts_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_courts_active ON public.courts USING btree (active);


--
-- Name: idx_courts_venue; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_courts_venue ON public.courts USING btree (venue_id);


--
-- Name: idx_dates_date_value; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_dates_date_value ON public.dates USING btree (date_value);


--
-- Name: idx_default_times_time_value; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_default_times_time_value ON public.default_times USING btree (time_value);


--
-- Name: idx_final_byes_round; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_final_byes_round ON public.final_bye_schedule USING btree (round_id);


--
-- Name: idx_final_byes_team; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_final_byes_team ON public.final_bye_schedule USING btree (team_id);


--
-- Name: idx_final_games_ct; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_final_games_ct ON public.final_game_schedule USING btree (court_time_id);


--
-- Name: idx_final_games_round; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_final_games_round ON public.final_game_schedule USING btree (round_id);


--
-- Name: idx_grade_court_restrictions_keys; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_grade_court_restrictions_keys ON public.grade_court_restrictions USING btree (round_setting_id, grade_id, court_time_id);


--
-- Name: idx_grade_round_constraints_keys; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_grade_round_constraints_keys ON public.grade_round_constraints USING btree (round_setting_id, grade_id);


--
-- Name: idx_grades_age; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_grades_age ON public.grades USING btree (age_id);


--
-- Name: idx_organisations_created_by; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_organisations_created_by ON public.organisations USING btree (created_by_user_id);


--
-- Name: idx_p2_allocations_ct; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_p2_allocations_ct ON public.p2_allocations USING btree (court_time_id);


--
-- Name: idx_p2_allocations_run_round; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_p2_allocations_run_round ON public.p2_allocations USING btree (run_id, round_id);


--
-- Name: idx_p3_byes_run_round; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_p3_byes_run_round ON public.p3_bye_allocations USING btree (run_id, round_id);


--
-- Name: idx_p3_byes_team; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_p3_byes_team ON public.p3_bye_allocations USING btree (team_id);


--
-- Name: idx_p3_games_ct; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_p3_games_ct ON public.p3_game_allocations USING btree (court_time_id);


--
-- Name: idx_p3_games_run_round; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_p3_games_run_round ON public.p3_game_allocations USING btree (run_id, round_id);


--
-- Name: idx_p3_games_teams; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_p3_games_teams ON public.p3_game_allocations USING btree (team_a_id, team_b_id);


--
-- Name: idx_round_dates_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_round_dates_date ON public.round_dates USING btree (date_id);


--
-- Name: idx_round_dates_round; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_round_dates_round ON public.round_dates USING btree (round_id);


--
-- Name: idx_round_groups_round; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_round_groups_round ON public.round_groups USING btree (round_id);


--
-- Name: idx_round_groups_setting; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_round_groups_setting ON public.round_groups USING btree (round_setting_id);


--
-- Name: idx_round_settings_day; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_round_settings_day ON public.round_settings USING btree (season_day_id);


--
-- Name: idx_run_constraints_snapshot_run; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_run_constraints_snapshot_run ON public.run_constraints_snapshot USING btree (run_id);


--
-- Name: idx_run_events_run; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_run_events_run ON public.scheduling_run_events USING btree (run_id);


--
-- Name: idx_run_events_severity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_run_events_severity ON public.scheduling_run_events USING btree (severity);


--
-- Name: idx_run_events_stage; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_run_events_stage ON public.scheduling_run_events USING btree (stage);


--
-- Name: idx_run_events_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_run_events_time ON public.scheduling_run_events USING btree (event_time);


--
-- Name: idx_run_exports_run; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_run_exports_run ON public.run_exports USING btree (run_id);


--
-- Name: idx_runs_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_runs_created_at ON public.scheduling_runs USING btree (created_at);


--
-- Name: idx_runs_created_by; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_runs_created_by ON public.scheduling_runs USING btree (created_by_user_id);


--
-- Name: idx_runs_season_day; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_runs_season_day ON public.scheduling_runs USING btree (season_day_id);


--
-- Name: idx_runs_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_runs_status ON public.scheduling_runs USING btree (run_status);


--
-- Name: idx_saved_byes_run_round; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_saved_byes_run_round ON public.saved_byes USING btree (run_id, round_id);


--
-- Name: idx_saved_byes_team; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_saved_byes_team ON public.saved_byes USING btree (team_id);


--
-- Name: idx_saved_games_ct; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_saved_games_ct ON public.saved_games USING btree (court_time_id);


--
-- Name: idx_saved_games_run_round; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_saved_games_run_round ON public.saved_games USING btree (run_id, round_id);


--
-- Name: idx_season_days_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_season_days_active ON public.season_days USING btree (active);


--
-- Name: idx_season_days_season; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_season_days_season ON public.season_days USING btree (season_id);


--
-- Name: idx_season_days_week_day; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_season_days_week_day ON public.season_days USING btree (week_day);


--
-- Name: idx_seasons_comp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_seasons_comp ON public.seasons USING btree (competition_id);


--
-- Name: idx_seasons_created_by; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_seasons_created_by ON public.seasons USING btree (created_by_user_id);


--
-- Name: idx_seasons_visibility_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_seasons_visibility_active ON public.seasons USING btree (visibility, active);


--
-- Name: idx_staging_diffs_entity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_staging_diffs_entity ON public.staging_diffs USING btree (entity_type, entity_id);


--
-- Name: idx_staging_diffs_run; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_staging_diffs_run ON public.staging_diffs USING btree (run_id);


--
-- Name: idx_teams_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_teams_active ON public.teams USING btree (active);


--
-- Name: idx_teams_grade; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_teams_grade ON public.teams USING btree (grade_id);


--
-- Name: idx_time_slots_day; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_time_slots_day ON public.time_slots USING btree (season_day_id);


--
-- Name: idx_time_slots_start_end; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_time_slots_start_end ON public.time_slots USING btree (start_time, end_time);


--
-- Name: idx_user_permissions_org; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_permissions_org ON public.user_permissions USING btree (organisation_id);


--
-- Name: idx_user_permissions_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_permissions_user ON public.user_permissions USING btree (user_account_id);


--
-- Name: idx_venues_created_by; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_venues_created_by ON public.venues USING btree (created_by_user_id);


--
-- Name: uq_scheduling_locks_season_day; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_scheduling_locks_season_day ON public.scheduling_locks USING btree (season_day_id);


--
-- Name: age_court_restrictions fk_age_court_restrictions_ages_age_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.age_court_restrictions
    ADD CONSTRAINT fk_age_court_restrictions_ages_age_id FOREIGN KEY (age_id) REFERENCES public.ages(age_id);


--
-- Name: age_court_restrictions fk_age_court_restrictions_court_times_court_time_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.age_court_restrictions
    ADD CONSTRAINT fk_age_court_restrictions_court_times_court_time_id FOREIGN KEY (court_time_id) REFERENCES public.court_times(court_time_id);


--
-- Name: age_court_restrictions fk_age_court_restrictions_round_settings_round_setting_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.age_court_restrictions
    ADD CONSTRAINT fk_age_court_restrictions_round_settings_round_setting_id FOREIGN KEY (round_setting_id) REFERENCES public.round_settings(round_setting_id);


--
-- Name: age_court_restrictions fk_age_court_restrictions_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.age_court_restrictions
    ADD CONSTRAINT fk_age_court_restrictions_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: age_round_constraints fk_age_round_constraints_ages_age_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.age_round_constraints
    ADD CONSTRAINT fk_age_round_constraints_ages_age_id FOREIGN KEY (age_id) REFERENCES public.ages(age_id);


--
-- Name: age_round_constraints fk_age_round_constraints_round_settings_round_setting_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.age_round_constraints
    ADD CONSTRAINT fk_age_round_constraints_round_settings_round_setting_id FOREIGN KEY (round_setting_id) REFERENCES public.round_settings(round_setting_id);


--
-- Name: age_round_constraints fk_age_round_constraints_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.age_round_constraints
    ADD CONSTRAINT fk_age_round_constraints_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: ages fk_ages_season_days_season_day_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ages
    ADD CONSTRAINT fk_ages_season_days_season_day_id FOREIGN KEY (season_day_id) REFERENCES public.season_days(season_day_id);


--
-- Name: ages fk_ages_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ages
    ADD CONSTRAINT fk_ages_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: allocation_settings fk_allocation_settings_ages_age_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.allocation_settings
    ADD CONSTRAINT fk_allocation_settings_ages_age_id FOREIGN KEY (age_id) REFERENCES public.ages(age_id);


--
-- Name: allocation_settings fk_allocation_settings_grades_grade_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.allocation_settings
    ADD CONSTRAINT fk_allocation_settings_grades_grade_id FOREIGN KEY (grade_id) REFERENCES public.grades(grade_id);


--
-- Name: allocation_settings fk_allocation_settings_round_settings_round_setting_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.allocation_settings
    ADD CONSTRAINT fk_allocation_settings_round_settings_round_setting_id FOREIGN KEY (round_setting_id) REFERENCES public.round_settings(round_setting_id);


--
-- Name: allocation_settings fk_allocation_settings_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.allocation_settings
    ADD CONSTRAINT fk_allocation_settings_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: allocation_settings fk_allocation_settings_users_updated_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.allocation_settings
    ADD CONSTRAINT fk_allocation_settings_users_updated_by_user_id FOREIGN KEY (updated_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: competitions fk_competitions_organisations_organisation_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.competitions
    ADD CONSTRAINT fk_competitions_organisations_organisation_id FOREIGN KEY (organisation_id) REFERENCES public.organisations(organisation_id);


--
-- Name: competitions fk_competitions_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.competitions
    ADD CONSTRAINT fk_competitions_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: court_rankings fk_court_rankings_courts_court_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.court_rankings
    ADD CONSTRAINT fk_court_rankings_courts_court_id FOREIGN KEY (court_id) REFERENCES public.courts(court_id);


--
-- Name: court_rankings fk_court_rankings_round_settings_round_setting_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.court_rankings
    ADD CONSTRAINT fk_court_rankings_round_settings_round_setting_id FOREIGN KEY (round_setting_id) REFERENCES public.round_settings(round_setting_id);


--
-- Name: court_rankings fk_court_rankings_season_days_season_day_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.court_rankings
    ADD CONSTRAINT fk_court_rankings_season_days_season_day_id FOREIGN KEY (season_day_id) REFERENCES public.season_days(season_day_id);


--
-- Name: court_rankings fk_court_rankings_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.court_rankings
    ADD CONSTRAINT fk_court_rankings_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: court_rankings fk_court_rankings_users_updated_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.court_rankings
    ADD CONSTRAINT fk_court_rankings_users_updated_by_user_id FOREIGN KEY (updated_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: court_times fk_court_times_courts_court_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.court_times
    ADD CONSTRAINT fk_court_times_courts_court_id FOREIGN KEY (court_id) REFERENCES public.courts(court_id);


--
-- Name: court_times fk_court_times_round_settings_round_setting_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.court_times
    ADD CONSTRAINT fk_court_times_round_settings_round_setting_id FOREIGN KEY (round_setting_id) REFERENCES public.round_settings(round_setting_id);


--
-- Name: court_times fk_court_times_season_days_season_day_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.court_times
    ADD CONSTRAINT fk_court_times_season_days_season_day_id FOREIGN KEY (season_day_id) REFERENCES public.season_days(season_day_id);


--
-- Name: court_times fk_court_times_time_slots_time_slot_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.court_times
    ADD CONSTRAINT fk_court_times_time_slots_time_slot_id FOREIGN KEY (time_slot_id) REFERENCES public.time_slots(time_slot_id);


--
-- Name: court_times fk_court_times_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.court_times
    ADD CONSTRAINT fk_court_times_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: court_times fk_court_times_users_updated_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.court_times
    ADD CONSTRAINT fk_court_times_users_updated_by_user_id FOREIGN KEY (updated_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: courts fk_courts_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courts
    ADD CONSTRAINT fk_courts_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: courts fk_courts_venues_venue_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courts
    ADD CONSTRAINT fk_courts_venues_venue_id FOREIGN KEY (venue_id) REFERENCES public.venues(venue_id);


--
-- Name: final_bye_schedule fk_final_bye_schedule_ages_age_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_bye_schedule
    ADD CONSTRAINT fk_final_bye_schedule_ages_age_id FOREIGN KEY (age_id) REFERENCES public.ages(age_id);


--
-- Name: final_bye_schedule fk_final_bye_schedule_grades_grade_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_bye_schedule
    ADD CONSTRAINT fk_final_bye_schedule_grades_grade_id FOREIGN KEY (grade_id) REFERENCES public.grades(grade_id);


--
-- Name: final_bye_schedule fk_final_bye_schedule_rounds_round_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_bye_schedule
    ADD CONSTRAINT fk_final_bye_schedule_rounds_round_id FOREIGN KEY (round_id) REFERENCES public.rounds(round_id);


--
-- Name: final_bye_schedule fk_final_bye_schedule_scheduling_runs_run_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_bye_schedule
    ADD CONSTRAINT fk_final_bye_schedule_scheduling_runs_run_id FOREIGN KEY (run_id) REFERENCES public.scheduling_runs(run_id);


--
-- Name: final_bye_schedule fk_final_bye_schedule_teams_team_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_bye_schedule
    ADD CONSTRAINT fk_final_bye_schedule_teams_team_id FOREIGN KEY (team_id) REFERENCES public.teams(team_id);


--
-- Name: final_bye_schedule fk_final_bye_schedule_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_bye_schedule
    ADD CONSTRAINT fk_final_bye_schedule_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: final_bye_schedule fk_final_bye_schedule_users_published_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_bye_schedule
    ADD CONSTRAINT fk_final_bye_schedule_users_published_by_user_id FOREIGN KEY (published_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: final_game_schedule fk_final_game_schedule_ages_age_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_game_schedule
    ADD CONSTRAINT fk_final_game_schedule_ages_age_id FOREIGN KEY (age_id) REFERENCES public.ages(age_id);


--
-- Name: final_game_schedule fk_final_game_schedule_court_times_court_time_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_game_schedule
    ADD CONSTRAINT fk_final_game_schedule_court_times_court_time_id FOREIGN KEY (court_time_id) REFERENCES public.court_times(court_time_id);


--
-- Name: final_game_schedule fk_final_game_schedule_grades_grade_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_game_schedule
    ADD CONSTRAINT fk_final_game_schedule_grades_grade_id FOREIGN KEY (grade_id) REFERENCES public.grades(grade_id);


--
-- Name: final_game_schedule fk_final_game_schedule_rounds_round_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_game_schedule
    ADD CONSTRAINT fk_final_game_schedule_rounds_round_id FOREIGN KEY (round_id) REFERENCES public.rounds(round_id);


--
-- Name: final_game_schedule fk_final_game_schedule_scheduling_runs_run_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_game_schedule
    ADD CONSTRAINT fk_final_game_schedule_scheduling_runs_run_id FOREIGN KEY (run_id) REFERENCES public.scheduling_runs(run_id);


--
-- Name: final_game_schedule fk_final_game_schedule_teams_team_a_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_game_schedule
    ADD CONSTRAINT fk_final_game_schedule_teams_team_a_id FOREIGN KEY (team_a_id) REFERENCES public.teams(team_id);


--
-- Name: final_game_schedule fk_final_game_schedule_teams_team_b_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_game_schedule
    ADD CONSTRAINT fk_final_game_schedule_teams_team_b_id FOREIGN KEY (team_b_id) REFERENCES public.teams(team_id);


--
-- Name: final_game_schedule fk_final_game_schedule_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_game_schedule
    ADD CONSTRAINT fk_final_game_schedule_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: final_game_schedule fk_final_game_schedule_users_published_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.final_game_schedule
    ADD CONSTRAINT fk_final_game_schedule_users_published_by_user_id FOREIGN KEY (published_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: grade_court_restrictions fk_grade_court_restrictions_court_times_court_time_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grade_court_restrictions
    ADD CONSTRAINT fk_grade_court_restrictions_court_times_court_time_id FOREIGN KEY (court_time_id) REFERENCES public.court_times(court_time_id);


--
-- Name: grade_court_restrictions fk_grade_court_restrictions_grades_grade_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grade_court_restrictions
    ADD CONSTRAINT fk_grade_court_restrictions_grades_grade_id FOREIGN KEY (grade_id) REFERENCES public.grades(grade_id);


--
-- Name: grade_court_restrictions fk_grade_court_restrictions_round_settings_round_setting_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grade_court_restrictions
    ADD CONSTRAINT fk_grade_court_restrictions_round_settings_round_setting_id FOREIGN KEY (round_setting_id) REFERENCES public.round_settings(round_setting_id);


--
-- Name: grade_court_restrictions fk_grade_court_restrictions_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grade_court_restrictions
    ADD CONSTRAINT fk_grade_court_restrictions_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: grade_round_constraints fk_grade_round_constraints_ages_age_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grade_round_constraints
    ADD CONSTRAINT fk_grade_round_constraints_ages_age_id FOREIGN KEY (age_id) REFERENCES public.ages(age_id);


--
-- Name: grade_round_constraints fk_grade_round_constraints_grades_grade_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grade_round_constraints
    ADD CONSTRAINT fk_grade_round_constraints_grades_grade_id FOREIGN KEY (grade_id) REFERENCES public.grades(grade_id);


--
-- Name: grade_round_constraints fk_grade_round_constraints_round_settings_round_setting_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grade_round_constraints
    ADD CONSTRAINT fk_grade_round_constraints_round_settings_round_setting_id FOREIGN KEY (round_setting_id) REFERENCES public.round_settings(round_setting_id);


--
-- Name: grade_round_constraints fk_grade_round_constraints_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grade_round_constraints
    ADD CONSTRAINT fk_grade_round_constraints_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: grades fk_grades_ages_age_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grades
    ADD CONSTRAINT fk_grades_ages_age_id FOREIGN KEY (age_id) REFERENCES public.ages(age_id);


--
-- Name: grades fk_grades_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grades
    ADD CONSTRAINT fk_grades_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: organisations fk_organisations_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.organisations
    ADD CONSTRAINT fk_organisations_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: p2_allocations fk_p2_allocations_ages_age_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p2_allocations
    ADD CONSTRAINT fk_p2_allocations_ages_age_id FOREIGN KEY (age_id) REFERENCES public.ages(age_id);


--
-- Name: p2_allocations fk_p2_allocations_court_times_court_time_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p2_allocations
    ADD CONSTRAINT fk_p2_allocations_court_times_court_time_id FOREIGN KEY (court_time_id) REFERENCES public.court_times(court_time_id);


--
-- Name: p2_allocations fk_p2_allocations_grades_grade_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p2_allocations
    ADD CONSTRAINT fk_p2_allocations_grades_grade_id FOREIGN KEY (grade_id) REFERENCES public.grades(grade_id);


--
-- Name: p2_allocations fk_p2_allocations_rounds_round_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p2_allocations
    ADD CONSTRAINT fk_p2_allocations_rounds_round_id FOREIGN KEY (round_id) REFERENCES public.rounds(round_id);


--
-- Name: p2_allocations fk_p2_allocations_scheduling_runs_run_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p2_allocations
    ADD CONSTRAINT fk_p2_allocations_scheduling_runs_run_id FOREIGN KEY (run_id) REFERENCES public.scheduling_runs(run_id);


--
-- Name: p2_allocations fk_p2_allocations_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p2_allocations
    ADD CONSTRAINT fk_p2_allocations_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: p3_bye_allocations fk_p3_bye_allocations_ages_age_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_bye_allocations
    ADD CONSTRAINT fk_p3_bye_allocations_ages_age_id FOREIGN KEY (age_id) REFERENCES public.ages(age_id);


--
-- Name: p3_bye_allocations fk_p3_bye_allocations_grades_grade_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_bye_allocations
    ADD CONSTRAINT fk_p3_bye_allocations_grades_grade_id FOREIGN KEY (grade_id) REFERENCES public.grades(grade_id);


--
-- Name: p3_bye_allocations fk_p3_bye_allocations_rounds_round_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_bye_allocations
    ADD CONSTRAINT fk_p3_bye_allocations_rounds_round_id FOREIGN KEY (round_id) REFERENCES public.rounds(round_id);


--
-- Name: p3_bye_allocations fk_p3_bye_allocations_scheduling_runs_run_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_bye_allocations
    ADD CONSTRAINT fk_p3_bye_allocations_scheduling_runs_run_id FOREIGN KEY (run_id) REFERENCES public.scheduling_runs(run_id);


--
-- Name: p3_bye_allocations fk_p3_bye_allocations_teams_team_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_bye_allocations
    ADD CONSTRAINT fk_p3_bye_allocations_teams_team_id FOREIGN KEY (team_id) REFERENCES public.teams(team_id);


--
-- Name: p3_bye_allocations fk_p3_bye_allocations_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_bye_allocations
    ADD CONSTRAINT fk_p3_bye_allocations_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: p3_game_allocations fk_p3_game_allocations_ages_age_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_game_allocations
    ADD CONSTRAINT fk_p3_game_allocations_ages_age_id FOREIGN KEY (age_id) REFERENCES public.ages(age_id);


--
-- Name: p3_game_allocations fk_p3_game_allocations_court_times_court_time_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_game_allocations
    ADD CONSTRAINT fk_p3_game_allocations_court_times_court_time_id FOREIGN KEY (court_time_id) REFERENCES public.court_times(court_time_id);


--
-- Name: p3_game_allocations fk_p3_game_allocations_grades_grade_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_game_allocations
    ADD CONSTRAINT fk_p3_game_allocations_grades_grade_id FOREIGN KEY (grade_id) REFERENCES public.grades(grade_id);


--
-- Name: p3_game_allocations fk_p3_game_allocations_p2_allocations_p2_allocation_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_game_allocations
    ADD CONSTRAINT fk_p3_game_allocations_p2_allocations_p2_allocation_id FOREIGN KEY (p2_allocation_id) REFERENCES public.p2_allocations(p2_allocation_id);


--
-- Name: p3_game_allocations fk_p3_game_allocations_rounds_round_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_game_allocations
    ADD CONSTRAINT fk_p3_game_allocations_rounds_round_id FOREIGN KEY (round_id) REFERENCES public.rounds(round_id);


--
-- Name: p3_game_allocations fk_p3_game_allocations_scheduling_runs_run_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_game_allocations
    ADD CONSTRAINT fk_p3_game_allocations_scheduling_runs_run_id FOREIGN KEY (run_id) REFERENCES public.scheduling_runs(run_id);


--
-- Name: p3_game_allocations fk_p3_game_allocations_teams_team_a_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_game_allocations
    ADD CONSTRAINT fk_p3_game_allocations_teams_team_a_id FOREIGN KEY (team_a_id) REFERENCES public.teams(team_id);


--
-- Name: p3_game_allocations fk_p3_game_allocations_teams_team_b_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_game_allocations
    ADD CONSTRAINT fk_p3_game_allocations_teams_team_b_id FOREIGN KEY (team_b_id) REFERENCES public.teams(team_id);


--
-- Name: p3_game_allocations fk_p3_game_allocations_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p3_game_allocations
    ADD CONSTRAINT fk_p3_game_allocations_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: public_holidays fk_public_holidays_dates_date_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.public_holidays
    ADD CONSTRAINT fk_public_holidays_dates_date_id FOREIGN KEY (date_id) REFERENCES public.dates(date_id);


--
-- Name: round_dates fk_round_dates_dates_date_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_dates
    ADD CONSTRAINT fk_round_dates_dates_date_id FOREIGN KEY (date_id) REFERENCES public.dates(date_id);


--
-- Name: round_dates fk_round_dates_rounds_round_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_dates
    ADD CONSTRAINT fk_round_dates_rounds_round_id FOREIGN KEY (round_id) REFERENCES public.rounds(round_id);


--
-- Name: round_dates fk_round_dates_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_dates
    ADD CONSTRAINT fk_round_dates_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: round_groups fk_round_groups_round_settings_round_setting_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_groups
    ADD CONSTRAINT fk_round_groups_round_settings_round_setting_id FOREIGN KEY (round_setting_id) REFERENCES public.round_settings(round_setting_id);


--
-- Name: round_groups fk_round_groups_rounds_round_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_groups
    ADD CONSTRAINT fk_round_groups_rounds_round_id FOREIGN KEY (round_id) REFERENCES public.rounds(round_id);


--
-- Name: round_groups fk_round_groups_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_groups
    ADD CONSTRAINT fk_round_groups_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: round_settings fk_round_settings_season_days_season_day_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_settings
    ADD CONSTRAINT fk_round_settings_season_days_season_day_id FOREIGN KEY (season_day_id) REFERENCES public.season_days(season_day_id);


--
-- Name: round_settings fk_round_settings_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_settings
    ADD CONSTRAINT fk_round_settings_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: rounds fk_rounds_seasons_season_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rounds
    ADD CONSTRAINT fk_rounds_seasons_season_id FOREIGN KEY (season_id) REFERENCES public.seasons(season_id);


--
-- Name: rounds fk_rounds_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rounds
    ADD CONSTRAINT fk_rounds_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: run_constraints_snapshot fk_run_constraints_snapshot_scheduling_runs_run_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.run_constraints_snapshot
    ADD CONSTRAINT fk_run_constraints_snapshot_scheduling_runs_run_id FOREIGN KEY (run_id) REFERENCES public.scheduling_runs(run_id);


--
-- Name: run_exports fk_run_exports_scheduling_runs_run_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.run_exports
    ADD CONSTRAINT fk_run_exports_scheduling_runs_run_id FOREIGN KEY (run_id) REFERENCES public.scheduling_runs(run_id);


--
-- Name: saved_byes fk_saved_byes_ages_age_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_byes
    ADD CONSTRAINT fk_saved_byes_ages_age_id FOREIGN KEY (age_id) REFERENCES public.ages(age_id);


--
-- Name: saved_byes fk_saved_byes_grades_grade_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_byes
    ADD CONSTRAINT fk_saved_byes_grades_grade_id FOREIGN KEY (grade_id) REFERENCES public.grades(grade_id);


--
-- Name: saved_byes fk_saved_byes_rounds_round_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_byes
    ADD CONSTRAINT fk_saved_byes_rounds_round_id FOREIGN KEY (round_id) REFERENCES public.rounds(round_id);


--
-- Name: saved_byes fk_saved_byes_scheduling_runs_run_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_byes
    ADD CONSTRAINT fk_saved_byes_scheduling_runs_run_id FOREIGN KEY (run_id) REFERENCES public.scheduling_runs(run_id);


--
-- Name: saved_byes fk_saved_byes_teams_team_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_byes
    ADD CONSTRAINT fk_saved_byes_teams_team_id FOREIGN KEY (team_id) REFERENCES public.teams(team_id);


--
-- Name: saved_byes fk_saved_byes_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_byes
    ADD CONSTRAINT fk_saved_byes_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: saved_games fk_saved_games_ages_age_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_games
    ADD CONSTRAINT fk_saved_games_ages_age_id FOREIGN KEY (age_id) REFERENCES public.ages(age_id);


--
-- Name: saved_games fk_saved_games_court_times_court_time_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_games
    ADD CONSTRAINT fk_saved_games_court_times_court_time_id FOREIGN KEY (court_time_id) REFERENCES public.court_times(court_time_id);


--
-- Name: saved_games fk_saved_games_grades_grade_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_games
    ADD CONSTRAINT fk_saved_games_grades_grade_id FOREIGN KEY (grade_id) REFERENCES public.grades(grade_id);


--
-- Name: saved_games fk_saved_games_rounds_round_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_games
    ADD CONSTRAINT fk_saved_games_rounds_round_id FOREIGN KEY (round_id) REFERENCES public.rounds(round_id);


--
-- Name: saved_games fk_saved_games_scheduling_runs_run_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_games
    ADD CONSTRAINT fk_saved_games_scheduling_runs_run_id FOREIGN KEY (run_id) REFERENCES public.scheduling_runs(run_id);


--
-- Name: saved_games fk_saved_games_teams_team_a_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_games
    ADD CONSTRAINT fk_saved_games_teams_team_a_id FOREIGN KEY (team_a_id) REFERENCES public.teams(team_id);


--
-- Name: saved_games fk_saved_games_teams_team_b_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_games
    ADD CONSTRAINT fk_saved_games_teams_team_b_id FOREIGN KEY (team_b_id) REFERENCES public.teams(team_id);


--
-- Name: saved_games fk_saved_games_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_games
    ADD CONSTRAINT fk_saved_games_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: scheduling_locks fk_scheduling_locks_scheduling_runs_run_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduling_locks
    ADD CONSTRAINT fk_scheduling_locks_scheduling_runs_run_id FOREIGN KEY (run_id) REFERENCES public.scheduling_runs(run_id);


--
-- Name: scheduling_locks fk_scheduling_locks_season_days_season_day_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduling_locks
    ADD CONSTRAINT fk_scheduling_locks_season_days_season_day_id FOREIGN KEY (season_day_id) REFERENCES public.season_days(season_day_id);


--
-- Name: scheduling_locks fk_scheduling_locks_users_locked_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduling_locks
    ADD CONSTRAINT fk_scheduling_locks_users_locked_by_user_id FOREIGN KEY (locked_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: scheduling_run_events fk_scheduling_run_events_scheduling_runs_run_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduling_run_events
    ADD CONSTRAINT fk_scheduling_run_events_scheduling_runs_run_id FOREIGN KEY (run_id) REFERENCES public.scheduling_runs(run_id);


--
-- Name: scheduling_runs fk_scheduling_runs_season_days_season_day_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduling_runs
    ADD CONSTRAINT fk_scheduling_runs_season_days_season_day_id FOREIGN KEY (season_day_id) REFERENCES public.season_days(season_day_id);


--
-- Name: scheduling_runs fk_scheduling_runs_seasons_season_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduling_runs
    ADD CONSTRAINT fk_scheduling_runs_seasons_season_id FOREIGN KEY (season_id) REFERENCES public.seasons(season_id);


--
-- Name: scheduling_runs fk_scheduling_runs_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduling_runs
    ADD CONSTRAINT fk_scheduling_runs_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: season_days fk_season_days_seasons_season_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.season_days
    ADD CONSTRAINT fk_season_days_seasons_season_id FOREIGN KEY (season_id) REFERENCES public.seasons(season_id);


--
-- Name: season_days fk_season_days_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.season_days
    ADD CONSTRAINT fk_season_days_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: seasons fk_seasons_competitions_competition_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.seasons
    ADD CONSTRAINT fk_seasons_competitions_competition_id FOREIGN KEY (competition_id) REFERENCES public.competitions(competition_id);


--
-- Name: seasons fk_seasons_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.seasons
    ADD CONSTRAINT fk_seasons_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: staging_diffs fk_staging_diffs_scheduling_runs_run_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staging_diffs
    ADD CONSTRAINT fk_staging_diffs_scheduling_runs_run_id FOREIGN KEY (run_id) REFERENCES public.scheduling_runs(run_id);


--
-- Name: staging_diffs fk_staging_diffs_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staging_diffs
    ADD CONSTRAINT fk_staging_diffs_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: teams fk_teams_grades_grade_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT fk_teams_grades_grade_id FOREIGN KEY (grade_id) REFERENCES public.grades(grade_id);


--
-- Name: teams fk_teams_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT fk_teams_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: time_slots fk_time_slots_default_times_end_time_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_slots
    ADD CONSTRAINT fk_time_slots_default_times_end_time_id FOREIGN KEY (end_time_id) REFERENCES public.default_times(time_id);


--
-- Name: time_slots fk_time_slots_default_times_start_time_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_slots
    ADD CONSTRAINT fk_time_slots_default_times_start_time_id FOREIGN KEY (start_time_id) REFERENCES public.default_times(time_id);


--
-- Name: time_slots fk_time_slots_season_days_season_day_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_slots
    ADD CONSTRAINT fk_time_slots_season_days_season_day_id FOREIGN KEY (season_day_id) REFERENCES public.season_days(season_day_id);


--
-- Name: time_slots fk_time_slots_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_slots
    ADD CONSTRAINT fk_time_slots_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- Name: user_permissions fk_user_permissions_organisations_organisation_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT fk_user_permissions_organisations_organisation_id FOREIGN KEY (organisation_id) REFERENCES public.organisations(organisation_id);


--
-- Name: user_permissions fk_user_permissions_users_user_account_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT fk_user_permissions_users_user_account_id FOREIGN KEY (user_account_id) REFERENCES public.users(user_account_id);


--
-- Name: venues fk_venues_organisations_organisation_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.venues
    ADD CONSTRAINT fk_venues_organisations_organisation_id FOREIGN KEY (organisation_id) REFERENCES public.organisations(organisation_id);


--
-- Name: venues fk_venues_users_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.venues
    ADD CONSTRAINT fk_venues_users_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(user_account_id);


--
-- PostgreSQL database dump complete
--
