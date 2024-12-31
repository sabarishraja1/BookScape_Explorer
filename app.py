import streamlit as st
import psycopg2
import pandas as pd

# Replace with your PostgreSQL database credentials
host = "localhost"
user = "postgres"
password = "root"
database_name = "project"

# Database connection
def connect_to_db():
    try:
        conn_string = f"postgresql://{user}:{password}@{host}:5432/{database_name}"
        conn = psycopg2.connect(conn_string)
        return conn
    except psycopg2.OperationalError as error:
        st.error(f"Error connecting to database: {error}")
        return None

# Query execution
def query_data(query):
    conn = connect_to_db()
    if conn is None:
        return None, None
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]  # Fetch column names
            results = cur.fetchall()
            return columns, results
    except (Exception, psycopg2.Error) as error:
        st.error(f"An error occurred while executing the query: {error}")
        return None, None
    finally:
        conn.close()

# Insert data into database
def insert_data(book_data):
    conn = connect_to_db()
    if conn is None:
        return False
    try:
        with conn.cursor() as cur:
            query = """
            INSERT INTO books_datas(
                book_id, search_key, book_title, book_subtitle, book_authors, book_description,
                industryIdentifiers, text_readingModes, image_readingModes, pageCount, categories,
                language, imageLinks, ratingsCount, averageRating, country, saleability, isEbook,
                amount_listPrice, currencyCode_listPrice, amount_retailPrice, currencyCode_retailPrice,
                buyLink, year, publisher
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(query, tuple(book_data.values()))
            conn.commit()
        return True
    except Exception as error:
        st.error(f"Error inserting data: {error}")
        return False
    finally:
        conn.close()

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["Query Data", "Collect & Store Data"])

    if page == "Query Data":
        st.title("BookScape Explorer")
        
        # Query execution and display logic (from your original code)

        # Dropdown questions and their SQL queries (use your existing queries dictionary)
        questions_queries = {
        "1. Check Availability of eBooks vs Physical Books": 
            "SELECT isEbook, COUNT(*) AS count FROM books_datasGROUP BY isEbook;",
        "2. Find the Publisher with the Most Books Published": 
            "SELECT publisher, COUNT(*) AS book_count FROM books_datasGROUP BY publisher ORDER BY book_count DESC LIMIT 2;",
        "3. Identify the Publisher with the Highest Average Rating":
            "SELECT publisher, AVG(averageRating) AS avg_rating FROM books_datasGROUP BY publisher ORDER BY avg_rating DESC LIMIT 1;",
        "4. Get the Top 5 Most Expensive Books by Retail Price":
            "SELECT book_title, amount_retailPrice, currencyCode_retailPrice FROM books_datasORDER BY amount_retailPrice DESC LIMIT 5;",
        "5. Find Books Published After 2010 with at Least 500 Pages":
            "SELECT book_title, year, pageCount FROM books_datasWHERE year::INTEGER > 2010 AND pageCount >= 500;",
        "6. List Books with Discounts Greater than 20%":
            """SELECT book_title, 
                amount_listPrice, 
                amount_retailPrice, 
                CASE 
                    WHEN amount_listPrice > 0 THEN (amount_listPrice - amount_retailPrice) / amount_listPrice * 100
                    ELSE 0
                END AS discount_percentage 
            FROM books_datas
            WHERE amount_listPrice > 0 AND (amount_listPrice - amount_retailPrice) / amount_listPrice * 100 > 20;
            """,
        "7. Find the Average Page Count for eBooks vs Physical Books":
            "SELECT isEbook, AVG(pageCount) AS avg_page_count FROM books_datasGROUP BY isEbook;",
        "8. Find the Top 3 Authors with the Most Books":
            """SELECT UNNEST(STRING_TO_ARRAY(book_authors, ',')) AS author, COUNT(*) AS book_count 
               FROM books_datasGROUP BY author ORDER BY book_count DESC LIMIT 3;""",
        "9. List Publishers with More than 10 Books":
            "SELECT publisher, COUNT(*) AS book_count FROM books_datasGROUP BY publisher HAVING COUNT(*) > 10;",
        "10. Find the Average Page Count for Each Category":
            """SELECT UNNEST(STRING_TO_ARRAY(categories, ',')) AS category, AVG(pageCount) AS avg_page_count 
               FROM books_datasGROUP BY category;""",
        "11. Retrieve Books with More than 3 Authors":
            """SELECT book_title, book_authors 
               FROM books_datas
               WHERE ARRAY_LENGTH(STRING_TO_ARRAY(book_authors, ','), 1) > 3;""",
        "12. Books with Ratings Count Greater Than the Average":
            """SELECT book_title, ratingsCount 
               FROM books_datas
               WHERE ratingsCount > (SELECT AVG(ratingsCount) FROM books_data);""",
        "13. Books with the Same Author Published in the Same Year":
            """SELECT author, year, COUNT(*) AS book_count 
               FROM (SELECT UNNEST(STRING_TO_ARRAY(book_authors, ',')) AS author, year 
                     FROM books_data) subquery 
               GROUP BY author, year 
               HAVING COUNT(*) > 1;""",
        "14. Books with a Specific Keyword in the Title":
            "SELECT book_title, book_subtitle FROM books_datasWHERE book_title ILIKE '%keyword%';",
        "15. Year with the Highest Average Book Price":
            """SELECT year, AVG(amount_retailPrice) AS avg_price 
               FROM books_datas
               GROUP BY year 
               ORDER BY avg_price DESC LIMIT 1;""",
        "16. Count Authors Who Published 3 Consecutive Years":
            """SELECT author, COUNT(DISTINCT year) AS consecutive_years 
               FROM (SELECT UNNEST(STRING_TO_ARRAY(book_authors, ',')) AS author, year::INTEGER 
                     FROM books_data) subquery 
               GROUP BY author 
               HAVING MAX(year) - MIN(year) >= 2;""",
        "17. Authors Publishing in the Same Year with Different Publishers":
            """SELECT author, year, COUNT(DISTINCT publisher) AS publisher_count 
               FROM (SELECT UNNEST(STRING_TO_ARRAY(book_authors, ',')) AS author, year, publisher 
                     FROM books_data) subquery 
               GROUP BY author, year 
               HAVING COUNT(DISTINCT publisher) > 1;""",
        "18. Average Retail Price for eBooks vs Physical Books":
            """SELECT AVG(CASE WHEN isEbook THEN amount_retailPrice ELSE NULL END) AS avg_ebook_price, 
                      AVG(CASE WHEN NOT isEbook THEN amount_retailPrice ELSE NULL END) AS avg_physical_price 
               FROM books_data;""",
        "19. Books with Ratings More Than Two Standard Deviations from the Average":
            """WITH stats AS (
                   SELECT AVG(averageRating) AS avg_rating, STDDEV(averageRating) AS stddev_rating 
                   FROM books_data)
               SELECT book_title, averageRating, ratingsCount 
               FROM books_data, stats 
               WHERE averageRating > avg_rating + 2 * stddev_rating 
                  OR averageRating < avg_rating - 2 * stddev_rating;""",
        "20. Publisher with the Highest Average Rating (More Than 10 Books)":
            """SELECT publisher, AVG(averageRating) AS avg_rating, COUNT(*) AS book_count 
               FROM books_datas
               GROUP BY publisher 
               HAVING COUNT(*) > 10 
               ORDER BY avg_rating DESC LIMIT 10;"""
    }

  
        selected_question = st.selectbox("Select a question to execute:", ["Select a Query"] + list(questions_queries.keys()))

        if selected_question != "Select a Query":
            query = questions_queries[selected_question]
            columns, data = query_data(query)

            if data is not None:
                df = pd.DataFrame(data, columns=columns)
                st.write(f"### Results for: {selected_question}")
                st.dataframe(df)

    elif page == "Collect & Store Data":
        st.title("Collect & Store Book Data")

        # Input fields for book data
        book = {
            "book_id": st.text_input("Book ID"),
            "search_key": st.text_input("Search Key"),
            "book_title": st.text_input("Book Title"),
            "book_subtitle": st.text_input("Book Subtitle"),
            "book_authors": st.text_input("Book Authors (comma-separated)"),
            "book_description": st.text_area("Book Description"),
            "industryIdentifiers": st.text_input("Industry Identifiers (comma-separated)"),
            "text_readingModes": st.checkbox("Text Reading Mode"),
            "image_readingModes": st.checkbox("Image Reading Mode"),
            "pageCount": st.number_input("Page Count", min_value=0, step=1),
            "categories": st.text_input("Categories (comma-separated)"),
            "language": st.text_input("Language"),
            "imageLinks": st.text_input("Image Links"),
            "ratingsCount": st.number_input("Ratings Count", min_value=0, step=1),
            "averageRating": st.number_input("Average Rating", min_value=0.0, max_value=5.0, step=0.1),
            "country": st.text_input("Country"),
            "saleability": st.text_input("Saleability"),
            "isEbook": st.checkbox("Is eBook"),
            "amount_listPrice": st.number_input("List Price Amount", min_value=0.0, step=0.1),
            "currencyCode_listPrice": st.text_input("List Price Currency Code"),
            "amount_retailPrice": st.number_input("Retail Price Amount", min_value=0.0, step=0.1),
            "currencyCode_retailPrice": st.text_input("Retail Price Currency Code"),
            "buyLink": st.text_input("Buy Link"),
            "year": st.text_input("Year"),
            "publisher": st.text_input("Publisher"),
        }

        # Submit button to insert data
        if st.button("Submit Book Data"):
            success = insert_data(book)
            if success:
                st.success("Book data inserted successfully!")
            else:
                st.error("Failed to insert book data.")

if __name__ == "__main__":
    main()
