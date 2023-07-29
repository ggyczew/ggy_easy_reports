import importlib
import sys
import os
import copy
import logging
from pathlib import Path

# import schedule
from datetime import datetime
from shutil import copyfile

# Package imports
from .config import Config
from .data import DataCreator
from .excel import ExcelCreator
from .email import EmailCreator

import traceback


def processor(fn):
    """Mark decoreted function as processor"""
    fn.__processor__ = True
    return fn


class ReportConfig:
    """Create base config by merging default config with passed options"""

    def __init__(self, base_config: Config, options):
        self.report_symbol = options.symbol
        self.report_name = options.name

        # configure logs path
        self.report_logs_path = getattr(options, 'logs_path', None)
        if self.report_logs_path is None:
            if getattr(base_config, 'LOGS_BASE_PATH', None):
                if getattr(options, 'LOGS_DIR', None):
                    self.report_logs_path = Path(
                        getattr(base_config, 'LOGS_BASE_PATH')
                    ).resolve() / getattr(options, 'LOGS_DIR')
                else:
                    self.report_logs_path = (
                        Path(getattr(base_config, 'LOGS_BASE_PATH')).resolve()
                        / options.symbol
                    )
            else:
                self.report_logs_path = options.report_path / getattr(
                    options, 'LOGS_DIR', base_config.LOGS_DIR
                )

        # configure archive path
        self.report_arch_path = getattr(options, 'arch_path', None)
        if self.report_arch_path is None:
            if getattr(base_config, 'ARCH_BASE_PATH', None):
                if getattr(options, 'ARCH_DIR', None):
                    self.report_arch_path = Path(
                        getattr(base_config, 'ARCH_BASE_PATH')
                    ).resolve() / getattr(options, 'ARCH_DIR')
                else:
                    self.report_arch_path = (
                        Path(getattr(base_config, 'ARCH_BASE_PATH')).resolve()
                        / options.symbol
                    )
            else:
                self.report_arch_path = options.report_path / getattr(
                    options, 'ARCH_DIR', base_config.ARCH_DIR
                )

        # configure sql path
        self.report_sql_path = getattr(options, 'sql_path', None)
        if self.report_sql_path is None:
            if getattr(base_config, 'SQL_BASE_PATH', None):
                if getattr(options, 'SQL_DIR', None):
                    self.report_sql_path = Path(
                        getattr(base_config, 'SQL_BASE_PATH')
                    ).resolve() / getattr(options, 'SQL_DIR')
                else:
                    self.report_sql_path = (
                        Path(getattr(base_config, 'SQL_BASE_PATH')).resolve()
                        / options.symbol
                    )
            else:
                self.report_sql_path = options.report_path / getattr(
                    options, 'SQL_DIR', base_config.SQL_DIR
                )

        # configure cache path
        self.report_cache_path = getattr(options, 'cache_path', None)
        if self.report_cache_path is None:
            if getattr(base_config, 'CACHE_BASE_PATH', None):
                if getattr(options, 'CACHE_DIR', None):
                    self.report_cache_path = Path(
                        getattr(base_config, 'CACHE_BASE_PATH')
                    ).resolve() / getattr(options, 'CACHE_DIR')
                else:
                    self.report_cache_path = (
                        Path(getattr(base_config, 'CACHE_BASE_PATH')).resolve()
                        / options.symbol
                    )
            else:
                self.report_cache_path = options.report_path / getattr(
                    options, 'CACHE_DIR', base_config.CACHE_DIR
                )

        # configure templates path
        self.report_templ_path = getattr(options, 'templ_path', None)
        if self.report_templ_path is None:
            if getattr(base_config, 'TEMPL_BASE_PATH', None):
                if getattr(options, 'TEMPL_DIR', None):
                    self.report_templ_path = Path(
                        getattr(base_config, 'TEMPL_BASE_PATH')
                    ).resolve() / getattr(options, 'TEMPL_DIR')
                else:
                    self.report_templ_path = (
                        Path(getattr(base_config, 'TEMPL_BASE_PATH')).resolve()
                        / options.symbol
                    )
            else:
                self.report_templ_path = options.report_path / getattr(
                    options, 'TEMPL_DIR', base_config.TEMPL_DIR
                )

        # configure databse connection list and
        # add any additional defined in report definition
        self.report_db_list = copy.deepcopy(base_config.DB_LIST)
        db_list = getattr(options, 'db_list', None)
        if db_list:
            for key, value in db_list.items():
                if key not in self.report_db_list.keys():
                    self.report_db_list[key] = value

        self.report_sql_list = getattr(options, 'sql_list', None)
        # check if all db aliases declared in db_list
        if bool(self.report_sql_list):
            if bool(self.report_db_list):
                for i, value in enumerate(self.report_sql_list):
                    if value[1] not in self.report_db_list.keys():
                        raise ValueError(
                            f'Database alias "{value[1]}" for sql {i} not defined!'
                        )
            else:
                raise ValueError('Empty DB_LIST')

        self.report_sql_params = getattr(options, 'sql_params', None)
        # check if all db aliases declared in db_list
        if self.report_sql_params is not None:
            for i, value in enumerate(self.report_sql_params):
                if value[1] not in self.report_db_list.keys():
                    raise ValueError(
                        f'Database alias "{value[1]}" for param "{i}" not defined!'
                    )

        # configure report
        # if any config item is missing then its taken from defaults
        self.report_rpt_config = getattr(options, 'rpt_config', None)
        if self.report_rpt_config is None:
            self.report_rpt_config = dict()
            self.report_rpt_config[1] = copy.deepcopy(base_config._RPT_CONFIG)
        else:
            default_rpt_config = copy.deepcopy(base_config._RPT_CONFIG)
            for r, rpt in self.report_rpt_config.items():
                for r_key, r_value in default_rpt_config.items():
                    if r_key not in rpt.keys():
                        self.report_rpt_config[r][r_key] = r_value
                    elif r_key == 'sheets':
                        for s, sheet in rpt['sheets'].items():
                            for s_key, s_value in default_rpt_config['sheets'][
                                1
                            ].items():
                                if s_key not in sheet.keys():
                                    self.report_rpt_config[r]['sheets'][s][
                                        s_key
                                    ] = s_value

        # # Get email_engine
        self.email_engine = copy.deepcopy(base_config.EMAIL_ENGINE)
        self.email_server = copy.deepcopy(base_config.EMAIL_SERVER)
        self.email_port = copy.deepcopy(base_config.EMAIL_PORT)
        self.email_user = copy.deepcopy(base_config.EMAIL_USER)
        self.email_password = copy.deepcopy(base_config.EMAIL_PASSWORD)

        # Configure Email
        self.report_email_config = getattr(options, 'email_config', None)
        if self.report_email_config is None:
            self.report_email_config = copy.deepcopy(base_config._EMAIL_CONFIG)
        else:
            email_item_config = copy.deepcopy(base_config._EMAIL_ITEM_CONFIG)
            for i, email in self.report_email_config.items():
                for key, value in email_item_config.items():
                    if key not in email.keys():
                        email[key] = value

        self.report_xls_formats = getattr(options, 'xls_formats', None)
        if self.report_xls_formats is None:
            self.report_xls_formats = copy.deepcopy(base_config._XLS_FORMATS)

        self.report_schedule_config = getattr(options, 'schedule_config', None)

    def __repr__(self):
        attrs = [key for key in vars(self).keys() if not key.startswith('_')]

        conf = '\n'.join(f'   {item} = {getattr(self, item)}' for item in sorted(attrs))
        return f'CONFIG (report {self.report_symbol}):\n{conf}'


class ReportMetaclass(type):
    def __new__(cls, name, bases, attrs):
        parents = [b for b in bases if issubclass(b, ReportBase)]
        new_cls = super().__new__(cls, name, bases, attrs)
        if parents:
            attr_meta = attrs.pop('Meta', None)
            new_cls._meta = attr_meta or getattr(new_cls, 'Meta', None)

            # if name is misssing then set it to classname
            if not hasattr(new_cls._meta, 'symbol'):
                new_cls._meta.symbol = new_cls.__module__

            # if name is misssing then set it to classname
            if not hasattr(new_cls._meta, 'name'):
                new_cls._meta.name = new_cls.__qualname__

            # get current working directory for report
            new_cls._meta.report_path = (
                Path(sys.modules[new_cls.__module__].__file__).resolve().parent
            )

            # add decorated function to processors registry
            new_cls._processors = []
            for fn in [
                getattr(new_cls, fn) for fn in dir(new_cls) if not fn.startswith('__')
            ]:
                if getattr(fn, '__processor__', None):
                    new_cls._processors.append(fn)

        return new_cls


class ReportBase(metaclass=ReportMetaclass):
    def __init__(self, base_config: Config):
        self.report_config = ReportConfig(base_config, self._meta)
        self.data_results = dict()
        self.logger = None
        self._setup_dirs = False

    def init_logger(self, logging_level=logging.INFO):
        """Init logger for new run"""

        self.logger = logging.getLogger(self._meta.symbol)
        self.logger.setLevel(logging_level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        filename = '{}_{}.log'.format(
            self._meta.symbol, datetime.today().strftime('%Y%m%d_%H%M%S')
        )

        path = self.report_config.report_logs_path
        if not path.exists():
            path.mkdir(parents=True)
        filepath = path / filename

        file_handler = logging.FileHandler(filepath, mode='w')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging_level)
        self.logger.addHandler(stream_handler)

    def clear_logger(self):
        """Clear loggr after run"""
        self.logger.handlers.clear()

    def setup_dirs(self):
        """Check if dirs exist and if not create missing"""

        if not self._setup_dirs:
            path_list = [
                self.report_config.report_arch_path,
                self.report_config.report_cache_path,
                self.report_config.report_logs_path,
            ]
            for path in path_list:
                path.mkdir(parents=True, exist_ok=True)
            self._setup_dirs = True

    def run_data(self, **kwargs):
        self.setup_dirs()

        # get data
        self._data = DataCreator(
            config=self.report_config, logger=self.logger, **kwargs
        )
        self._data.run(**kwargs)
        # process data
        self._data.run_processors(self._processors)
        return self._data

    def run_excel(self, **kwargs):
        self.setup_dirs()

        # create excel reports
        self._excel = ExcelCreator(
            config=self.report_config, logger=self.logger, **kwargs
        )
        self._excel.set_data_results(self._data.get_results())
        self._excel.run(**kwargs)
        return self._excel

    def run_email(self, **kwargs):
        self.setup_dirs()

        # send email with report attachments
        # cannot access excel object if skipping excel
        attachments = (
            None
            if 'excel' in kwargs.get('skip', [])
            else self._excel.get_email_attachments()
        )
        placeholders = self._data.get_email_placeholders()

        self._email = EmailCreator(
            config=self.report_config,
            logger=self.logger,
            attachments=attachments,
            placeholders=placeholders,
            **kwargs,
        )
        self._email.run(**kwargs)
        return self._email

    def run(self, **kwargs):
        # settup legger for current run
        logging_level = kwargs.get('logging_level', logging.INFO)
        self.init_logger(logging_level)
        self.logger.info('Report update started...')

        skip = kwargs.get('skip', [])

        self.run_data(**kwargs)
        if 'excel' in skip:
            self.logger.info('!!!! Pomija tworzenie plików Excel !!!!')
        else:
            self.run_excel(**kwargs)

        if 'email' in skip:
            self.logger.info('!!!! Pomija wysyłanie widomosci Email !!!!')
        else:
            self.run_email(**kwargs)

        self.logger.info('Report update finished')


class EasyReport:
    _reports: list[ReportBase] = []

    def __init__(self, **kwargs):
        """Initialize base path and base config"""

        self.base_path = Path(kwargs.pop('base_path', '')).resolve()
        self.base_config = Config(self.base_path)
        self._defs_path = None

    @property
    def defs_path(self):
        if self._defs_path is not None:
            return self._defs_path

        if hasattr(self.base_config, 'DEFS_BASE_PATH'):
            return Path(self.base_config.DEFS_BASE_PATH).resolve(strict=False)

        return self.base_path / self.base_config.DEFS_DIR

    @defs_path.setter
    def defs_path(self, path):
        if path is None:
            self._defs_path = None
        else:
            self._defs_path = Path(path).resolve()

    def load_reports(self, report_list: list[str] = None, **kwargs):
        """Load report modules from defs_dir"""

        if report_list is None:
            raise ValueError('Report list must be supplied!')
        self.report_list = report_list

        if kwargs.get('defs_path', None):
            self.defs_path = kwargs.get('defs_path')

        if not str(self.defs_path) in sys.path:
            sys.path.insert(1, str(self.defs_path))

        if not self.defs_path.exists():
            print(f"WARNING - Defs folder: {str(self.defs_path)} does not exist!")
        else:
            print(f"Scanning for report defs in: {str(self.defs_path)}")
            for f in os.scandir(self.defs_path):
                if f.is_dir():
                    name = os.path.basename(f)
                    if name not in self.report_list:
                        continue
                    try:
                        module = importlib.import_module('.report', name)
                        self._reports.append(module.Report(self.base_config))
                    except ImportError as e:
                        print(e.msg)

        return self._reports

    def get_rpt(self, name):
        """Get report class from modules"""

        if not name.endswith('.report'):
            name += '.report'

        rpt = ([r for r in self._reports if r.__module__ == name][:1] or [None])[0]
        if rpt:
            return rpt
        return sys.modules[name].Report(self.base_config)

    def create_boilerplate(self, symbol):
        """Create new report boilerplate"""

        report_path = self.defs_path / symbol
        if report_path.exists():
            raise RuntimeError(f'Folder {str(report_path)} already exists!')

        report_path.mkdir(parents=True, exist_ok=False)
        (report_path / self.base_config.ARCH_DIR).mkdir()
        (report_path / self.base_config.SQL_DIR).mkdir()
        (report_path / self.base_config.CACHE_DIR).mkdir()
        (report_path / self.base_config.LOGS_DIR).mkdir()

        copyfile(
            Path(__file__).resolve().parent / 'boilerplate' / 'report.py',
            report_path / 'report.py',
        )

        # replace #symbol with symbol
        with open(report_path / 'report.py') as f:
            s = f.read()

        with open(report_path / 'report.py', 'w') as f:
            s = s.replace('#symbol', symbol)
            f.write(s)

        print(f'New report {symbol} structure has been created in {report_path}.')

    def refresh(self, rpt=None, **kwargs):
        """Refresh single report"""

        try:
            rpt.run(**kwargs)
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)

    def refresh_reports(self, **kwargs):
        """Refresh all reports"""

        for rpt in self._reports:
            self.refresh(rpt, **kwargs)

    def run(self, **kwargs):
        """Run all loaded and configured reports"""

        self.refresh_reports(**kwargs)
