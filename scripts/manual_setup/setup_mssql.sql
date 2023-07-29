USE master;
GO

-- Create database
CREATE DATABASE [easy_reports];

-- Create a new login
CREATE LOGIN [easy_reports]	WITH 
	PASSWORD=N'EasyReports#2023',
	DEFAULT_DATABASE = [easy_reports];

-- Grant permissions
USE [easy_reports];
CREATE USER [easy_reports] FOR LOGIN [easy_reports];
EXEC sp_addrolemember 'db_datareader', 'easy_reports';
EXEC sp_addrolemember 'db_datawriter', 'easy_reports';
GRANT CONTROL on schema :: dbo to [easy_reports]
GRANT CREATE TABLE, SELECT, INSERT, UPDATE, DELETE to [easy_reports]; 