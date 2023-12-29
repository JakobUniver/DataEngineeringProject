import psycopg2

def insert_authors(cursor, authors_parsed):
    author_ids = []
    for author in authors_parsed:
        author_tuple = tuple(author + [""] * (3 - len(author)))
        print(author_tuple)
        try:
            cursor.execute(
                """
                INSERT INTO authors (last_name, first_name, middle_name)
                VALUES (%s, %s, %s)
                ON CONFLICT (last_name, first_name, middle_name)
                DO UPDATE SET last_name = EXCLUDED.last_name
                RETURNING author_id;
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
                    INSERT INTO categories (category_name)
                    VALUES (%s)
                    ON CONFLICT (category_name)
                    DO NOTHING
                    RETURNING category_id;
                    """,
                    (category,)
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
        author_ids = insert_authors(cursor, authors_parsed)
        category_ids = insert_categories(cursor, categories)

        paper_id = record['id']
        cursor.execute(
            """
            INSERT INTO papers (paper_id, title, submitter, comments, journal_ref, doi, report_no, abstract, update_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (paper_id) DO NOTHING;
            """,
            (paper_id, record.get('title'), record.get('submitter'), record.get('comments'),
             record.get('journal-ref'), record.get('doi'), record.get('report-no'),
             record.get('abstract'), record.get('update_date'))
        )

        for author_id in author_ids:
            cursor.execute(
                "INSERT INTO paper_authors (paper_id, author_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (paper_id, author_id)
            )

        for category_id in category_ids:
            cursor.execute(
                "INSERT INTO paper_categories (paper_id, category_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (paper_id, category_id)
            )
    except psycopg2.Error as e:
        print(f"Database error occurred: {e}")

def connect():
    try:
        conn = psycopg2.connect(
            dbname='dataeng',
            user='postgres',
            password='postgres',
            host='localhost',
            port='5532'
        )
        conn.autocommit = True
        cursor = conn.cursor()
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        exit(1)
    return cursor, conn