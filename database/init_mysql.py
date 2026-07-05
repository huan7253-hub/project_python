import os
import pandas as pd
import pymysql

BASE_DIR = os.path.dirname(__file__)

CSV_PATH = os.path.join(
    BASE_DIR,
    "..",
    "Data",
    "books_clean.csv"
)
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="@Huan1312",
    database="fahasa_db",
    charset="utf8mb4"
)

cursor = conn.cursor()


df = pd.read_csv(CSV_PATH)

data = list(
    df[
        [
            "id",
            "link",
            "title",
            "category_path",
            "author",
            "publisher",
            "publish_year",
            "page_count",
            "current_price",
            "old_price",
            "description",
        ]
    ].itertuples(index=False, name=None)
)


sql = """
INSERT INTO books (
    id,
    link,
    title,
    category_path,
    author,
    publisher,
    publish_year,
    page_count,
    current_price,
    old_price,
    description
)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""


cursor.executemany(sql, data)

conn.commit()

print(f"Imported {len(data)} books successfully!")

cursor.close()
conn.close()
