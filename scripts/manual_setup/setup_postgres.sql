

-- Create new database
CREATE DATABASE easy_reports;

-- Create new user
CREATE USER easy_reports WITH PASSWORD 'EasyReports#2023';

-- Grant privileges to new user on new_database
GRANT ALL PRIVILEGES ON DATABASE easy_reports TO easy_reports;

GRANT ALL ON SCHEMA public TO easy_reports;