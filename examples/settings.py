import os

# set path relative to root folder
DEFS_BASE_PATH = './examples/defs'

server = 'localhost'
database = 'easy_reports'
username = 'easy_reports'
password = 'EasyReports#2023'
driver = 'ODBC Driver 18 for SQL Server'

DB_LIST = {
    'postgres': {
        'url': f'postgresql+psycopg2://{username}:{password}@db-postgres/{database}'
    },
    'mysql': {'url': f'mysql+pymysql://{username}:{password}@db-mysql/{database}'},
    'mssql': {
        'url': f'mssql+pyodbc://{username}:{password}@db-mssql/{database}?driver={driver}&TrustServerCertificate=yes'
    },
}

# MailDev Docker
EMAIL_SERVER = 'maildev'
EMAIL_PORT = 1025
EMAIL_USER = os.getenv('CUSTOM_EMAIL_USER', None)
EMAIL_PASSWORD = os.getenv('CUSTOM_EMAIL_PASSWORD', None)
