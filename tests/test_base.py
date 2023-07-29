import pytest
from easy_reports import EasyReport
from pathlib import Path


def test_easy_report_init():
    app = EasyReport()
    assert app.base_path == Path().resolve()
    assert app.base_config.BASE_PATH == Path().resolve()
    assert app.defs_path == Path().resolve() / 'defs'


def test_base_easy_report_set_defs_path(monkeypatch):
    monkeypatch.setenv('EASY_REPORTS_DEFS_DIR', 'defs_mod_from_env')

    app = EasyReport()

    assert app.defs_path == Path().resolve() / 'defs_mod_from_env'

    app.defs_path = './defs_mod'
    assert app.defs_path == Path().resolve() / 'defs_mod'

    # reset defs_path to None
    app.defs_path = None
    app.base_config.from_pyfile('./tests/settings_test_base.py')

    assert app.defs_path == Path('./temp/test/defs').resolve()


def test_base_easy_report_load_reports():
    report_list = ['R001']
    app = EasyReport()
    app.defs_path = './examples/defs'

    assert app.defs_path == Path().resolve() / 'examples/defs'

    # test FAIL without supplied settings.py
    with pytest.raises(ValueError):
        app.load_reports(report_list)
    assert len(app._reports) == 0

    # test SUCCESS with supplied settings.py
    app.base_config.from_pyfile('./tests/settings_test_report.py')
    app.load_reports(report_list)
    assert len(app._reports) == len(report_list)

    # test basic Meta attribiutes mapped to report_config
    r = app._reports[0]
    assert r.report_config.report_symbol == 'R001'
    assert r.report_config.report_name == 'Test Report R001'


def test_base_easy_report_get_rpt():
    report_list = ['R001']
    app = EasyReport()
    app.defs_path = './examples/defs'
    app.base_config.from_pyfile('./tests/settings_test_report.py')
    app.load_reports(report_list)

    rpt = app.get_rpt('R001')
    assert rpt.__module__ == app._reports[0].__module__
