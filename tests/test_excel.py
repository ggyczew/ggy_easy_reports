import pytest
import copy
from easy_reports import EasyReport
from easy_reports.data import DataCreator
from easy_reports.excel import ExcelCreator, Excel
import sqlalchemy
import pandas as pd
import tempfile
from pathlib import Path
from datetime import date


@pytest.fixture
def rpt():
    report_list = ['R001']
    app = EasyReport()
    # load setting that do not change DEFS and SQL paths
    app.base_config.from_pyfile('./tests/settings_test_excel.py')
    app.defs_path = './examples/defs'
    app.load_reports(report_list)
    rpt = app._reports[0]
    return copy.deepcopy(rpt)


@pytest.fixture
def data(rpt):
    rpt.setup_dirs()
    data = DataCreator(config=rpt.report_config)
    data.open_db_conn()
    yield data
    data.close_db_conn()


@pytest.fixture
def excel(rpt):
    data = rpt.run_data()
    excel = ExcelCreator(config=rpt.report_config)
    excel.set_data_results(data.get_results())
    yield excel


@pytest.fixture
def xls(excel):
    for file_id, file_config in excel.config.report_rpt_config.items():
        xls = Excel(file_config, excel.config, excel.logger)
        yield xls


def test_excel_excel_creator_init(rpt):

    excel = ExcelCreator(config=rpt.report_config)

    assert excel.config == rpt.report_config


def test_excel_excel_creator_init_no_config_exception():

    with pytest.raises(ValueError, match='Empty Report config!'):
        assert ExcelCreator()


def test_excel_excel_creator_set_data_results(rpt, excel):

    # dataframes expected: df_final, df_result_processed
    assert len(excel.data_results) == 2
    for name in excel.data_results.keys():
        pd.testing.assert_frame_equal(
            excel.data_results[name], rpt._data.get_result_df(name)
        )


def test_excel_excel_creator_create_file(excel):

    for file_id, file_config in excel.config.report_rpt_config.items():

        filepath = excel.create_file(file_id, file_config)
        assert Path(filepath).resolve().exists()
        assert excel.email_attachments[file_id] == filepath


def test_excel_excel_init_no_file_config_exception(excel):

    for file_id, file_config in excel.config.report_rpt_config.items():

        with pytest.raises(ValueError, match='Empty File config!'):
            assert Excel(None, excel.config, excel.logger)


def test_excel_excel_init_no_report_config_exception(excel):

    for file_id, file_config in excel.config.report_rpt_config.items():

        with pytest.raises(ValueError, match='Empty Report config!'):
            assert Excel(file_config, None, excel.logger)


def test_excel_excel_format_filename(xls):

    input_1 = 'new_file_{date}'
    output_1 = input_1.replace(r'{date}', date.today().strftime("%Y-%m-%d"))
    assert xls.format_filename(input_1) == output_1

    input_2 = 'new_file_{option_1}_{option_2}'
    output_2 = 'new_file_A_B'
    options = [('{option_1}', 'A'), ('{option_2}', 'B')]
    assert xls.format_filename(input_2, options) == output_2


def test_excel_excel_write_sheet_data_src_exception(excel, xls):

    # test data_src pointing to non existing data
    xls.file_config['sheets'][1]['data_src'] = 'bar'
    with pytest.raises(ValueError):
        assert xls.write_sheet(1)

    # test data_src pointing data = None
    xls.data_results = {'df_result_processed': None}
    with pytest.raises(ValueError):
        assert xls.write_sheet(1)
