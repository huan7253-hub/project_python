CREATE DATABASE IF NOT EXISTS fahasa_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE fahasa_db;

CREATE TABLE books (
    id INT PRIMARY KEY,

    link TEXT,
    title TEXT,
    category_path TEXT,

    author VARCHAR(255),
    publisher VARCHAR(255),

    publish_year INT,
    page_count INT,

    current_price INT,
    old_price INT,

    description LONGTEXT
);
