from datetime import datetime
import os
import glob
import pandas as pd
import pickle
from functools import reduce
import contextlib
from sqlalchemy import create_engine, text
from pathlib import Path
import logging


class DataCreator:
    def __init__(self, config=None, logger=None, **kwargs):
        # perform checks
        if not config:
            raise ValueError("Empty Report config!")

        if not config.report_sql_list:
            raise ValueError("Empty SQL list!")

        if not config.report_db_list:
            raise ValueError("Empty DB list!")

        self.config = config
        self.logger = logger or logging.getLogger('dummy')
        self.db_conn = dict()
        self.email_placeholders = dict()
        self.results = dict()
        self.from_cache = kwargs.get('from_cache', False)
        self.cache_format = kwargs.get('cache_format', 'parquet')

        # check if all db aliases from sql_list are present in db_list
        if self.from_cache == False:
            for sql, db, *args in config.report_sql_list:
                if db not in config.report_db_list.keys():
                    raise ValueError(
                        f'Missing db connection alias "{db}" in db_list for sql "{sql}"!'
                    )

    def open_db_conn(self):
        self.logger.debug('Opening db connections...')
        for f in self.config.report_sql_list:
            conn = f[1]
            if conn not in self.db_conn:
                self.logger.debug(f'Connecting db: {conn}')
                url = self.config.report_db_list.get(conn).get('url')
                self.db_conn[conn] = create_engine(url).connect()

    def close_db_conn(self):
        self.logger.debug('Closing db connections...')
        for alias in self.db_conn:
            self.logger.debug(f'Closing db: {self.db_conn[alias]}')
            self.db_conn[alias].close()

    def read_from_cache(self, filename, format='parquet'):
        filepath = self.config.report_cache_path / f'{filename}.{format}'
        if format == 'parquet':
            df = pd.read_parquet(filepath)
        elif format == 'csv':
            df = pd.read_csv(filepath, delimiter=';', decimal=',', encoding='utf-8')
        else:
            raise AttributeError(f'Unsupported cache file format: {format}')
        self.logger.debug(f'Read cache file: {filename}.{format}')
        return df

    def get_email_placeholders(self):
        return self.email_placeholders

    def sql_from_file(self, filename) -> str:
        filepath = self.config.report_sql_path / f'{filename}.sql'
        sql = open(filepath, 'r', encoding='UTF8').read()
        return sql

    def sql_to_df(self, sql, conn):
        df = pd.read_sql(sql, con=conn)
        return df

    def write_to_cache(self, df, filename, format='parquet'):
        path = self.config.report_cache_path
        if not path.exists():
            path.mkdir(parents=True)

        filepath = path / f'{filename}.{format}'

        if format == 'parquet':
            df.to_parquet(filepath)
        elif format == 'csv':
            df.to_csv(filepath, sep=';', index=False, decimal=',', encoding='utf-8')
        else:
            raise AttributeError(f'Unsupported cache file format: {format}')
        self.logger.debug(f'Zapisano plik cache: {filename}.{format}')
        return filepath

    def load_from_cache(self, format='parquet'):
        self.logger.debug('Reading cache files...')
        self.email_placeholders = pickle.load(
            open(os.path.join(self.cache_dir, 'email_placeholders__cache.pickle'), 'rb')
        )

        cache_files = [
            f for f in glob.glob(os.path.join(self.cache_dir, f'*__cache.{format}'))
        ]
        # read only known files from sql list
        for filename, db_alias, *args in self.config.report_sql_list:
            filename = f'df_{filename}__cache'
            dfname = f'df_{filename}'
            if args:
                dfjoin = (args[0:1] or (None,))[0]

            self.results[dfname] = [self.read_from_cache(filename, format), dfjoin]

    def save_to_cache(self):
        self.logger.debug('Writing cache files...')
        pickle.dump(
            self.email_placeholders,
            open(
                self.config.report_cache_path / 'email_placeholders__cache.pickle', 'wb'
            ),
        )
        self.logger.debug('Wrote to cache file: email_placeholders__cache.pickle')

        for result_df_name, result_df in self.results.items():
            if isinstance(result_df, pd.DataFrame):
                self.write_to_cache(result_df, f'{result_df_name}__cache')
            elif type(result_df) is list:
                self.write_to_cache(result_df[0], f'{result_df_name}__cache')
            else:
                raise ValueError(
                    'Value of result_df variable is neither DataFrame nor List of Dataframe and list of ON fileds!'
                )

    def set_def_params(self):
        """Set SQL params defined in report definition file"""
        if self.config.report_sql_params is None:
            return
        for f in self.config.report_sql_params:
            if f[1] == 'mssql':
                self.logger.error('Setting run params for MSSQL not working. Tested.')
            else:
                self.logger.info(f'Sets SQL params: {f[0]}')
                conn = self.db_conn.get(f[1])
                conn.execute(text(f[0]))
                conn.commit()

    def set_run_params(self, **kwargs):
        """Set SQL params passed as kwargs to run method"""
        params = kwargs.get('params', None)
        if params:
            for f in params.items():
                if f[1] == 'mssql':
                    self.logger.error(
                        'Setting run params for MSSQL not working. Tested.'
                    )
                else:
                    self.logger.info(f'Sets SQL params: {f[0]}')
                    conn = self.db_conn.get(f[1])
                    conn.execute(text(f[0]))
                    conn.commit()

    def load_from_database(self):
        query_count = 0
        for filename, db_alias, *args in self.config.report_sql_list:
            self.logger.info(f'Running sql query: {filename}')
            sql = self.sql_from_file(filename)
            if args:
                dfjoin = (args[0:1] or (None,))[0]
            else:
                dfjoin = None
            self.results[f'df_{filename}'] = [
                self.sql_to_df(sql=text(sql), conn=self.db_conn.get(db_alias)),
                dfjoin,
            ]
            query_count += 1

            self.email_placeholders.update(self.get_email_placeholders())

        self.save_to_cache()
        if self.results:
            self.logger.info(f'Total {query_count} sql query run')

    # TODO add more advanced merging logic
    def merge_data_frames(self, df_list, df_name='df_final', write_to_cache=True):
        # merge dataframes
        if len(df_list) > 1:
            """Loop df_list and merge using specified list of fields"""
            df = df_list[0][0]
            for i in range(1, len(df_list)):
                # merge only DF with list of keys
                if not df_list[i][1] is None:
                    df = pd.merge(df, df_list[i][0], how='left', on=df_list[i][1])
        else:
            df = df_list[0][0]

        self.logger.debug(
            f'Total {len(self.config.report_sql_list)} dataframes merged into one. Shape: {df.shape}'
        )
        if write_to_cache:
            f = self.write_to_cache(df, f'{df_name}')
        return df

    def get_results(self) -> dict:
        return self.results

    def get_result_df(self, name) -> pd.DataFrame:
        return self.results.get(name, None)

    def reset_results(self):
        self.results = dict()

    def run(self, **kwargs):
        self.logger.debug('Data extraxction started...')

        # runtime setting
        from_cache = kwargs.get('from_cache', self.from_cache)
        cache_format = kwargs.get('cache_format', self.cache_format)

        if from_cache:
            self.load_from_cache(format=cache_format)
        else:
            self.open_db_conn()
            self.set_def_params()
            self.set_run_params(**kwargs)
            self.load_from_database()
            self.close_db_conn()

        # merge dataframes
        df_list = list(self.results.values())
        df_final = self.merge_data_frames(df_list, 'df_final')

        # TODO test releasing
        # release memory
        if kwargs.get('release_memory', False):
            self.reset_results()

        # store merged result dataframe
        self.results['df_final'] = df_final
        self.logger.debug('Data extraxction finished')

    def run_processors(self, processors=[]):
        self.logger.info('Data processing started...')

        for fn in processors:
            self.logger.debug(f'- running processor {fn.__name__}')
            try:
                df_dict = fn(self)
            except Exception as e:
                print(e)

            # add datafre to results dictionary
            self.logger.debug(f'- {len(df_dict)} results added')
            for name, value in df_dict.items():
                self.results[name] = value

        self.logger.info('Data processing finished')

    def flush(self):
        """Clean after run"""
        self.email_placeholders = dict()
        self.results = dict()
