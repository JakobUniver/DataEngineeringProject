-- Here are some example BI queries that could be run on the database

-- finding the most prolific authors
SELECT a.first_name, a.middle_name, a.last_name, COUNT(pa.paper_id) AS total_papers
FROM author a
         JOIN paper_author pa ON a.id = pa.author_id
GROUP BY a.id
ORDER BY total_papers DESC;

-- finding authors who collaborate frequently
SELECT a1.first_name || ' ' || a1.last_name AS author_1,
       a2.first_name || ' ' || a2.last_name AS author_2,
       COUNT(*) AS coauthored_papers
FROM paper_author pa1
         JOIN paper_author pa2 ON pa1.paper_id = pa2.paper_id AND pa1.author_id < pa2.author_id
         JOIN author a1 ON pa1.author_id = a1.id
         JOIN author a2 ON pa2.author_id = a2.id
GROUP BY author_1, author_2
ORDER BY coauthored_papers DESC;

-- finding most referenced papers
SELECT p.id, p.title, COUNT(pr.reference_id) AS reference_count
FROM paper p
         JOIN paper_reference pr ON p.id = pr.paper_id
GROUP BY p.id
ORDER BY reference_count DESC;

-- finding most popular categories
SELECT c.category_name, COUNT(pc.paper_id) AS paper_count
FROM category c
         JOIN paper_category pc ON c.id = pc.category_id
GROUP BY c.id
ORDER BY paper_count DESC;

-- finding categories that appear together frequently
SELECT c1.category_name AS category1, c2.category_name AS category2, COUNT(*) AS cooccurrence_count
FROM paper_category pc1
         JOIN paper_category pc2 ON pc1.paper_id = pc2.paper_id AND pc1.category_id < pc2.category_id
         JOIN category c1 ON pc1.category_id = c1.id
         JOIN category c2 ON pc2.category_id = c2.id
GROUP BY c1.category_name, c2.category_name
ORDER BY cooccurrence_count DESC;

