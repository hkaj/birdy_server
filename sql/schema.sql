SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;
SET search_path = public, pg_catalog;
SET default_tablespace = '';
SET default_with_oids = false;

-- Name: liensUtilisateurs; Type: TABLE; Schema: public; Owner: birdy_admin
CREATE TABLE liensUtilisateurs (
    id_lien integer NOT NULL,
    login_user_1 character varying,
    login_user_2 character varying,
    type character varying(20) DEFAULT 'proche'::character varying,
    status boolean
);

ALTER TABLE liensUtilisateurs OWNER TO birdy_admin;


-- Name: liensUtilisateurs_id_lien_seq; Type: SEQUENCE; Schema: public; Owner: birdy_admin
CREATE SEQUENCE liensUtilisateurs_id_lien_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;

ALTER SEQUENCE liensUtilisateurs_id_lien_seq OWNER TO birdy_admin;
ALTER SEQUENCE liensUtilisateurs_id_lien_seq OWNED BY liensUtilisateurs.id_lien;

SELECT pg_catalog.setval('liensUtilisateurs_id_lien_seq', 1, false);


-- Name: position; Type: TABLE; Schema: public; Owner: birdy_admin
CREATE TABLE position (
    id_position integer NOT NULL,
    login_user character varying NOT NULL,
    latitude double precision,
    longitude double precision,
    vit double precision,
    acc double precision,
    last_update timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE public.position OWNER TO birdy_admin;


-- Name: position_id_position_seq; Type: SEQUENCE; Schema: public; Owner: birdy_admin
CREATE SEQUENCE position_id_position_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;

ALTER SEQUENCE position_id_position_seq OWNER TO birdy_admin;
ALTER SEQUENCE position_id_position_seq OWNED BY position.id_position;

SELECT pg_catalog.setval('position_id_position_seq', 6, true);

-- Name: utilisateur; Type: TABLE; Schema: public; Owner: birdy_admin; Tablespace: 
CREATE TABLE utilisateur (
    id_user integer NOT NULL,
    login_user character varying NOT NULL,
    password character varying NOT NULL,
    nom character varying,
    prenom character varying,
    numero_tel character varying(14),
    e_mail character varying,
    numero_tel_sec character varying(14)
);

ALTER TABLE public.utilisateur OWNER TO birdy_admin;


-- Name: utilisateur_id_user_seq; Type: SEQUENCE; Schema: public; Owner: birdy_admin
CREATE SEQUENCE utilisateur_id_user_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;

ALTER SEQUENCE utilisateur_id_user_seq OWNER TO birdy_admin;
ALTER SEQUENCE utilisateur_id_user_seq OWNED BY utilisateur.id_user;

SELECT pg_catalog.setval('utilisateur_id_user_seq', 7, true);


ALTER TABLE liensUtilisateurs
    ALTER COLUMN id_lien SET DEFAULT nextval('liensUtilisateurs_id_lien_seq'::regclass);

ALTER TABLE position
    ALTER COLUMN id_position SET DEFAULT nextval('position_id_position_seq'::regclass);

ALTER TABLE utilisateur
    ALTER COLUMN id_user SET DEFAULT nextval('utilisateur_id_user_seq'::regclass);


-- Data for Name: utilisateur; Type: TABLE DATA; Schema: public; Owner: birdy_admin
INSERT INTO utilisateur (login_user, password) VALUES ('hkaj', 'foo');
INSERT INTO utilisateur (login_user, password) VALUES ('mdaragon', 'bar');
INSERT INTO utilisateur (login_user, password) VALUES ('avolle', 'foobar');

-- Data for liensUtilisateurs
INSERT INTO liensUtilisateurs (login_user_1, login_user_2, status) VALUES ('hkaj', 'mdaragon', true);
INSERT INTO liensUtilisateurs (login_user_1, login_user_2, status) VALUES ('hkaj', 'avolle', true);
INSERT INTO liensUtilisateurs (login_user_1, login_user_2, status) VALUES ('mdaragon', 'hkaj', true);
INSERT INTO liensUtilisateurs (login_user_1, login_user_2, status) VALUES ('mdaragon', 'avolle', true);
INSERT INTO liensUtilisateurs (login_user_1, login_user_2, status) VALUES ('avolle', 'hkaj', true);
INSERT INTO liensUtilisateurs (login_user_1, login_user_2, status) VALUES ('avolle', 'mdaragon', true);

-- Data for position
INSERT INTO position (login_user, latitude, longitude, vit, acc, last_update)
VALUES (
    'hkaj',
    '49.463999999999999',
    '2.1099999999999999',
    '3.3999999999999999',
    '1',
    '2013-05-07 17:41:28.339+02'
);

-- Name: liensUtilisateurs_pkey; Type: CONSTRAINT; Schema: public; Owner: birdy_admin; Tablespace: 
ALTER TABLE ONLY liensUtilisateurs
    ADD CONSTRAINT liensUtilisateurs_pkey PRIMARY KEY (id_lien);


-- Name: position_login_user_key; Type: CONSTRAINT; Schema: public; Owner: birdy_admin; Tablespace: 
ALTER TABLE ONLY position
    ADD CONSTRAINT position_login_user_key UNIQUE (login_user);


-- Name: position_pkey; Type: CONSTRAINT; Schema: public; Owner: birdy_admin; Tablespace: 
ALTER TABLE ONLY position
    ADD CONSTRAINT position_pkey PRIMARY KEY (id_position);


-- Name: utilisateur_login_user_key; Type: CONSTRAINT; Schema: public; Owner: birdy_admin; Tablespace: 
ALTER TABLE ONLY utilisateur
    ADD CONSTRAINT utilisateur_login_user_key UNIQUE (login_user);


-- Name: utilisateur_pkey; Type: CONSTRAINT; Schema: public; Owner: birdy_admin; Tablespace: 
ALTER TABLE ONLY utilisateur
    ADD CONSTRAINT utilisateur_pkey PRIMARY KEY (id_user);

-- Name: public; Type: ACL; Schema: -; Owner: postgres
REVOKE ALL PRIVILEGES ON SCHEMA public FROM PUBLIC;
REVOKE ALL PRIVILEGES ON SCHEMA public FROM postgres;
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA public TO birdy_admin;
