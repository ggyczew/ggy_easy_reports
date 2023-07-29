from pathlib import Path

ARCH_BASE_PATH = Path('./temp/test/arch').resolve()
CACHE_BASE_PATH = Path('./temp/test/cache').resolve()
LOGS_BASE_PATH = Path('./temp/test/logs').resolve()

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
