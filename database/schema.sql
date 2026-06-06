-- ============================================
-- Exposys Data Labs - MySQL Database Schema
-- ============================================

CREATE DATABASE IF NOT EXISTS exposys_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE exposys_db;

-- Students Table
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    branch VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    college VARCHAR(200) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    tenth_percentage FLOAT NOT NULL,
    twelfth_percentage FLOAT NOT NULL,
    ug VARCHAR(100),
    pg VARCHAR(100),
    location VARCHAR(100) NOT NULL,
    internship_domain VARCHAR(100) NOT NULL,
    duration VARCHAR(50) NOT NULL,
    password VARCHAR(256) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Admins Table
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(256) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Internships Table
CREATE TABLE IF NOT EXISTS internships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    domain VARCHAR(100) NOT NULL,
    description TEXT,
    duration_options VARCHAR(200),
    stipend VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Payments Table
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    amount FLOAT NOT NULL,
    transaction_id VARCHAR(100),
    screenshot_filename VARCHAR(200),
    status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(50) DEFAULT 'UPI',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Contacts Table
CREATE TABLE IF NOT EXISTS contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    phone VARCHAR(15),
    subject VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
