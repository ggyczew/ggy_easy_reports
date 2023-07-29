from datetime import date
import os
import pandas as pd
import logging

from xlsxwriter.utility import xl_range, xl_cell_to_rowcol
import re
import fnmatch


def is_valid_excel_col_range(c):
    """Check if string literal is valid Excel column range"""
    m = re.match(r'^([A-Z]{1,2}:[A-Z]{1,2})$', c)
    return bool(m)


class Sheet:
    # formats = {}

    def __init__(
        self,
        writer,
        data_results,
        sheet_config,
        formats,
        apply_formats=True,
        logger=None,
        **kwargs,
    ):
        self.sheet_config = sheet_config
        self.sheet_name = sheet_config.get('sheet_name')
        self.logger = logger or logging.getLogger('dummy')
        self.formats = formats
        self.df = self.setup_df(data_results)

        self.df.to_excel(writer, self.sheet_name, index=False)
        self.workbook = writer.book
        self.sheet = writer.sheets[self.sheet_name]
        if apply_formats:
            self.apply_formatting()

    def setup_df(self, data_results) -> pd.DataFrame:
        """Prepare dataframe before writing to the sheet"""
        df = None
        if type(data_results) is dict:
            df = data_results.get(self.sheet_config.get('data_src'), None)
        if df is None:
            raise ValueError(
                f"Sheet's '{self.sheet_name}' data_src points to not existing DataFrame!"
            )

        output_columns = self.sheet_config.get('output_columns', [])
        if len(output_columns):
            df = df[output_columns]

        return df

    def _add_header_format(self, headers, header_formats):
        """Add header formatting"""

        # Write the column headers with the defined format.
        for col, header in enumerate(headers):
            # get first format from resolution order [explicit, implicit, default]
            fmt = [
                *filter(None, [header_formats.get(_) for _ in [header, '*']]),
                'header',
            ][0]

            if type(fmt) is dict:
                tag = self.sheet_name + '_header_' + str(col)
                self.formats[tag] = {
                    'format_def': fmt,
                    'format_obj': self.workbook.add_format(fmt),
                }
            else:
                tag = fmt

            self.sheet.write(0, col, header, self.formats.get(tag)['format_obj'])

    def is_header_text_wrapped(self, header, header_formats) -> bool:
        """Check if header has TEXT_WRAP set to True"""

        return any(
            [
                fmt['format_def'].get('text_wrap', False)
                for fmt in [
                    *filter(None, [header_formats.get(_) for _ in [header, '*']])
                ]
            ]
        )

    def _append_number_format(self, header, format: dict = {}):
        """Append number format to existing column format"""

        format_word_list = {
            'percent': ['%', 'PERCENT', 'PROCENT'],
            'currency2': ['PRICE', 'CENA'],
            'currency0': ['VALUE', 'AMOUNT', '_USD', 'WARTOSC', 'KWOTA', '_PLN'],
            'decimal': ['QUANTITY', 'QTY', 'ILOSC'],
            'integer': ['NUMBER', 'STOCK', 'LICZBA', 'STAN'],
        }

        tag = ''
        for format, word_list in format_word_list.items():
            if any(s.upper() in header.upper() for s in word_list):
                tag = format

        if tag:
            fmt = {}
            try:
                fmt = {**format, **self.xls_formats[tag]}
            except TypeError:
                self.logger.error("TypeError for Header: ", header, " format:", format)

            return fmt

        return {}

    def _get_column_width(self, df, header=None):
        """Get column width"""
        if header is None:
            return 20

        column_width = max(df[header].astype(str).map(len).max(), len(header))
        return column_width + 3

    def _get_column_formats(self, header, headers, column_formats):
        """Collect given header options and return them in one dictionary"""

        header_idx = headers.index(header)
        fmt = {}
        for format_target, col_formats in column_formats.items():
            apply_format = False
            if is_valid_excel_col_range(format_target):
                col_name_1, col_name_2 = format_target.split(':')
                col_1 = xl_cell_to_rowcol(col_name_1.upper() + '1')[1]
                col_2 = xl_cell_to_rowcol(col_name_2.upper() + '1')[1]
                if col_1 <= header_idx <= col_2:
                    apply_format = True

            # if format_target == header or format_target == '*' or fnmatch.fnmatch(string, pattern):
            #     apply_format = True

            if fnmatch.fnmatch(header, format_target):
                apply_format = True

            if apply_format:
                if type(col_formats) is dict:
                    fmt.update(col_formats)
                elif type(col_formats) is str:
                    global_format = self.formats.get(col_formats, None)

                    if global_format is not None:
                        fmt.update(global_format['format_def'])
                else:
                    self.logger.error(
                        f'Format literal: {col_formats} is not defined in global XLS_FORMATS!'
                    )

        fmt = self._append_number_format(header, fmt)
        return fmt

    def _get_column_options(self, header, headers, column_options):
        """Collect given header options and return them in one dictionary"""

        header_idx = headers.index(header)
        opt = {}
        for option_target, col_options in column_options.items():
            if is_valid_excel_col_range(option_target):
                col_name_1, col_name_2 = option_target.split(':')
                col_1 = xl_cell_to_rowcol(col_name_1.upper() + '1')[1]
                col_2 = xl_cell_to_rowcol(col_name_2.upper() + '1')[1]
                if col_1 <= header_idx <= col_2:
                    opt.update(col_options)
            elif option_target == header:
                opt.update(col_options)

        return opt

    def _add_column_format(
        self, headers, column_formats, column_options, df, width_ratio=1
    ):
        """Adding field formats"""

        for col, header in enumerate(headers):
            # sprawdzamy szerokosc kolumny
            col_width = self._get_column_width(df, header)
            if col_width > 20:
                col_width = col_width * width_ratio

            col_fmt_def = self._get_column_formats(header, headers, column_formats)
            col_fmt = self.workbook.add_format(col_fmt_def)
            self.formats[self.sheet_name + '_fmt_' + str(col)] = {
                'format_def': col_fmt_def,
                'format_obj': col_fmt,
            }

            col_opt_def = self._get_column_options(header, headers, column_options)
            self.formats[self.sheet_name + '_opt_' + str(col)] = {
                'format_def': col_opt_def,
                'format_obj': None,
            }

            self.sheet.set_column(
                xl_range(0, col, 1048575, col), col_width, col_fmt, col_opt_def
            )

    def _add_data_validation(self, headers, data_validations):
        """Adding data validation"""

        for col, header in enumerate(headers):
            if header in data_validations:
                self.sheet.data_validation(
                    xl_range(0, col, 1048575, col), data_validations.get(header)
                )

    def _add_conditional_format(self, headers, conditional_formats, shape):
        """Add conditional formatting"""

        for col, header in enumerate(headers):
            if header in conditional_formats or '*' in conditional_formats:
                if conditional_formats.get('*'):
                    cond = conditional_formats.get('*')
                else:
                    cond = conditional_formats.get(header)

                if type(cond) is list:
                    cond_list = cond
                else:
                    cond_list = [cond]

                for i in range(len(cond_list)):
                    if conditional_formats.get('*'):
                        cond_format = cond_list[i].get('format')
                        cell_range = xl_range(0, 0, shape[0], shape[1] - 1)
                    else:
                        cond_format = cond_list[i].get('format')
                        cell_range = xl_range(0, col, shape[0], col)

                    if type(cond_format) is dict:
                        format = self.workbook.add_format(cond_format)
                        tag = self.sheet_name + '_cond_' + str(i) + '_' + str(col)
                        self.formats[tag] = format
                        cond_list[i]['format'] = format
                        self.sheet.conditional_format(cell_range, cond_list[i])
                    else:
                        cond_list[i]['format'] = self.formats.get(cond_format)
                        self.sheet.conditional_format(cell_range, cond_list[i])

    def auto_adjust_all_columns_width(self, df):
        """Auto-adjust all columns' width"""

        for column in df:
            column_width = max(df[column].astype(str).map(len).max(), len(column))
            col_idx = df.columns.get_loc(column)
            self.sheet.set_column(col_idx, col_idx, column_width + 3)

    def auto_adjust_column_width(self, df, column_name):
        """Auto-adjust columns' width"""

        column_width = max(df[column_name].astype(str).map(len).max(), len(column_name))
        col_idx = df.columns.get_loc(column_name)
        self.sheet.set_column(col_idx, col_idx, column_width + 3)

    def set_column_width(self, df, column_name, column_width):
        """Manually adjust the wifth of column 'this_is_a_long_column_name"""

        col_idx = df.columns.get_loc(column_name)
        self.sheet.set_column(col_idx, col_idx, column_width)

    def set_freeze_panes(self, cell):
        """Freeze panes abowe and left to passed row/col zero indexed"""

        self.sheet.freeze_panes(cell)

    def set_autofilter(self, shape):
        """Set Autofilter"""

        cell_range = xl_range(0, 0, shape[0], shape[1])
        self.sheet.autofilter(cell_range)

    def apply_formatting(self):
        self.logger.debug('- appying header formats')
        width_ratio = 0.5
        header_formats = self.sheet_config.get('header_formats', {})
        if header_formats:
            headers = self.df.columns.tolist()
            self._add_header_format(headers, header_formats)

        self.logger.debug('- appying columns formats and/or options')
        column_formats = self.sheet_config.get('column_formats', {})
        column_options = self.sheet_config.get('column_options', {})
        if column_formats or column_options:
            self._add_column_format(
                headers,
                column_formats,
                column_options,
                self.df,
                width_ratio,
            )

        self.logger.debug('- appying conditional formats')
        conditional_formats = self.sheet_config.get('conditional_formats', [])
        if conditional_formats:
            self._add_conditional_format(headers, conditional_formats, self.df.shape)

        self.logger.debug('- appying columns data validation')
        data_validations = self.sheet_config.get('data_validations', {})
        if data_validations:
            self._add_data_validation(headers, data_validations)

        self.logger.debug('- appying columns width adjustment')
        self.auto_adjust_all_columns_width(self.df)

        self.logger.debug('- appying freeze panes')
        cell = self.sheet_config.get('freeze_panes', 'A2')
        if cell:
            self.set_freeze_panes(cell)

        self.logger.debug('- appying autofilter')
        self.set_autofilter(self.df.shape)


class Excel:
    filepath = ''
    formats = {}
    options = {}

    def __init__(
        self, file_config=None, config=None, data_results=None, logger=None, **kwargs
    ):
        # perform checks
        if not file_config:
            raise ValueError("Empty File config!")

        if not config:
            raise ValueError("Empty Report config!")

        if not data_results:
            raise ValueError("Empty Data Results!")

        self.file_config = file_config
        self.config = config
        self.data_results = data_results
        self.logger = logger or logging.getLogger('dummy')

        self.filepath = self.config.report_arch_path / self.format_filename(
            self.file_config.get('filename')
        )
        self.writer = pd.ExcelWriter(self.filepath, engine='xlsxwriter')
        # self.workbook = self.writer.book

        self.load_formats()

    def format_filename(self, filename, options=None):
        """Replace known placeholders in filename
        or passed as tuples({placeholder}, value)
        """

        f = filename.replace(r'{date}', date.today().strftime("%Y-%m-%d"))
        if options:
            for placeholder, value in options:
                f = f.replace(placeholder, value)
        return f

    def load_formats(self):
        """Load global formats and store definition dict and format object"""
        for format_tag, format_def in self.config.report_xls_formats.items():
            self.formats[format_tag] = {
                'format_def': format_def,
                'format_obj': self.writer.book.add_format(format_def),
            }

    def write_sheet(self, sheet_id):
        """Create new Sheet instance which writes DF and applies formatting"""

        Sheet(
            self.writer,
            self.data_results,
            self.file_config['sheets'][sheet_id],
            self.formats,
        )

    def write_sheets(self):
        """Write all sheets"""

        for sheet_id in self.file_config.get('sheets'):
            self.write_sheet(sheet_id)

    def close(self):
        """Save excel"""
        self.writer.close()
        return self.filepath


class ExcelCreator:
    def __init__(self, config=None, logger=None, **kwargs):
        # perform checks
        if not config:
            raise ValueError("Empty Report config!")

        self.config = config
        self.logger = logger or logging.getLogger('dummy')
        self.data_results = dict()
        self.email_attachments = dict()

    def set_data_results(self, data_results):
        for name, value in data_results.items():
            if isinstance(value, pd.DataFrame):
                self.data_results[name] = value

    def get_email_attachments(self):
        return self.email_attachments

    def create_file(self, file_id, file_config, **kwargs):
        self.logger.info(f'Writing Excel file in: {self.config.report_arch_path}')

        xls = Excel(file_config, self.config, self.data_results, self.logger, **kwargs)
        xls.write_sheets()
        filepath = xls.close()
        self.logger.info(f'Excel file created: {os.path.split(filepath)[-1]}')

        if file_config.get('send_email', False):
            self.email_attachments[file_id] = filepath

        return filepath

    def run(self, **kwargs):
        self.logger.info('Creation of Excel files...')

        for file_id, file_config in self.config.report_rpt_config.items():
            self.create_file(file_id, file_config, **kwargs)

    def flush(self):
        """Clean after run"""
        self.data_results = dict()
        self.email_attachments = dict()
