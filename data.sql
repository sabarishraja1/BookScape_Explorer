
select * from books_datas

SELECT publisher, 
 from books_data;


1. Check Availability of eBooks vs Physical Books


SELECT 
    isEbook, 
    COUNT(*) AS count 
FROM books_datas
GROUP BY isEbook;


2. Find the Publisher with the Most Books Published


SELECT publisher, 
    COUNT(*) AS book_count 
FROM books_datas 
GROUP BY publisher 
ORDER BY book_count DESC 
LIMIT 2;


3. Identify the Publisher with the Highest Average Rating


SELECT publisher, AVG(averageRating) AS avg_rating 
FROM books_datas 
GROUP BY publisher 
ORDER BY avg_rating DESC 
LIMIT 1;


4. Get the Top 5 Most Expensive Books by Retail Price


SELECT 
    book_title, 
    amount_retailPrice, 
    currencyCode_retailPrice 
FROM books_datas
ORDER BY amount_retailPrice DESC 
LIMIT 5;


5. Find Books Published After 2010 with at Least 500 Pages


SELECT 
    book_title, 
    year, 
    pageCount 
FROM books_data
WHERE year::INTEGER > 2010 AND pageCount >= 500;


6. List Books with Discounts Greater than 20%


-- SELECT 
--     book_title, 
--     amount_listPrice, 
--     amount_retailPrice, 
--     (amount_listPrice - amount_retailPrice) / amount_listPrice * 100 AS discount_percentage 
-- FROM books_datas
-- WHERE (amount_listPrice - amount_retailPrice) / amount_listPrice * 100 > 20;

SELECT 
    book_title, 
    amount_listPrice, 
    amount_retailPrice, 
    CASE 
        WHEN amount_listPrice > 0 THEN (amount_listPrice - amount_retailPrice) / amount_listPrice * 100
        ELSE 0
    END AS discount_percentage 
FROM books_datas
WHERE amount_listPrice > 0 AND (amount_listPrice - amount_retailPrice) / amount_listPrice * 100 > 20;



7. Find the Average Page Count for eBooks vs Physical Books


SELECT 
    isEbook, 
    AVG(pageCount) AS avg_page_count 
FROM books_datas
GROUP BY isEbook;


8. Find the Top 3 Authors with the Most Books


SELECT 
    UNNEST(STRING_TO_ARRAY(book_authors, ',')) AS author, 
    COUNT(*) AS book_count 
FROM books_data
GROUP BY author 
ORDER BY book_count DESC 
LIMIT 3;


9. List Publishers with More than 10 Books


SELECT 
    publisher, 
    COUNT(*) AS book_count 
FROM books_datas
GROUP BY publisher 
HAVING COUNT(*) > 10;

10. Find the Average Page Count for Each Category


SELECT 
    UNNEST(STRING_TO_ARRAY(categories, ',')) AS category, 
    AVG(pageCount) AS avg_page_count 
FROM books_datas
GROUP BY category;


11. Retrieve Books with More than 3 Authors


SELECT 
    book_title, 
    book_authors 
FROM books_data
WHERE ARRAY_LENGTH(STRING_TO_ARRAY(book_authors, ','), 1) > 3;


12. Books with Ratings Count Greater Than the Average


SELECT 
    book_title, 
    ratingsCount 
FROM books_datas
WHERE ratingsCount > (SELECT AVG(ratingsCount) FROM books);


13. Books with the Same Author Published in the Same Year


SELECT 
    author, 
    year, 
    COUNT(*) AS book_count 
FROM (
    SELECT 
        UNNEST(STRING_TO_ARRAY(book_authors, ',')) AS author, 
        year 
    FROM books_data
) subquery
GROUP BY author, year 
HAVING COUNT(*) > 1;


14. Books with a Specific Keyword in the Title


SELECT 
    book_title, 
    book_subtitle 
FROM books_datas
WHERE book_title ILIKE '%keyword%';


15. Year with the Highest Average Book Price


SELECT 
    year, 
    AVG(amount_retailPrice) AS avg_price 
FROM books_data
GROUP BY year 
ORDER BY avg_price DESC 
LIMIT 1;


16. Count Authors Who Published 3 Consecutive Years


SELECT 
    author, 
    COUNT(DISTINCT year) AS consecutive_years 
FROM (
    SELECT 
        UNNEST(STRING_TO_ARRAY(book_authors, ',')) AS author, 
        year::INTEGER 
    FROM books_data
) subquery
GROUP BY author 
HAVING MAX(year) - MIN(year) >= 2;


17. Authors Publishing in the Same Year with Different Publishers


SELECT 
    author, 
    year, 
    COUNT(DISTINCT publisher) AS publisher_count 
FROM (
    SELECT 
        UNNEST(STRING_TO_ARRAY(book_authors, ',')) AS author, 
        year, 
        publisher 
    FROM books_data
) subquery
GROUP BY author, year 
HAVING COUNT(DISTINCT publisher) > 1;


18. Average Retail Price for eBooks vs Physical Books


SELECT 
    AVG(CASE WHEN isEbook THEN amount_retailPrice ELSE NULL END) AS avg_ebook_price, 
    AVG(CASE WHEN NOT isEbook THEN amount_retailPrice ELSE NULL END) AS avg_physical_price 
FROM books_data;


19. Books with Ratings More Than Two Standard Deviations from the Average


WITH stats AS (
    SELECT 
        AVG(averageRating) AS avg_rating, 
        STDDEV(averageRating) AS stddev_rating 
    FROM books_data
)
SELECT 
    book_title, 
    averageRating, 
    ratingsCount 
FROM books_data, stats 
WHERE averageRating > avg_rating + 2 * stddev_rating 
   OR averageRating < avg_rating - 2 * stddev_rating;
   
   
20. Publisher with the Highest Average Rating (More Than 10 Books)


SELECT 
    publisher, 
    AVG(averageRating) AS avg_rating, 
    COUNT(*) AS book_count 
FROM books_datas
GROUP BY publisher 
HAVING COUNT(*) > 10 
ORDER BY avg_rating DESC 
LIMIT 1;

