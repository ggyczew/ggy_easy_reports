from easy_reports import EasyReport
from pathlib import Path

app = EasyReport(base_path=Path(__file__).resolve().parent)
app.base_config.from_pyfile('settings.py')
app.load_reports(['R002'])
app.run(logging_level='DEBUG')
#
