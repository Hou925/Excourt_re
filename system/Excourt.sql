-- 要和学校数据库匹配，学号和姓名还有密码
CREATE TABLE Student (
    Student_id INT PRIMARY KEY,                         -- 学生学号
    Student_name VARCHAR(50) NOT NULL,                  -- 学生姓名
    Student_phone VARCHAR(50),                          -- 学生电话
    Student_password VARCHAR(50) NOT NULL,              -- 学生密码
    Student_profileurl VARCHAR(255) DEFAULT NULL,       -- 学生头像图片url
    Student_nickname VARCHAR(255) NOT NULL,             -- 学生昵称
    Student_credit INT DEFAULT 100,                     -- 学生信用分
    Student_level INT,                                  -- 学生等级
    Student_status INT                                  -- 学生状态
);

CREATE TABLE CourtInfo (
    Court_id VARCHAR(50) PRIMARY KEY,                                             -- 场地ID（校区-年-月-日-时间段-场地号拼接而成）
    Court_campus ENUM('JiaDing','SiPing','Huxi','HuBei') DEFAULT 'JiaDing',       -- 场地所属校区
    Court_date DATE NOT NULL,                                                     -- 场地日期
    Court_time INT NOT NULL,                                                      -- 场地时间段（0-12）
    Court_no VARCHAR(50) NOT NULL,                                                -- 场地号
    Court_state ENUM('not_owned','owned') NOT NULL DEFAULT 'not_owned',           -- 场地状态
    Court_owner INT,                                                              -- 场地拥有者
    Court_qrcodeurl VARCHAR(255),                                                 -- 场地码的URL
    FOREIGN KEY (Court_owner) REFERENCES Student(Student_id)
);

CREATE TABLE Exchangecourt_upload (
    Exchange_upload_id INT AUTO_INCREMENT PRIMARY KEY,                                                                               -- 交换场地发布id
    Exchange_uploader_id INT NOT NULL,                                                                                               -- 交换场地发布者学号
    Exchange_upload_state ENUM('not_responsed','responsed','exchanged','retrieved') NOT NULL DEFAULT 'not_responsed',                -- 场地交换状态（无相应，有人相应，已经交换，已撤回）
    Exchange_uploaded_court_id VARCHAR(50) NOT NULL,                                                                                 -- 交换的场地id
    Exchange_upload_time DATETIME,                                                                                                   -- 场地交换发起时间
    FOREIGN KEY (Exchange_uploader_id) REFERENCES Student(Student_id),
    FOREIGN KEY (Exchange_uploaded_court_id) REFERENCES CourtInfo(Court_id)
);

CREATE TABLE Exchangecourt_record (
    Exchange_record_id INT AUTO_INCREMENT PRIMARY KEY,       -- 交换场地记录
    Exchange_uploader_id INT NOT NULL,                       -- 场地交换者学号
    Exchange_responser_id INT NOT NULL,                      -- 场地交换响应者学号
    Exchange_state ENUM('not_responsed','exchanged','retrieved') DEFAULT 'not_responsed' NOT NULL,            -- 场地交换状态
    Exchange_uploader_court_id VARCHAR(50) NOT NULL,         -- 被交换的场地id
    Exchange_responser_court_id VARCHAR(50) NOT NULL,        -- 响应者的场地id
    Exchange_uploader_score DOUBLE DEFAULT 5.0,              -- 场地发布者分数
    Exchange_responser_score DOUBLE DEFAULT 5.0,             -- 场地响应者分数
    FOREIGN KEY (Exchange_uploader_id) REFERENCES Student(Student_id),
    FOREIGN KEY (Exchange_responser_id) REFERENCES Student(Student_id),
    FOREIGN KEY (Exchange_uploader_court_id) REFERENCES CourtInfo(Court_id),
    FOREIGN KEY (Exchange_responser_court_id) REFERENCES CourtInfo(Court_id)
);

CREATE TABLE Offercourt_upload (
    Offer_upload_id INT AUTO_INCREMENT PRIMARY KEY,         -- 送场发布记录id
    Offer_uploader_id INT NOT NULL,                         -- 送场发布者学号
    Offer_upload_state ENUM('not_responsed','responsed','offered','retrieved') DEFAULT 'not_responsed' NOT NULL,                                 -- 送场发布状态
    Offer_uploaded_court_id VARCHAR(50) NOT NULL,           -- 送场场地id
    Offer_upload_time DATETIME,                             -- 送场发布时间
    FOREIGN KEY (Offer_uploader_id) REFERENCES Student(Student_id),
    FOREIGN KEY (Offer_uploaded_court_id) REFERENCES CourtInfo(Court_id)
);

CREATE TABLE Offercourt_record (
    Offer_record_id INT AUTO_INCREMENT PRIMARY KEY,         -- 送场记录id
    Offer_uploader_id INT NOT NULL,                         -- 送场发布者学号
    Offer_responser_id INT NOT NULL,                        -- 送场响应者学号
    Offer_state ENUM('not_responsed','offered','retrieved') DEFAULT 'not_responsed' NOT NULL,                                        -- 送场状态
    Offer_uploader_court_id VARCHAR(50) NOT NULL,           -- 送场场地id
    FOREIGN KEY (Offer_uploader_id) REFERENCES Student(Student_id),
    FOREIGN KEY (Offer_responser_id) REFERENCES Student(Student_id),
    FOREIGN KEY (Offer_uploader_court_id) REFERENCES CourtInfo(Court_id)
);

CREATE TABLE Teamup_upload (
    Teamup_upload_id INT AUTO_INCREMENT PRIMARY KEY,        -- 组队拼场发布记录id
    Teamup_uploader_id INT NOT NULL,                        -- 组队拼场发布者学号
    Teamup_court_id VARCHAR(50) NOT NULL,                   -- 组队场地id
    Teamup_max_num INT DEFAULT 3,                           -- 组队最大人数
    Teamup_upload_state ENUM('not_responsed','responsed','full','retrieved') DEFAULT 'not_responsed' NOT NULL,                                -- 组队发布状态
    Teamup_upload_time DATETIME NOT NULL,                   -- 组队发布时间
    FOREIGN KEY (Teamup_uploader_id) REFERENCES Student(Student_id),
    FOREIGN KEY (Teamup_court_id) REFERENCES CourtInfo(Court_id)
);


CREATE TABLE Teamup_request_record (
    Teamup_request_id INT AUTO_INCREMENT PRIMARY KEY,      -- 组队请求记录id
    Teamup_requester_id INT NOT NULL,                      -- 组队响应者学号
    Teamup_uploader_id INT NOT NULL,                       -- 组队发布者的学号
    Teamup_court_id VARCHAR(50) NOT NULL,                  -- 组队场地id
    Teamup_request_state ENUM('not_responsed','responsed','retrieved') DEFAULT 'not_responsed' NOT NULL,                              -- 组队请求状态
    FOREIGN KEY (Teamup_requester_id) REFERENCES Student(Student_id),
    FOREIGN KEY (Teamup_uploader_id) REFERENCES Student(Student_id),
    FOREIGN KEY (Teamup_court_id) REFERENCES CourtInfo(Court_id)
);

-- 用于用户发布自己丢失了某件物品
CREATE TABLE MyLost (
    Lost_id INT AUTO_INCREMENT PRIMARY KEY,        -- 丢失记录id号
    Lost_uploader_id INT NOT NULL,                 -- 丢失记录发布者学号
    Lost_item_name VARCHAR(255),                   -- 丢失物品名称
    Lost_description VARCHAR(1000),                -- 丢失物品描述
    Lost_position VARCHAR(255),                    -- 丢失位置描述
    Lost_time DATETIME,                            -- 丢失时间
    Lost_contact VARCHAR(255),                     -- 丢失者联系方式
    Lost_item_pic_url VARCHAR(255),                -- 丢失物品照片url
    FOREIGN KEY (Lost_uploader_id) REFERENCES Student(Student_id)
);

-- 用于用户发布自己找到的物品
CREATE TABLE MyFound (
    Found_id INT AUTO_INCREMENT PRIMARY KEY,       -- 找到丢失物品记录的id号
    Found_uploader_id INT NOT NULL,                -- 找到物品记录发布者
    Found_item_name VARCHAR(255),                  -- 找到物品名称
    Found_description VARCHAR(1000),               -- 找到物品描述
    Found_position VARCHAR(255),                   -- 找到位置
    Found_time DATETIME,                           -- 找到时间
    Found_contact VARCHAR(255),                    -- 找到者联系方式
    Found_item_pic_url VARCHAR(255),               -- 找到物品照片url
    FOREIGN KEY (Found_uploader_id) REFERENCES Student(Student_id)
);

CREATE TABLE ConversationInfo (
    Conversation_id BIGINT AUTO_INCREMENT PRIMARY KEY,  -- 聊天记录ID
    Sender_id INT NOT NULL,                             -- 发送者学号
    Receiver_id INT NOT NULL,                           -- 接收者学号
    Message_sent TEXT,                                  -- 聊天消息内容
    Message_type ENUM('text', 'image') DEFAULT 'text',  -- 消息类型
    Pic_url VARCHAR(500) DEFAULT NULL,                  -- 图片文件路径
    Message_time DATETIME NOT NULL,                     -- 消息发送时间
    Is_deleted INT DEFAULT 0,                       -- 0-未撤回, 1-已撤回
    Is_read INT DEFAULT 0,                          -- 0-未读，1-已读 
    FOREIGN KEY (Sender_id) REFERENCES Student(Student_id),
    FOREIGN KEY (Receiver_id) REFERENCES Student(Student_id)
);


CREATE TABLE Friend (
    Friend_relation_id INT AUTO_INCREMENT PRIMARY KEY,-- 好友关系id
    Friend_a_id INT NOT NULL,                                  -- 用户a学号
    Friend_b_id INT NOT NULL,                                  -- 用户b学号
    FOREIGN KEY (Friend_a_id) REFERENCES Student(Student_id), 
    FOREIGN KEY (Friend_b_id) REFERENCES Student(Student_id)
);

CREATE TABLE Operation_record (
    Operation_record_id INT AUTO_INCREMENT PRIMARY KEY,        -- 我的操作id
    Operator_id INT NOT NULL,                                  -- 操作者的学生学号
    Operation_type ENUM(
                        'Exchangecourt_upload',                -- 发布了一个换场申请
                        'Exchangecourt_record',                -- 响应了他人的一次换场
                        'Offercourt_upload',                   -- 送出了一个场地
                        'Request_court',                       -- 接受了他人送出的一个场地
                        'Teamup_upload',                       -- 发布了一个组队拼场
                        'Teamup_request',                      -- 与别人组队拼场
                        'MyLost',                              -- 我丢失了一个物品
                        'MyFound'                              -- 我找到了一个物品
                        ) NOT NULL,                            -- 操作类型
    Operation_id INT NOT NULL,                                 -- 操作id号
    Operation_status INT,                                      -- 操作状态
    Operation_time DATETIME,                                   -- 操作时间
    FOREIGN KEY (Operator_id) REFERENCES Student(Student_id)
);

