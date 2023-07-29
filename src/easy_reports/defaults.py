DEFS_DIR = 'defs'
# By default following dirs are subfolders of each Report
LOGS_DIR = 'logs'
ARCH_DIR = 'arch'
SQL_DIR = 'sql'
CACHE_DIR = 'cache'
TEMPL_DIR = 'templ'

EMAIL_ENGINE = 'smtplib'
EMAIL_SERVER = 'localhost'
EMAIL_PORT = 1025
EMAIL_USER = ''
EMAIL_PASSWORD = ''

DB_LIST = {}

_SHEET_CONFIG = {
    'sheet_name': 'dane',
    'data_src': 'df_final',
    'output_columns': [],
    'freeze_panes': 'B2',
    'header_formats': {'*': 'header'},
    'column_formats': {},
    'column_options': {},
    'conditional_formats': {},
}

_RPT_CONFIG = {
    'filename': 'report.xlsx',
    'send_email': False,
    'sheets': {1: _SHEET_CONFIG},
}

_EMAIL_ITEM_CONFIG = {
    'to': '',
    'cc': '',
    'subject': '',
    'onbehalf': '',
    'body': '',
    'template': '',
    'attachments': [],
    'attachments_rpt_id': [1],
}

_EMAIL_CONFIG = {
    1: _EMAIL_ITEM_CONFIG,
}


_XLS_FORMATS = {
    'percent': {'num_format': '#,##0.0 %'},
    'currency2': {'num_format': '#,##0.00 zł'},
    'currency0': {'num_format': '#,##0 zł'},
    'decimal': {'num_format': '#,##0.0'},
    'integer': {'num_format': '#,##0'},
    'header': {
        'bold': True,
        'valign': 'center',
        'align': 'center',
        'fg_color': '#b0b0b0',
        'border': 1,
    },
    'header_wrap': {
        'bold': True,
        'valign': 'center',
        'align': 'center',
        'fg_color': '#b0b0b0',
        'border': 1,
        'text_wrap': True,
    },
    'header_rotated': {
        'bold': True,
        'valign': 'center',
        'align': 'center',
        'fg_color': '#b0b0b0',
        'border': 1,
        'rotation': 90,
    },
    'fg_excel_35': {
        'fg_color': '#b0b0b0',
    },
}
