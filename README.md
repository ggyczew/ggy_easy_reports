
# Easy Reports


![test](https://github.com/ggyczew/ggy_easy_reports/actions/workflows/test.yml/badge.svg)

---

Easy Reports is a python package which simplifies report configuration, generation and distribution.
Reasons for this package creation are:

- removal of repetitive code from multiple python report scripts written by workers with different level of programming skills
- ability to extract data from two or more databases
- ability to join query results into one final dataset
- simplification of excel file formatting by introducing dictionary bases configuration
- introduction of @processor decorated functions that can do additional data processing and return dataset for excel generator


## Table of Contents

- [Easy Reports](#easy-reports)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Application Configuration](#application-configuration)
    - [Report Configuration](#report-configuration)
    - [Reports Loading](#reports-loading)
    - [Report Generation](#report-generation)
  - [Examples](#examples)
    - [Creation of Report boilerplate](#creation-of-report-boilerplate)
  - [Testing](#testing)
  - [Contributing](#contributing)
  - [License](#license)



## Installation

Create project folder and initialize venv environment

```bash
$ mkdir myproject
$ cd myproject
$ python3 -m venv venv
```

Within the activated environment, use follownig command to install Easy Reports

```bash
$ pip install easy-reports
```

## Usage

A minimal Easy Report looks as below:

```python
from easy_reports import EasyReport
from pathlib import Path

app = EasyReport(base_path=Path(__file__).resolve().parent)
app.base_config.from_pyfile('settings.py')
app.load_reports(report_list=['R001'])
app.run()
```

### Application Configuration

Application default confinguration is defined in defaults.py.
Config parameters can be changed:

- defining environment variable prefixed with EASY_REPORTS
- passed as keyword arguments to EasyReport() 
- loaded from settings.py file

Each Report configuration is created on top of Application's **base_config**.
Selected parameters can be overriden by uppercase attribiutes in Report's [Meta]().

### Report Configuration

By default each Report lives in dedicated folder inside path: ```app.defs_path```

Preferred (default) Report structure consists of:

- report.py module file that contains Report definition such as settings, mappings and [processors]()
- subfolders:
  - ``/sql`` - SQL scripts used to retrive data
  - ``/templ`` - templates of email messages
  - ``/cache`` - cached SQL script's results and dataframes used by Excel creator
  - ``/logs`` - log files  
  - ``/arch`` - generated Excel report files

It is not advised but if necessary default folder paths can be changed in Application configuration step.
For example change of default ``/arch`` can be done by:

- setting evironment variable

```bash
$ export EASY_REPORTS_ARCH_BASE_PATH = '/new_location/arch'
```

- passing keyword argument to EasyReport class constructor
  
```python
app = EasyReport(..., arch_base_path = '/new_location/arch')
```

- setting variable in settings.py
  
```python
ARCH_BASE_PATH = '/new_location/arch'
```

### Reports Loading

Reports loading is done by scaning `app.defs_path` for subfolders containing report.py modules. Modules (Reports) are imported, configured and stored in `app._report` list

### Report Generation

Reports can be generated individually by calling:

```python
# generate selected Report 'R001'
app.refresh(name='R001')
```

or all

```python
app.refresh_all()
or 
app.run()
```

Additional keyword arguments can be passed to the above functions:
One of them, useful while preparing and developing new Report module is **skip** list of blocked parts of Report generation flow

```python
# skip excel creation and email sending
app.refresh(name='R001', skip=['excel','email'])
```

## Examples

### Creation of Report boilerplate

New Report boilerplate can be created using CLI command.

```bash
$ easy-reports create
Enter new report symbol: R7777
Creating report R7777...
```

New subfolder R7777 will be created uder **defs** path.
Report folder will contain report.py module file and four subfolders (as shown below)

```bash
$ cd defs
defs/$ tree
.
└── R7777
    ├── arch
    ├── cache
    ├── logs
    ├── sql
    └── report.py

```

Module file report.py contains all configuration needed to generate report files.
Global (default) configuration from setting.py can be extended by each report.


1. If needed additional aliases and connection strings can be defined as below:

```python
db_list = {
    'alias_1': {'url': 'testing'},
    'alias_2': {'url': 'testing'},
    # 'alias_3': {'url': 'testing'}
}
```
2. List of SQL files with DB aliases and list of fields used to join resulting Dataframes into one aggregate result. 

```python
 sql_list = [
            ('sql_1', 'alias_1', ['PK']),
            ('sql_2', 'alias_2', ['PK']),
            # ('sql_3', 'alias_3', ['PK']),
        ]
```

3. Reports can be sent by email. Email configuration is done in the dictonary shown below. Each email is bound with report files by list of ID's

```python
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
```

4. Reports configuration is done in the dictionary shown below. Each entry is ID of the report.
Report config defines such elements as report filneme, wheather is can be sent by email (added to attachments dictionary), list of sheets. Each sheet must be named and bound to data source (name of Dataframe). Other dictionary keys allow configuration and formatting of the resultig sheet.

```python
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
```

5. Additional processing can be done to aggregate result Dataframe (df_final) or any other stored in self.results dictionary. Functions decorated with @processor are executed in order of definition in the report.py module file. Each function should return dictionary of Name and Dataframe object witch will be added to self.results dictionary.


```python
@processor
def p01(self) -> dict:
    df = self.results['df_final']
    # dataframe processing
    return {'df_result': df}

```

6. Default settings can be overriden by defining variables in the Meta class body:

Default subfolder names can be modified by defining any of below variables
```python
class Report(ReportBase):
  class Meta:
    LOGS_DIR = 'logs'
    ARCH_DIR = 'arch'
    SQL_DIR = 'sql'
    CACHE_DIR = 'cache'
    TEMPL_DIR = 'templ'
    ...
```

If necessary full paths can be provided that will override any other path and folder settings
```python
class Report(ReportBase):
  class Meta:
    logs_path = pathlib.Path('/custom_path/logs').resolve()
    arch_path = pathlib.Path('/custom_path/arch').resolve()
    sql_path = pathlib.Path('/custom_path/sql').resolve()
    cache_path = pathlib.Path('/custom_path/cache').resolve()
    templ_path = pathlib.Path('/custom_path/templ').resolve()
    ...
```

## Testing

Packege can has been tested against three databases: Postgres, MySQL and SqlServer.
Test can be run by deploying stack of Docker containers.

Running command bellow will start container in detached mode and run pytest in the app contaner when all db container are ready.
```bash
$ docker compose up -d
```
While contaner are running in the background tests from host machine can be run. Prior to running pytest or tox aliases to localhost for db-postgres, db-mysql, db-mssql must be added to enable host name resolution.


## Contributing

To contribute to the project, you can:

- Submit bug reports and feature requests through the GitHub issue tracker
- Fork the repository and submit pull requests with bug fixes or new features
- Help improve the documentation

Please read the contributing guidelines for more information.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
