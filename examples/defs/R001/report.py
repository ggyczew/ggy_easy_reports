from easy_reports import ReportBase, processor


class Report(ReportBase):
    class Meta:
        symbol = 'R001'
        name = 'Test Report R001'

        db_list = {'R001_db': {'url': 'testing'}}

        # POSTGRES: select current_setting('easy_reports.date_from')
        # MYSQL: select @date_from
        # MSSQL: select @date_from -- !!! this is nnot working

        sql_params = [
            ("set easy_reports.date_from = '2023-01-01';", 'postgres'),
            ("set @date_from = '2023-01-01';", 'mysql'),
            ("declare @x int = 12", 'mssql'),
            # not working - left for information
            # ("exec sp_set_session_context  'date_from', '2023-01-01'", 'mssql'),
            # ("declare @date_from varchar(10) = '2023-01-01';", 'mssql'),
        ]

        sql_list = [
            ('test_postgres', 'postgres', ['name', 'language']),
            ('test_mysql', 'mysql', ['name', 'language']),
            ('test_mssql', 'mssql', ['name', 'language']),
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
                'filename': 'report {date}.xlsx',
                'send_email': True,
                'sheets': {
                    1: {
                        'sheet_name': 'Result Processed',
                        'data_src': 'df_result_processed',
                        'output_columns': [],
                        'freeze_panes': 'C2',
                        'header_formats': {
                            '*': 'header',
                        },
                        'column_formats': {},
                        'column_options': {},
                    },
                },
            }
        }

    @processor
    def p01(self) -> dict:
        df = self.results['df_final']
        # dataframe processing
        return {'df_result_processed': df}
