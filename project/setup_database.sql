-- Database setup script for Haru Issues system
-- Run this script in your MySQL database

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS summaries;

-- Use the database
USE summaries;

-- Create summaries table if it doesn't exist
CREATE TABLE IF NOT EXISTS summaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    reference VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    INDEX idx_reference (reference)
);

-- Insert some sample data if table is empty
INSERT INTO summaries (title, content, reference) 
SELECT * FROM (
    SELECT 
        '사이트 버그 제보' as title,
        '모바일 화면에서 레이아웃이 깨지는 현상이 발생하고 있습니다. 특히 아이폰에서 문제가 심각합니다.' as content,
        'toby' as reference
) AS tmp
WHERE NOT EXISTS (
    SELECT title FROM summaries WHERE title = '사이트 버그 제보'
) LIMIT 1;

INSERT INTO summaries (title, content, reference) 
SELECT * FROM (
    SELECT 
        '기능 요청' as title,
        '검색 기능이 있으면 좋겠어요. 현재는 글을 찾기 어려워서 불편합니다.' as content,
        '관리자' as reference
) AS tmp
WHERE NOT EXISTS (
    SELECT title FROM summaries WHERE title = '기능 요청'
) LIMIT 1;

-- Show table structure
DESCRIBE summaries;

-- Show sample data
SELECT * FROM summaries LIMIT 5; 