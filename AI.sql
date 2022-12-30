CREATE TABLE IF NOT EXISTS author (author_id int AUTO_INCREMENT , author_name varchar(255), email varchar(255), password varchar(16), reviewer_role varchar(255), PRIMARY KEY(author_id))

CREATE TABLE IF NOT EXISTS discourse (discourse_id int NOT NULL AUTO_INCREMENT, author_id int, no_sentences int, domain varchar(255), create_date datetime default now(), other_attributes VARCHAR(255), sentences VARCHAR(255),PRIMARY KEY (discourse_id),FOREIGN KEY (author_id) REFERENCES author(author_id))

CREATE TABLE IF NOT EXISTS usr (author_id int,  discourse_id int, sentence_id int ,USR_ID int NOT NULL AUTO_INCREMENT, orignal_USR_json JSON,final_USR json,create_date datetime default now(),USR_status varchar(255),FOREIGN KEY (sentence_id) REFERENCES discourse (discourse_id) ,FOREIGN KEY (discourse_id) REFERENCES discourse(discourse_id),FOREIGN KEY (author_id) REFERENCES author(author_id), PRIMARY KEY (USR_ID))

CREATE TABLE IF NOT EXISTS USR_review (USR_id int,  reviewer_id int, review_status varchar(255) , review_date datetime default now(),change_note vrchar(255), FOREIGN KEY (USR_id) REFERENCES usr (USR_id) ,FOREIGN KEY (discourse_id) REFERENCES discourse(discourse_id))