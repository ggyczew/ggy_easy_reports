import pytest
import copy
from easy_reports import EasyReport
from easy_reports.data import DataCreator
import sqlalchemy
import pandas as pd
import tempfile
from pathlib import Path


@pytest.fixture
def rpt():
    report_list = ['R001']
    app = EasyReport()
    app.base_config.from_pyfile('./tests/settings_test_data.py')
    app.defs_path = './examples/defs'
    app.load_reports(report_list)
    rpt = app._reports[0]
    return copy.deepcopy(rpt)


@pytest.fixture
def data(rpt):
    data = DataCreator(config=rpt.report_config)
    try:
        data.open_db_conn()
        # attribiute set for testing otherwise it is pass from report self.processor
        data._processors = rpt._processors
        yield data
    finally:
        data.close_db_conn()


def test_data_data_creator_init(rpt):
    data = DataCreator(config=rpt.report_config, from_cache=False)

    assert data.config == rpt.report_config
    assert data.from_cache == False


def test_data_data_creator_init_no_config_exception():
    with pytest.raises(ValueError, match='Empty Report config!'):
        assert DataCreator()


def test_data_data_creator_init_no_report_sql_list(rpt):
    rpt.report_config.report_sql_list = None
    with pytest.raises(ValueError, match='Empty SQL list!'):
        assert DataCreator(config=rpt.report_config)


def test_data_data_creator_init_no_report_db_list(rpt):
    rpt.report_config.report_db_list = None
    with pytest.raises(ValueError, match='Empty DB list!'):
        assert DataCreator(config=rpt.report_config)


def test_data_data_creator_init_missing_db_alias(rpt):
    key = list(rpt.report_config.report_db_list.keys())[0]
    rpt.report_config.report_db_list.pop(key, None)
    with pytest.raises(ValueError, match='Missing db connection*'):
        assert DataCreator(config=rpt.report_config)


def test_data_data_creator_open_close_db_connection(rpt):
    """Test opening and closing database connections"""

    data = DataCreator(config=rpt.report_config)

    # test if connection is open
    data.open_db_conn()
    for alias in data.db_conn:
        assert isinstance(data.db_conn[alias], sqlalchemy.Connection)

    # test if connection is closed
    data.close_db_conn()
    for alias in data.db_conn:
        assert data.db_conn[alias].closed == True


def test_data_data_creator_sql_to_df(data):
    """Test query against database"""

    for conn_alias in data.db_conn:
        print(f'Asserting DB {conn_alias=}')
        for filename, db_alias, *_ in data.config.report_sql_list:
            if db_alias == conn_alias:
                print(f'Asserting SQL {filename=}, {db_alias=}')
                sql = data.sql_from_file(filename)
                df = data.sql_to_df(sqlalchemy.text(sql), data.db_conn[conn_alias])
                assert isinstance(df, pd.DataFrame)
                assert df.shape is not None


def test_data_data_creator_write_to_read_from_cache(data):
    """Test if dataframe written and restored from cache are equal"""

    filename, db_alias, *_ = data.config.report_sql_list[0]
    sql = data.sql_from_file(filename)
    df1 = data.sql_to_df(sqlalchemy.text(sql), data.db_conn[db_alias])
    for format in [data.cache_format, 'parquet', 'csv']:
        data.write_to_cache(df1, filename, format)
        df2 = data.read_from_cache(filename, format)
        print(f'Asserting cache write/read for {format=}')
        pd.testing.assert_frame_equal(df1, df2)


def test_data_data_creator_get_results(data):
    assert type(data.get_results()) == type(dict())


def test_data_data_creator_get_result_df(data):
    data.load_from_database()
    for filename, db_alias, *_ in data.config.report_sql_list:
        name = f'df_{filename}'
        # assert isinstance(data.get_result_df(name), pd.DataFrame)


def test_data_data_creator_load_from_database(data):
    """Test loading data from sql queries into dataframes stored in results list"""

    data.load_from_database()

    assert type(data.get_results()) == type(dict())
    assert len(data.get_results()) == len(data.config.report_sql_list)


def test_data_data_creator_merge_data_frames(data):
    """Test merging dataframes into one df_final"""

    data.load_from_database()
    df_list = list(data.get_results().values())
    filename = 'test_df_final__cache'
    df1 = data.merge_data_frames(df_list, filename)
    df2 = data.read_from_cache(filename)
    pd.testing.assert_frame_equal(df1, df2)


def test_data_data_creator_run(data):
    data.run()

    assert 'df_final' in data.get_results().keys()

    # test if connection is closed after run
    data.close_db_conn()
    for alias in data.db_conn:
        assert data.db_conn[alias].closed == True


def test_data_data_creator_run_processors(data):
    data.run()
    data.run_processors(data._processors)

    assert 'df_result_processed' in data.get_results().keys()


def test_data_data_creator_set_def_params(data):
    sql = {
        "postgres": "select current_setting('easy_reports.date_from')",
        "mysql": "select @date_from",
        # not working - left for information
        # "mssql": "select session_context(N'date_from')",
        # "mssql": "select @date_from",
    }
    data.set_def_params()

    for alias, sql in sql.items():
        df = data.sql_to_df(sql=sqlalchemy.text(sql), conn=data.db_conn[alias])
        print(sql)
        print(df)
        assert str(df.iloc[0, 0]) == '2023-01-01'
