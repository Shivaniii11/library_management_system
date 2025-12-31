create database week05;
use week05;


CREATE TABLE IF NOT EXISTS books1 (
    book_id INTEGER PRIMARY KEY auto_increment,
    title varchar(100) NOT NULL,
    author varchar(100) NOT NULL,
    category varchar(100),
    total_copies INTEGER CHECK(total_copies >= 0),
    available_copies INTEGER CHECK(available_copies >= 0)
);

CREATE TABLE IF NOT EXISTS members1 (
    member_id INTEGER PRIMARY KEY auto_increment,
    name varchar(100) NOT NULL,
    email varchar(100) UNIQUE NOT NULL,
    join_date DATE NOT NULL,
    status varchar(100) CHECK(status IN ('active', 'inactive')) NOT NULL
);

CREATE TABLE IF NOT EXISTS book_issues1 (
    issue_id INTEGER PRIMARY KEY auto_increment,
    book_id INTEGER,
    member_id INTEGER,
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    FOREIGN KEY (book_id) REFERENCES books1(book_id),
    FOREIGN KEY (member_id) REFERENCES members1(member_id)
);

select * from books1;

select * from members1;

select * from book_issues1;
