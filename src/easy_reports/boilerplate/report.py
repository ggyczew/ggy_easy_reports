from easy_reports import ReportBase, processor


class Report(ReportBase):
    class Meta:
        symbol = '#symbol'
        name = f'Report {symbol}'

        db_list = {
            'alias_1': {'url': 'testing'},
            'alias_2': {'url': 'testing'},
            # 'alias_3': {'url': 'testing'}
        }

        sql_list = [
            ('sql_1', 'alias_1', ['PK']),
            ('sql_2', 'alias_2', ['PK']),
            # ('sql_3', 'alias_3', ['PK']),
        ]

        email_config = {
            1: {
                'to': 'recipient@email.com',
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
                'filename': 'report_{symbol}_{date}.xlsx',
                'send_email': True,
                'sheets': {
                    1: {
                        'sheet_name': 'Result',
                        'data_src': 'df_result',
                        'output_columns': [],
                        'freeze_panes': 'B2',
                        'header_formats': {
                            '*': 'header',
                        },
                        'column_formats': {
                            'column_name': 'fg_excel_35',
                        },
                        'column_options': {
                            'D:F': {'level': 1, 'hidden': True},
                            'C:C': {'collapsed': True},
                        },
                        'conditional_formats': {
                            'column_name': [
                                {
                                    'type': 'data_bar',
                                    'bar_color': '#50DAF6',
                                    'bar_border_color': 'black',
                                },
                            ],
                        },
                        'data_validations': {
                            'column_name': {
                                'validate': 'list',
                                'source': ['Excelent', 'Good', 'Moderate', 'Poor'],
                            },
                        },
                    }
                },
            }
        }

        @processor
        def p01(self) -> dict:
            df = self.results['df_final']
            # dataframe processing
            return {'df_result': df}
