import psycopg2

def insert_references(cursor, references):
    reference_ids = []
    for reference in references:
        try:
            cursor.execute(
                """
                INSERT INTO reference (title, doi)
                VALUES (%s, %s)
                ON CONFLICT (title, doi)
                DO NOTHING 
                RETURNING id;
                """,
                reference
            )
            reference_id = cursor.fetchone()[0]
            reference_ids.append(reference_id)
        except psycopg2.Error as e:
            print(f"Error while inserting reference: {e}")
    return reference_ids

def insert_authors(cursor, authors_parsed):
    author_ids = []
    for author in authors_parsed:
        author_tuple = tuple(author + [""] * (3 - len(author)))
        print(author_tuple)
        try:
            cursor.execute(
                """
                INSERT INTO author (last_name, first_name, middle_name)
                VALUES (%s, %s, %s)
                ON CONFLICT (last_name, first_name, middle_name)
                DO UPDATE SET last_name = EXCLUDED.last_name
                RETURNING id;
                """,
                author_tuple
            )
            author_id = cursor.fetchone()[0]
            author_ids.append(author_id)
        except psycopg2.Error as e:
            print(f"Error while inserting authors: {e}")
    return author_ids


def insert_categories(cursor, categories):
    category_ids = []
    for category in categories:
        if category:
            try:
                cursor.execute(
                    """
                    INSERT INTO category (category_name)
                    VALUES (%s)
                    ON CONFLICT (category_name)
                    DO NOTHING
                    RETURNING id;
                    """,
                    category
                )
                result = cursor.fetchone()
                category_id = result[0] if result else None
                if category_id:
                    category_ids.append(category_id)
            except psycopg2.Error as e:
                print(f"Error while inserting categories: {e}")
    return category_ids


def load_data(cursor, record):
    try:
        authors_parsed = record.get('authors_parsed', [])
        categories = record.get('categories', '').split()
        references = record.get('references', [])
        author_ids = insert_authors(cursor, authors_parsed)
        category_ids = insert_categories(cursor, categories)
        reference_ids = insert_references(cursor, references)

        paper_id = record['id']
        cursor.execute(
            """
            INSERT INTO paper (id, title, submitter, comments, journal_ref, doi, report_no, update_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
            """,
            (paper_id, record.get('title'), record.get('submitter'), record.get('comments'),
             record.get('journal-ref'), record.get('doi'), record.get('report-no'),
             record.get('update_date'))
        )

        for author_id in author_ids:
            cursor.execute(
                "INSERT INTO paper_author (paper_id, author_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (paper_id, author_id)
            )

        for category_id in category_ids:
            cursor.execute(
                "INSERT INTO paper_category (paper_id, category_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (paper_id, category_id)
            )
        for reference_id in reference_ids:
            cursor.execute(
                "INSERT INTO paper_reference (paper_id, reference_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (paper_id, reference_id)
            )
    except psycopg2.Error as e:
        print(f"Database error occurred: {e}")

def connect():
    try:
        conn = psycopg2.connect(
            dbname='airflow',
            user='airflow',
            password='airflow',
            host='localhost',
            port='5532'
        )
        conn.autocommit = True
        cursor = conn.cursor()
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        exit(1)
    return cursor, conn