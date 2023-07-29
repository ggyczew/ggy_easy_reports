import pytest
from easy_reports import EasyReport
from pathlib import Path


def test_config_init_without_args():
    app = EasyReport()
    assert app.base_path == Path().resolve()
    # assert app.defs_path == Path().resolve() / 'defs'


def test_config_init_with_args():
    app = EasyReport(base_path='./temp/test')
    assert app.base_path == Path().resolve() / 'temp/test'


def test_config_from_kwargs():
    app = EasyReport()
    app.base_config.from_kwargs(
        string='value', bool=True, int=1, float=1.2, list=[1, 2], dict={"k": "v"}
    )

    assert app.base_config.STRING == "value"
    assert app.base_config.BOOL is True
    assert app.base_config.INT == 1
    assert app.base_config.FLOAT == 1.2
    assert app.base_config.LIST == [1, 2]
    assert app.base_config.DICT == {"k": "v"}


def test_config_from_env(monkeypatch):
    monkeypatch.setenv("EASY_REPORTS_STRING", "value")
    monkeypatch.setenv("EASY_REPORTS_BOOL", "true")
    monkeypatch.setenv("EASY_REPORTS_INT", "1")
    monkeypatch.setenv("EASY_REPORTS_FLOAT", "1.2")
    monkeypatch.setenv("EASY_REPORTS_LIST", "[1, 2]")
    monkeypatch.setenv("EASY_REPORTS_DICT", '{"k": "v"}')

    app = EasyReport()
    app.base_config.from_env()

    assert app.base_config.STRING == "value"
    assert app.base_config.BOOL is True
    assert app.base_config.INT == 1
    assert app.base_config.FLOAT == 1.2
    assert app.base_config.LIST == [1, 2]
    assert app.base_config.DICT == {"k": "v"}


def test_config_from_env_custom_prefix(monkeypatch):
    monkeypatch.setenv("EASY_REPORTS_A", "a")
    monkeypatch.setenv("NOT_EASY_REPORTS_A", "b")

    app = EasyReport()
    app.base_config.from_env('NOT_EASY_REPORTS')

    assert app.base_config.A == "b"


def test_config_from_pyfile_1():
    app = EasyReport()

    with pytest.raises(OSError):
        app.base_config.from_pyfile('./tests/settings_not_exist.py')


def test_config_from_pyfile_2():
    app = EasyReport()
    app.base_config.from_pyfile('./tests/settings_test_base.py')

    assert app.base_config.DEFS_BASE_PATH == Path().resolve() / 'temp/test/defs'
    assert app.base_config.ARCH_BASE_PATH == Path().resolve() / 'temp/test/arch'
    assert app.base_config.LOGS_BASE_PATH == Path().resolve() / 'temp/test/logs'
    assert app.base_config.SQL_BASE_PATH == Path().resolve() / 'temp/test/sql'
    assert app.base_config.DEFS_DIR == 'defs_mod'
    assert app.base_config.ARCH_DIR == 'arch_mod'
    assert app.base_config.LOGS_DIR == 'logs_mod'
    assert app.base_config.SQL_DIR == 'sql_mod'


def test_config_from_pyfile_3(monkeypatch):
    """Test email configuration from env and settings"""

    monkeypatch.setenv('EASY_REPORTS_EMAIL_SERVER', 'email_server_from_env')
    monkeypatch.setenv('EASY_REPORTS_EMAIL_PORT', '1111')
    monkeypatch.setenv('EASY_REPORTS_EMAIL_USER', 'email_user_from_env')
    monkeypatch.setenv('EASY_REPORTS_EMAIL_PASSWORD', 'email_password_from_env')

    app = EasyReport()

    assert app.base_config.EMAIL_SERVER == 'email_server_from_env'
    assert app.base_config.EMAIL_PORT == 1111
    assert app.base_config.EMAIL_USER == 'email_user_from_env'
    assert app.base_config.EMAIL_PASSWORD == 'email_password_from_env'

    app.base_config.from_pyfile('./tests/settings_test_base.py')

    # check if attributes overriden by loading settings.py
    assert app.base_config.EMAIL_SERVER == 'email_server'
    assert app.base_config.EMAIL_PORT == 2222
    assert app.base_config.EMAIL_USER == 'email_user'
    assert app.base_config.EMAIL_PASSWORD == 'email_password'
