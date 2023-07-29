import os
from pathlib import Path
from datetime import date
from . import email_smtplib
import copy


def replace_common_placeholders(text: str) -> str:
    """Replace known placeholders in text"""
    t = text.replace(r'{date}', date.today().strftime("%Y-%m-%d"))
    return t


class EmailCreator:
    def __init__(self, config=None, logger=None, **kwargs):
        self.config = config
        self.logger = logger
        self.email_config = self.config.report_email_config
        if not self.email_config:
            raise ValueError("Empty email configuration!")

        self._engine = getattr(config, 'email_engine')
        if self._engine == 'smtplib':
            self._email = email_smtplib.Email
        # elif self._engine == 'exchangelib':
        #     # self._email = email_exchangelib.Email
        #     pass
        # elif self._engine == 'win32com':
        #     #  self._email = email_win32com.Email
        #     pass
        else:
            raise ValueError(f'Unknown email engine {self._engine}')

        self.placeholders = kwargs.get('placeholders', dict())
        self.attachments = kwargs.get('attachments', dict())

    def send_email(self, email_config):
        if email_config['to'] == '':
            self.logger.error('Incomplete email config Recipient must be defined!')
            return
        if email_config['subject'] == '':
            self.logger.error('Incomplete email config Subject must be defined!')
            return

        # if os.path.isfile(os.path.join(self.templ_dir, email_config.get('template'))):
        templ_file_path = self.config.report_templ_path / email_config.get('template')
        if templ_file_path.is_file():
            template = open(templ_file_path, 'r', encoding='UTF8').read()
            # Replace template placeholders
            for i in self.placeholders:
                template = template.replace('@' + i, str(self.placeholders[i]))

            # Replace body with template content
            email_config['body'] = replace_common_placeholders(template)

        # Replace placeholders in subject
        email_config['subject'] = replace_common_placeholders(email_config['subject'])

        def get_attachment_filepath(file_id):
            """Get by ID attachment filepath"""
            for id, filepath in self.attachments.items():
                if id == file_id:
                    return filepath
            # attachment not found or report file has set send_email=False
            return None

        for file_id in email_config.get('attachments_rpt_id'):
            filepath = get_attachment_filepath(file_id)
            if filepath:
                email_config.get('attachments', []).append(filepath)
            else:
                self.logger.info(
                    f'Attachment Id: {file_id} not found or has set send_email=False'
                )

        email = self._email(email_config, self.config, self.logger)
        email.send()

    def run(self, **kwargs):
        self.logger.info('Wysyłanie wiadomosci email...')
        for i, config in self.email_config.items():
            email_config = copy.deepcopy(config)
            self.send_email(email_config)
