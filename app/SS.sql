-- Create Database 'ss' on EC2 instance
CREATE DATABASE ss;
USE ss;

-- USERS

-- User (base table)
CREATE TABLE user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    institucional_email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    user_type TINYINT NOT NULL, -- 0 = admin, 1 = coordinator, 2 = student
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME
);

-- Admin
CREATE TABLE admin (
    user_id INT PRIMARY KEY,
    position VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- Coordinator
CREATE TABLE coordinator (
    user_id INT PRIMARY KEY,
    department VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- Student
CREATE TABLE student (
    user_id INT PRIMARY KEY,
    control_number VARCHAR(50),
    major VARCHAR(100), --ISC, IEM, IGE, IGL
    semester INT,
    credits INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);




-- INSTITUTIONS & PROGRAMS

CREATE TABLE institution (
    institution_id INT PRIMARY KEY AUTO_INCREMENT,
    institution_name VARCHAR(100),
    description VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(100),
    street VARCHAR(100),
    number VARCHAR(10),
    neighborhood VARCHAR(100),
    postal_code VARCHAR(10),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME
);

CREATE TABLE program (
    program_id INT PRIMARY KEY AUTO_INCREMENT,
    institution_id INT,
    program_name VARCHAR(100),
    description VARCHAR(255),
    activities VARCHAR(255),
    supervisor_name VARCHAR(100),
    supervisor_phone VARCHAR(20),
    supervisor_email VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME,
    FOREIGN KEY (institution_id) REFERENCES institution(institution_id)
);




-- REQUESTS

CREATE TABLE request (
    request_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL, -- FK to student(user_id)
    program_id INT NOT NULL,
    acceptance_status TINYINT, -- 0 = pending, 1 = accepted, 2 = rejected
    progress_status TINYINT,   -- 0 = pending, 1 = in_progress, 2 = completed
    request_date DATE,
    completed_hours INT DEFAULT 0,
    coordinator_id INT, -- FK to coordinator(user_id)
    feedback VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME,
    FOREIGN KEY (student_id) REFERENCES student(user_id),
    FOREIGN KEY (program_id) REFERENCES program(program_id),
    FOREIGN KEY (coordinator_id) REFERENCES coordinator(user_id)
);




-- DOCUMENTS 

-- Base document table
CREATE TABLE document (
    document_id INT PRIMARY KEY AUTO_INCREMENT,
    document_type TINYINT, -- 0 = report, 1 = template, 2 = release_letter
    file_path VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME
);

-- Templates
CREATE TABLE template (
    document_id INT PRIMARY KEY,
    description VARCHAR(255),
    coordinator_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME,
    FOREIGN KEY (document_id) REFERENCES document(document_id),
    FOREIGN KEY (coordinator_id) REFERENCES coordinator(user_id)
);

-- Reports
CREATE TABLE report (
    document_id INT PRIMARY KEY,
    request_id INT NOT NULL,
    report_number TINYINT NOT NULL, -- 1, 2, 3
    status TINYINT DEFAULT 0, -- 0=pending, 1=submitted, 2=accepted, 3=rejected
    feedback VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME,
    FOREIGN KEY (document_id) REFERENCES document(document_id),
    FOREIGN KEY (request_id) REFERENCES request(request_id)
);

-- Release letters
CREATE TABLE release_letter (
    document_id INT PRIMARY KEY,
    request_id INT NOT NULL,
    coordinator_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME,
    FOREIGN KEY (document_id) REFERENCES document(document_id),
    FOREIGN KEY (request_id) REFERENCES request(request_id),
    FOREIGN KEY (coordinator_id) REFERENCES coordinator(user_id)
);