from pathlib import Path

DEFS_BASE_PATH = Path('./temp/test/defs').resolve()
ARCH_BASE_PATH = Path('./temp/test/arch').resolve()
LOGS_BASE_PATH = Path('./temp/test/logs').resolve()
SQL_BASE_PATH = Path('./temp/test/sql').resolve()

DEFS_DIR = 'defs_mod'
ARCH_DIR = 'arch_mod'
LOGS_DIR = 'logs_mod'
SQL_DIR = 'sql_mod'

EMAIL_SERVER = 'email_server'
EMAIL_PORT = 2222
EMAIL_USER = 'email_user'
EMAIL_PASSWORD = 'email_password'

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
        'url': f'mssql+pyodbc://{username}:{password}@db-mssql/{database}?driver=ODBC Driver 18 for SQL Server&TrustServerCertificate=yes'
    },
}
