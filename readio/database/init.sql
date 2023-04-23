--这个东东现在用不了奥~
use readio_db;

-------------------------------------------------------------------------
--帖子
SET foreign_key_checks=0;
DROP Table if EXISTS posts;
SET foreign_key_checks=1;
create table posts(
    postID int primary key,
    postTitle TEXT not null,
    postAnswer TEXT,
    postTime DATE,
    postContent TEXT not null,
    postPopularity int default 0,
    remark TEXT
);

-------------------------------------------------------------------------
-- 标签
SET foreign_key_checks=0;
DROP Table if EXISTS tag;
SET foreign_key_checks=1;
CREATE TABLE tag(
    tagID INT PRIMARY KEY AUTO_INCREMENT,
    tagName VARCHAR(50) UNIQUE  NOT NULL,
    tagClass SMALLINT NOT NULL check(tagClass >= 1 and tagClass <= 3),
    tagParentName VARCHAR(50),
    tagPopularity INT default 0,
    remark TEXT,
    createTime datetime not null default current_timestamp
);

-------------------------------------------------------------------------
--帖子标签
DROP Table if EXISTS posts_tags;
create table posts_tags(
    postID int not null AUTO_INCREMENT,
    tagID int not null,
    primary key(postID,tagID),
    foreign key(postID) references posts(postID) on delete cascade on update cascade,
    foreign key(tagID) references tag(tagID) on delete cascade on update cascade
);


-------------------------------------------------------------------------
--帖子关键词
DROP Table if EXISTS posts_keywords;
create table posts_keywords(
    postID int not null,
    keyword VARCHAR(50) not null,
    primary key(postID,keyword),
    foreign key(postID) references posts(postID) on delete cascade on update cascade
); 

--------------------------------------------------------------------------
--定义触发器，维护完整性约束
drop trigger if EXISTS posts_tags_insert_tri ; 
create trigger posts_tags_insert_tri 
after insert on posts_tags 
for each row 
update tag set tagPopularity=(select count(*) as cnt from posts_tags where NEW.tagID=posts_tags.tagID group by NEW.tagID ) where tagID = NEW.tagID ;

drop trigger if EXISTS posts_tags_delete_tri ; 
create trigger posts_tags_delete_tri 
after delete on posts_tags 
for each row 
update tag set tagPopularity=(select count(*) as cnt from posts_tags where old.tagID=posts_tags.tagID  group by old.tagID ) where tagID = old.tagID ; 

-------------------------------------------------------------------------
--用户表
SET foreign_key_checks=0;
DROP Table if EXISTS user;
SET foreign_key_checks=1;

create table user( 
    uid int PRIMARY KEY AUTO_INCREMENT, 
    username varchar(50) not null UNIQUE, 
    nickname varchar(50) not null, 
    password TEXT not null, 
    roles varchar(8) not null , 
    email varchar(50), 
    phonenumber varchar(50), 
    avator TEXT, 
    createTime datetime not null  default CURRENT_TIMESTAMP 
); 


--用户会话表触发器
-- drop trigger if EXISTS user_token_insert_tri ; 
-- create trigger user_token_insert_tri 
-- before insert on user_token 
-- for each row 
-- delete from user_token where user_token.uid=new.uid; 

INSERT INTO user(username,nickname,password,roles) 
VALUES('admin','ruc', 
'pbkdf2:sha256:260000$twMVANMQb6phGZEV$bd84550842562a5e597c8f4eb57237ac5e7fda7f5177656447b5016a5f1d89c4','admin'); 

-------------------------------------------------------------------------

--文件
SET foreign_key_checks=0;
DROP Table if EXISTS file_info;
SET foreign_key_checks=1;
create table file_info(
	id varchar(128) PRIMARY KEY,
   name varchar(256) not null,
   type varchar(64) ,
   path varchar(128) not null,
   createTime datetime DEFAULT CURRENT_TIMESTAMP,
   visitTime datetime DEFAULT CURRENT_TIMESTAMP
);

--用户会话表
SET foreign_key_checks=0;
DROP Table if EXISTS user_token;
SET foreign_key_checks=1;
create table user_token(
    uid int not null,
    token VARCHAR(128) not null,
    createTime datetime not null  default CURRENT_TIMESTAMP,
    visitTime datetime not null default CURRENT_TIMESTAMP ,
    PRIMARY key(uid,token),
    foreign key(uid) references user(uid) on delete cascade on update cascade
);