CREATE TABLE Student (
    Student_id INT PRIMARY KEY,
    Student_name VARCHAR(50) NOT NULL,
    Student_phone VARCHAR(50),
    Student_password VARCHAR(50) NOT NULL
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
