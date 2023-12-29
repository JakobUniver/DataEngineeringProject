CREATE TABLE IF NOT EXISTS authors (
                                       author_id SERIAL PRIMARY KEY,
                                       first_name VARCHAR(256),
                                       middle_name VARCHAR(256),
                                       last_name VARCHAR(256),
                                       UNIQUE (first_name, middle_name, last_name)
);

CREATE TABLE IF NOT EXISTS categories (
                                          category_id SERIAL PRIMARY KEY,
                                          category_name VARCHAR(256) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS versions (
                                        version_id SERIAL PRIMARY KEY,
                                        version VARCHAR(64),
                                        created_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS papers (
                                      paper_id VARCHAR(64) PRIMARY KEY,
                                      title VARCHAR(1024) NOT NULL,
                                      submitter VARCHAR(256),
                                      comments VARCHAR(1024),
                                      journal_ref VARCHAR(1024),
                                      doi VARCHAR(1024),
                                      report_no VARCHAR(256),
                                      update_date DATE
);

CREATE TABLE IF NOT EXISTS paper_authors (
                                             paper_id VARCHAR(64),
                                             author_id INT,
                                             PRIMARY KEY (paper_id, author_id),
                                             FOREIGN KEY (paper_id) REFERENCES papers(paper_id),
                                             FOREIGN KEY (author_id) REFERENCES authors(author_id)
);

CREATE TABLE IF NOT EXISTS paper_categories (
                                                paper_id VARCHAR(64),
                                                category_id INT,
                                                PRIMARY KEY (paper_id, category_id),
                                                FOREIGN KEY (paper_id) REFERENCES papers(paper_id),
                                                FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

