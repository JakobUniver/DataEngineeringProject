CREATE TABLE IF NOT EXISTS author (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(256),
    middle_name VARCHAR(256),
    last_name VARCHAR(256),
    UNIQUE (first_name, middle_name, last_name)
);

CREATE TABLE IF NOT EXISTS category (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(256) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS version (
    id SERIAL PRIMARY KEY,
    version VARCHAR(64),
    created_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS paper (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(1024) NOT NULL,
    submitter VARCHAR(256),
    comments VARCHAR(1024),
    journal_ref VARCHAR(1024),
    doi VARCHAR(1024),
    report_no VARCHAR(256),
    update_date DATE,
    version_id INT,
    FOREIGN KEY (version_id) REFERENCES version(id)
);

CREATE TABLE IF NOT EXISTS paper_author (
    paper_id VARCHAR(64),
    author_id INT,
    PRIMARY KEY (paper_id, author_id),
    FOREIGN KEY (paper_id) REFERENCES paper(id),
    FOREIGN KEY (author_id) REFERENCES author(id)
);

CREATE TABLE IF NOT EXISTS paper_category (
    paper_id VARCHAR(64),
    category_id INT,
    PRIMARY KEY (paper_id, category_id),
    FOREIGN KEY (paper_id) REFERENCES paper(id),
    FOREIGN KEY (category_id) REFERENCES category(id)
);

CREATE TABLE IF NOT EXISTS paper_reference (
    paper_id VARCHAR(64),
    reference_id INT,
    PRIMARY KEY (paper_id, reference_id),
    FOREIGN KEY (paper_id) REFERENCES paper(id),
    FOREIGN KEY (reference_id) REFERENCES reference(id)
);

CREATE TABLE IF NOT EXISTS reference (
    id SERIAL PRIMARY KEY,
    title VARCHAR(1024) NOT NULL,
    doi VARCHAR(1024) UNIQUE NOT NULL
 );