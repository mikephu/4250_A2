-- Table: public.category

-- DROP TABLE IF EXISTS "public".category;

CREATE TABLE IF NOT EXISTS "public".category
(
    category_id integer NOT NULL,
    name character varying COLLATE pg_catalog."default",
    CONSTRAINT category_pkey PRIMARY KEY (category_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "public".category
    OWNER to postgres;

-- Table: public.document

-- DROP TABLE IF EXISTS "public".document;

CREATE TABLE IF NOT EXISTS "public".document
(
    doc_number integer NOT NULL,
    category_id integer,
    text character varying COLLATE pg_catalog."default",
    title character varying COLLATE pg_catalog."default",
    num_chars integer,
    date character varying COLLATE pg_catalog."default",
    CONSTRAINT document_pkey PRIMARY KEY (doc_number),
    CONSTRAINT document_category FOREIGN KEY (category_id)
        REFERENCES "public".category (category_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "public".document
    OWNER to postgres;

-- Table: public.term

-- DROP TABLE IF EXISTS "public".term;

CREATE TABLE IF NOT EXISTS "public".term
(
    term character varying COLLATE pg_catalog."default" NOT NULL,
    num_chars integer,
    CONSTRAINT term_pkey PRIMARY KEY (term)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "public".term
    OWNER to postgres;

-- Table: public.index

-- DROP TABLE IF EXISTS "public".index;

CREATE TABLE IF NOT EXISTS "public".index
(
    doc_number integer NOT NULL,
    term character varying COLLATE pg_catalog."default" NOT NULL,
    count integer,
    CONSTRAINT index_pkey PRIMARY KEY (doc_number, term)
        INCLUDE(doc_number, term),
    CONSTRAINT docnum FOREIGN KEY (doc_number)
        REFERENCES "public".document (doc_number) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT term FOREIGN KEY (term)
        REFERENCES "public".term (term) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "public".index
    OWNER to postgres;

CREATE INDEX IF NOT EXISTS fki_term
    ON "public".index USING btree
    (term COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;