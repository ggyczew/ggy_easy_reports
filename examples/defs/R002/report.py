from easy_reports import ReportBase, processor
import numpy as np


class Report(ReportBase):
    class Meta:
        symbol = 'R002'
        name = 'Countries Example Report'

        db_list = {'R002_alias': {'url': 'testing'}}

        sql_list = [
            ('countries_postgres', 'postgres', ['country']),
            ('countries_mysql', 'mysql', ['country']),
            ('countries_mssql', 'mssql', ['country']),
        ]

        email_config = {
            1: {
                'to': 'recepient@email.com',
                'cc': '',
                'subject': 'Test',
                'onbehalf': '',
                'body': 'This is test',
                'template': '',
                'attachments': [],
                'attachments_rpt_id': [1],
            }
        }

        rpt_config = {
            1: {
                'filename': 'countries {date}.xlsx',
                'send_email': True,
                'sheets': {
                    1: {
                        'sheet_name': 'Countries',
                        'data_src': 'df_final',
                        'output_columns': [],
                        'freeze_panes': 'B2',
                        'header_formats': {
                            '*': 'header',
                        },
                        'column_formats': {
                            'capital_*': 'fg_excel_35',
                            'flag_colors': 'fg_excel_35',
                        },
                        'column_options': {
                            'C:G': {'level': 1, 'hidden': True},
                            'B:B': {'collapsed': True},
                        },
                        'conditional_formats': {
                            'birth_rate': [
                                {
                                    'type': 'data_bar',
                                    'bar_color': '#50DAF6',
                                    'bar_border_color': 'black',
                                }
                            ],
                            'death_rate': [
                                {
                                    'type': 'data_bar',
                                    'bar_color': 'green',
                                    'bar_negative_color': 'red',
                                },
                            ],
                        },
                        'data_validations': {
                            'rating': {
                                'validate': 'list',
                                'source': ['Excelent', 'Good', 'Moderate', 'Poor'],
                            },
                        },
                    },
                    2: {
                        'sheet_name': 'CountriesCapitals',
                        'data_src': 'df_final',
                        'output_columns': ['country', 'capital'],
                        'freeze_panes': 'B2',
                        'header_formats': {
                            '*': 'header',
                        },
                        'column_formats': {},
                        'column_options': {},
                        'conditional_formats': {},
                    },
                    10: {
                        'sheet_name': 'DanubeCountries',
                        'data_src': 'df_danube',
                        'output_columns': [],
                        'freeze_panes': 'B2',
                        'header_formats': {
                            '*': 'header',
                        },
                        'column_formats': {},
                        'column_options': {},
                        'conditional_formats': {},
                    },
                },
            },
        }

    @processor
    def p01(self) -> dict:
        df = self.results['df_final']
        # dataframe processing
        df = df[df.longest_rivers.str.contains('Danube')]
        return {'df_danube': df}
