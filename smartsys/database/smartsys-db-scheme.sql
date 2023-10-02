--
-- PostgreSQL database dump
--

-- Started on 2023-09-30 23:02:47 EEST

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
-- TOC entry 3108 (class 1262 OID 16402)
-- Name: smartsys; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE smartsys WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.utf8';


ALTER DATABASE smartsys OWNER TO postgres;

\connect smartsys

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
-- TOC entry 5 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;

--
-- TOC entry 3110 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- TOC entry 214 (class 1255 OID 18758)
-- Name: trig_act_alarm(); Type: FUNCTION; Schema: public; Owner: smartsys
--

CREATE FUNCTION public.trig_act_alarm() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.alarm = ( SELECT "alarm" FROM "trig" WHERE "ID" = NEW.trig);
  RETURN NEW;
END;
$$;


ALTER FUNCTION public.trig_act_alarm() OWNER TO smartsys;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 200 (class 1259 OID 18759)
-- Name: clients; Type: TABLE; Schema: public; Owner: smartsys
--

CREATE TABLE public.clients (
    "ID" bigint NOT NULL,
    name character varying(256) DEFAULT ''::character varying NOT NULL,
    type character varying(256) DEFAULT ''::character varying NOT NULL,
    address character varying(256) DEFAULT ''::character varying NOT NULL,
    state boolean DEFAULT false NOT NULL
);


ALTER TABLE public.clients OWNER TO smartsys;

--
-- TOC entry 201 (class 1259 OID 18769)
-- Name: clients_ID_seq; Type: SEQUENCE; Schema: public; Owner: smartsys
--

CREATE SEQUENCE public."clients_ID_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."clients_ID_seq" OWNER TO smartsys;

--
-- TOC entry 3112 (class 0 OID 0)
-- Dependencies: 201
-- Name: clients_ID_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartsys
--

ALTER SEQUENCE public."clients_ID_seq" OWNED BY public.clients."ID";


--
-- TOC entry 202 (class 1259 OID 18771)
-- Name: point; Type: TABLE; Schema: public; Owner: smartsys
--

CREATE TABLE public.point (
    "ID" bigint NOT NULL,
    name character varying(256) DEFAULT ''::character varying NOT NULL,
    type character varying(256) DEFAULT ''::character varying NOT NULL,
    info character varying(256) DEFAULT ''::character varying NOT NULL,
    address character varying(512) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.point OWNER TO smartsys;

--
-- TOC entry 203 (class 1259 OID 18781)
-- Name: point_ID_seq; Type: SEQUENCE; Schema: public; Owner: smartsys
--

CREATE SEQUENCE public."point_ID_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."point_ID_seq" OWNER TO smartsys;

--
-- TOC entry 3113 (class 0 OID 0)
-- Dependencies: 203
-- Name: point_ID_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartsys
--

ALTER SEQUENCE public."point_ID_seq" OWNED BY public.point."ID";


--
-- TOC entry 204 (class 1259 OID 18783)
-- Name: sensors; Type: TABLE; Schema: public; Owner: smartsys
--

CREATE TABLE public.sensors (
    "ID" bigint NOT NULL,
    name character varying(256) DEFAULT ''::character varying NOT NULL,
    info character varying(512) DEFAULT ''::character varying NOT NULL,
    source character varying(256) DEFAULT ''::character varying NOT NULL,
    type character varying(256) DEFAULT ''::character varying NOT NULL,
    enable boolean DEFAULT false NOT NULL,
    update boolean DEFAULT false NOT NULL,
    alarm boolean DEFAULT false NOT NULL
);


ALTER TABLE public.sensors OWNER TO smartsys;

--
-- TOC entry 205 (class 1259 OID 18796)
-- Name: sensors_ID_seq; Type: SEQUENCE; Schema: public; Owner: smartsys
--

CREATE SEQUENCE public."sensors_ID_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."sensors_ID_seq" OWNER TO smartsys;

--
-- TOC entry 3114 (class 0 OID 0)
-- Dependencies: 205
-- Name: sensors_ID_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartsys
--

ALTER SEQUENCE public."sensors_ID_seq" OWNED BY public.sensors."ID";


--
-- TOC entry 206 (class 1259 OID 18798)
-- Name: trig; Type: TABLE; Schema: public; Owner: smartsys
--

CREATE TABLE public.trig (
    "ID" bigint NOT NULL,
    name character varying(256) DEFAULT ''::character varying NOT NULL,
    info character varying(512) DEFAULT ''::character varying NOT NULL,
    source character varying(256) DEFAULT ''::character varying NOT NULL,
    alarm boolean DEFAULT false NOT NULL,
    up_text character varying(256) DEFAULT ''::character varying NOT NULL,
    down_text character varying(256) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.trig OWNER TO smartsys;

--
-- TOC entry 207 (class 1259 OID 18810)
-- Name: trig_act; Type: TABLE; Schema: public; Owner: smartsys
--

CREATE TABLE public.trig_act (
    "ID" bigint NOT NULL,
    trig bigint NOT NULL,
    "DateTime" timestamp(0) without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    value boolean DEFAULT false NOT NULL,
    alarm boolean DEFAULT false NOT NULL
);


ALTER TABLE public.trig_act OWNER TO smartsys;

--
-- TOC entry 208 (class 1259 OID 18816)
-- Name: trig_act_ID_seq; Type: SEQUENCE; Schema: public; Owner: smartsys
--

CREATE SEQUENCE public."trig_act_ID_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."trig_act_ID_seq" OWNER TO smartsys;

--
-- TOC entry 3115 (class 0 OID 0)
-- Dependencies: 208
-- Name: trig_act_ID_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartsys
--

ALTER SEQUENCE public."trig_act_ID_seq" OWNED BY public.trig_act."ID";


--
-- TOC entry 209 (class 1259 OID 18818)
-- Name: trig_act_trig_seq; Type: SEQUENCE; Schema: public; Owner: smartsys
--

CREATE SEQUENCE public.trig_act_trig_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trig_act_trig_seq OWNER TO smartsys;

--
-- TOC entry 3116 (class 0 OID 0)
-- Dependencies: 209
-- Name: trig_act_trig_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartsys
--

ALTER SEQUENCE public.trig_act_trig_seq OWNED BY public.trig_act.trig;


--
-- TOC entry 210 (class 1259 OID 18820)
-- Name: triggers_ID_seq; Type: SEQUENCE; Schema: public; Owner: smartsys
--

CREATE SEQUENCE public."triggers_ID_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."triggers_ID_seq" OWNER TO smartsys;

--
-- TOC entry 3117 (class 0 OID 0)
-- Dependencies: 210
-- Name: triggers_ID_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartsys
--

ALTER SEQUENCE public."triggers_ID_seq" OWNED BY public.trig."ID";


--
-- TOC entry 211 (class 1259 OID 18822)
-- Name: value_thp; Type: TABLE; Schema: public; Owner: smartsys
--

CREATE TABLE public.value_thp (
    "ID" bigint NOT NULL,
    point bigint NOT NULL,
    "DateTime" timestamp(0) without time zone DEFAULT ('now'::text)::timestamp(0) without time zone NOT NULL,
    temp numeric(4,1) DEFAULT (0)::numeric(4,1) NOT NULL,
    humidity numeric(4,1) DEFAULT (0)::numeric(4,1) NOT NULL,
    pressure numeric(4,1) DEFAULT (0)::numeric(4,1) NOT NULL
);


ALTER TABLE public.value_thp OWNER TO smartsys;

--
-- TOC entry 212 (class 1259 OID 18829)
-- Name: value_thp_ID_seq; Type: SEQUENCE; Schema: public; Owner: smartsys
--

CREATE SEQUENCE public."value_thp_ID_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."value_thp_ID_seq" OWNER TO smartsys;

--
-- TOC entry 3118 (class 0 OID 0)
-- Dependencies: 212
-- Name: value_thp_ID_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartsys
--

ALTER SEQUENCE public."value_thp_ID_seq" OWNED BY public.value_thp."ID";


--
-- TOC entry 213 (class 1259 OID 18831)
-- Name: value_thp_point_seq; Type: SEQUENCE; Schema: public; Owner: smartsys
--

CREATE SEQUENCE public.value_thp_point_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.value_thp_point_seq OWNER TO smartsys;

--
-- TOC entry 3119 (class 0 OID 0)
-- Dependencies: 213
-- Name: value_thp_point_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartsys
--

ALTER SEQUENCE public.value_thp_point_seq OWNED BY public.value_thp.point;


--
-- TOC entry 2889 (class 2604 OID 18833)
-- Name: clients ID; Type: DEFAULT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.clients ALTER COLUMN "ID" SET DEFAULT nextval('public."clients_ID_seq"'::regclass);


--
-- TOC entry 2894 (class 2604 OID 18834)
-- Name: point ID; Type: DEFAULT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.point ALTER COLUMN "ID" SET DEFAULT nextval('public."point_ID_seq"'::regclass);


--
-- TOC entry 2899 (class 2604 OID 18835)
-- Name: sensors ID; Type: DEFAULT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.sensors ALTER COLUMN "ID" SET DEFAULT nextval('public."sensors_ID_seq"'::regclass);


--
-- TOC entry 2907 (class 2604 OID 18836)
-- Name: trig ID; Type: DEFAULT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.trig ALTER COLUMN "ID" SET DEFAULT nextval('public."triggers_ID_seq"'::regclass);


--
-- TOC entry 2914 (class 2604 OID 18837)
-- Name: trig_act ID; Type: DEFAULT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.trig_act ALTER COLUMN "ID" SET DEFAULT nextval('public."trig_act_ID_seq"'::regclass);


--
-- TOC entry 2915 (class 2604 OID 18838)
-- Name: trig_act trig; Type: DEFAULT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.trig_act ALTER COLUMN trig SET DEFAULT nextval('public.trig_act_trig_seq'::regclass);


--
-- TOC entry 2919 (class 2604 OID 18839)
-- Name: value_thp ID; Type: DEFAULT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.value_thp ALTER COLUMN "ID" SET DEFAULT nextval('public."value_thp_ID_seq"'::regclass);


--
-- TOC entry 2920 (class 2604 OID 18840)
-- Name: value_thp point; Type: DEFAULT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.value_thp ALTER COLUMN point SET DEFAULT nextval('public.value_thp_point_seq'::regclass);


--
-- TOC entry 3120 (class 0 OID 0)
-- Dependencies: 201
-- Name: clients_ID_seq; Type: SEQUENCE SET; Schema: public; Owner: smartsys
--

SELECT pg_catalog.setval('public."clients_ID_seq"', 11, true);


--
-- TOC entry 3121 (class 0 OID 0)
-- Dependencies: 203
-- Name: point_ID_seq; Type: SEQUENCE SET; Schema: public; Owner: smartsys
--

SELECT pg_catalog.setval('public."point_ID_seq"', 1, true);


--
-- TOC entry 3122 (class 0 OID 0)
-- Dependencies: 205
-- Name: sensors_ID_seq; Type: SEQUENCE SET; Schema: public; Owner: smartsys
--

SELECT pg_catalog.setval('public."sensors_ID_seq"', 16, true);


--
-- TOC entry 3123 (class 0 OID 0)
-- Dependencies: 208
-- Name: trig_act_ID_seq; Type: SEQUENCE SET; Schema: public; Owner: smartsys
--

SELECT pg_catalog.setval('public."trig_act_ID_seq"', 14925, true);


--
-- TOC entry 3124 (class 0 OID 0)
-- Dependencies: 209
-- Name: trig_act_trig_seq; Type: SEQUENCE SET; Schema: public; Owner: smartsys
--

SELECT pg_catalog.setval('public.trig_act_trig_seq', 1, false);


--
-- TOC entry 3125 (class 0 OID 0)
-- Dependencies: 210
-- Name: triggers_ID_seq; Type: SEQUENCE SET; Schema: public; Owner: smartsys
--

SELECT pg_catalog.setval('public."triggers_ID_seq"', 2, true);


--
-- TOC entry 3126 (class 0 OID 0)
-- Dependencies: 212
-- Name: value_thp_ID_seq; Type: SEQUENCE SET; Schema: public; Owner: smartsys
--

SELECT pg_catalog.setval('public."value_thp_ID_seq"', 1, false);


--
-- TOC entry 3127 (class 0 OID 0)
-- Dependencies: 213
-- Name: value_thp_point_seq; Type: SEQUENCE SET; Schema: public; Owner: smartsys
--

SELECT pg_catalog.setval('public.value_thp_point_seq', 1, false);


--
-- TOC entry 2927 (class 2606 OID 18842)
-- Name: clients clients_address_key; Type: CONSTRAINT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_address_key UNIQUE (address);


--
-- TOC entry 2930 (class 2606 OID 18844)
-- Name: clients clients_pkey; Type: CONSTRAINT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY ("ID");


--
-- TOC entry 2932 (class 2606 OID 18846)
-- Name: point point_name_key; Type: CONSTRAINT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.point
    ADD CONSTRAINT point_name_key UNIQUE (name);


--
-- TOC entry 2934 (class 2606 OID 18848)
-- Name: point point_pkey; Type: CONSTRAINT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.point
    ADD CONSTRAINT point_pkey PRIMARY KEY ("ID");


--
-- TOC entry 2938 (class 2606 OID 18850)
-- Name: sensors sensor_name_key; Type: CONSTRAINT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.sensors
    ADD CONSTRAINT sensor_name_key UNIQUE (name);


--
-- TOC entry 2940 (class 2606 OID 18852)
-- Name: sensors sensor_pkey; Type: CONSTRAINT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.sensors
    ADD CONSTRAINT sensor_pkey PRIMARY KEY ("ID");


--
-- TOC entry 2942 (class 2606 OID 18854)
-- Name: sensors sensor_source_key; Type: CONSTRAINT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.sensors
    ADD CONSTRAINT sensor_source_key UNIQUE (source);


--
-- TOC entry 2953 (class 2606 OID 18856)
-- Name: trig_act trig_act_pkey; Type: CONSTRAINT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.trig_act
    ADD CONSTRAINT trig_act_pkey PRIMARY KEY ("ID");


--
-- TOC entry 2946 (class 2606 OID 18858)
-- Name: trig trig_name_key; Type: CONSTRAINT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.trig
    ADD CONSTRAINT trig_name_key UNIQUE (name);


--
-- TOC entry 2948 (class 2606 OID 18860)
-- Name: trig trig_pkey; Type: CONSTRAINT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.trig
    ADD CONSTRAINT trig_pkey PRIMARY KEY ("ID");


--
-- TOC entry 2950 (class 2606 OID 18862)
-- Name: trig trig_source_key; Type: CONSTRAINT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.trig
    ADD CONSTRAINT trig_source_key UNIQUE (source);


--
-- TOC entry 2955 (class 2606 OID 18864)
-- Name: value_thp value_thp_pkey; Type: CONSTRAINT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.value_thp
    ADD CONSTRAINT value_thp_pkey PRIMARY KEY ("ID");


--
-- TOC entry 2925 (class 1259 OID 18865)
-- Name: clients_address_index; Type: INDEX; Schema: public; Owner: smartsys
--

CREATE INDEX clients_address_index ON public.clients USING btree (address);


--
-- TOC entry 2928 (class 1259 OID 18866)
-- Name: clients_id_index; Type: INDEX; Schema: public; Owner: smartsys
--

CREATE INDEX clients_id_index ON public.clients USING btree ("ID");


--
-- TOC entry 2935 (class 1259 OID 18867)
-- Name: sensor_id_index; Type: INDEX; Schema: public; Owner: smartsys
--

CREATE INDEX sensor_id_index ON public.sensors USING btree ("ID");


--
-- TOC entry 2936 (class 1259 OID 18868)
-- Name: sensor_name_index; Type: INDEX; Schema: public; Owner: smartsys
--

CREATE INDEX sensor_name_index ON public.sensors USING btree (name);


--
-- TOC entry 2951 (class 1259 OID 18869)
-- Name: trig_act_id_index; Type: INDEX; Schema: public; Owner: smartsys
--

CREATE INDEX trig_act_id_index ON public.trig_act USING btree ("ID");


--
-- TOC entry 2943 (class 1259 OID 18870)
-- Name: trig_id_index; Type: INDEX; Schema: public; Owner: smartsys
--

CREATE INDEX trig_id_index ON public.trig USING btree ("ID");


--
-- TOC entry 2944 (class 1259 OID 18871)
-- Name: trig_name_index; Type: INDEX; Schema: public; Owner: smartsys
--

CREATE INDEX trig_name_index ON public.trig USING btree (name);


--
-- TOC entry 2958 (class 2620 OID 18872)
-- Name: trig_act t_act_alarm_alarm; Type: TRIGGER; Schema: public; Owner: smartsys
--

CREATE TRIGGER t_act_alarm_alarm BEFORE INSERT ON public.trig_act FOR EACH ROW EXECUTE FUNCTION public.trig_act_alarm();


--
-- TOC entry 2956 (class 2606 OID 18873)
-- Name: trig_act trig_act_trig_fkey; Type: FK CONSTRAINT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.trig_act
    ADD CONSTRAINT trig_act_trig_fkey FOREIGN KEY (trig) REFERENCES public.trig("ID") ON DELETE CASCADE;


--
-- TOC entry 2957 (class 2606 OID 18878)
-- Name: value_thp value_thp_point_fkey; Type: FK CONSTRAINT; Schema: public; Owner: smartsys
--

ALTER TABLE ONLY public.value_thp
    ADD CONSTRAINT value_thp_point_fkey FOREIGN KEY (point) REFERENCES public.point("ID") ON DELETE CASCADE;
