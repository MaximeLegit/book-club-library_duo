drop table if exists book_authors;
drop table if exists loans;
drop table if exists members;
drop table if exists books;
drop table if exists authors;

create table members(
	member_id	integer primary KEY,
	first_name	text NOT NULL,
	last_name	text NOT NULL,
	email		text NOT NULL UNIQUE
);

create table authors(
	author_id	integer primary KEY,
	name		text NOT NULL
);

create table books(
	book_id		integer primary KEY,
	title		text NOT NULL,
    year		integer check (year > 0)
);

create table loans(
	loan_id    	integer primary KEY,
	member_id	integer NOT NULL,
	book_id    	integer NOT NULL,
	loan_date  	TEXT DEFAULT (date('now')),
	due_date   	TEXT DEFAULT (date('now', '+14 days')),
	return_date	TEXT,
    foreign key (member_id) references members(member_id),
	foreign key (book_id) references books(book_id)
);

create table book_authors(
	book_id		integer NOT NULL,
    author_id	integer NOT NULL,
    primary key (book_id, author_id),
	foreign key (book_id) references books(book_id),
	foreign key (author_id) references authors(author_id)
);

