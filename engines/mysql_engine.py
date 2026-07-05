import pymysql


def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="@Huan1312",
        database="fahasa_db",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )


def search_by_keyword_and_filter(
    keyword="",
    max_price=None,
    category=None,
    publish_year=None
):

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    SELECT *
    FROM books
    WHERE (title LIKE %s OR author LIKE %s)
    """

    params = [
        f"%{keyword}%",
        f"%{keyword}%"
    ]

    if max_price is not None:
        sql += " AND current_price <= %s"
        params.append(max_price)

    if category:
        sql += " AND category_path LIKE %s"
        params.append(f"%{category}%")

    if publish_year:
        sql += " AND publish_year = %s"
        params.append(publish_year)

    sql += " LIMIT 50"

    cursor.execute(sql, params)

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result


def fetch_books_by_ids(ids):

    if not ids:
        return []

    conn = get_connection()
    cursor = conn.cursor()

    placeholders = ",".join(["%s"] * len(ids))

    sql = f"""
    SELECT *
    FROM books
    WHERE id IN ({placeholders})
    ORDER BY FIELD(id, {placeholders})
    """

    cursor.execute(sql, ids + ids)

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result
