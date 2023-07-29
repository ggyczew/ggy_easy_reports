from pathlib import Path

DEFS_BASE_PATH = './defs'

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
