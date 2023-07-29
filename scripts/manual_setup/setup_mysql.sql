
-- Create database
CREATE DATABASE easy_reports;

-- Create a new user
CREATE USER 'easy_reports'@'%' IDENTIFIED BY 'EasyReports#2023';

-- Grant permissions
GRANT ALL PRIVILEGES ON easy_reports.* TO 'easy_reports'@'%';