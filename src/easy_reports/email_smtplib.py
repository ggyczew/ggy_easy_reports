from datetime import datetime
import os
import smtplib, ssl
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Email:
    def __init__(self, email_config=None, config=None, logger=None, **kwargs):
        if email_config is None:
            email_config = {}

        self.server = config.email_server
        self.port = config.email_port
        self.user = config.email_user
        self.password = config.email_password

        self.to = ";".join(
            [email.strip() for email in (email_config.get('to', '')).split(";")]
        )
        self.cc = ";".join(
            [email.strip() for email in (email_config.get('cc', '')).split(";")]
        )
        self.onbehalf = email_config.get('onbehalf', '')
        self.subject = email_config.get('subject', '')
        self.body = email_config.get('body', '')
        self.attachments = email_config.get('attachments', [])

        self.logger = logger

    def __repr__(self):
        x = '\n\t To:' + self.to + '\n'
        x += '\t Cc:' + self.cc + '\n'
        x += '\t On Behalf:' + self.onbehalf + '\n'
        x += '\t Attachments:' + ';'.join(self.attachments) + '\n'
        x += '\t Subject:' + self.subject + '\n'
        x += '\t Body:' + self.body + '\n'
        return x

    @property
    def context_time(self):
        return f'[{self.context}  {datetime.now()}]'

    def send(self):
        try:
            self.logger.debug(f'On behalf: {self.onbehalf}')
            self.logger.debug(f'To: {self.to}')
            self.logger.debug(f'Subject: {self.subject}')
            self.logger.debug(f'Server: {self.server}')
            self.logger.debug(f'Port: {self.port}')

            context = ssl.create_default_context()
            self.logger.debug(f'Context: {context}')

            with smtplib.SMTP(self.server, self.port) as server:
                if server.has_extn('STARTTLS'):
                    server.starttls(context=context)
                if 'auth' in server.esmtp_features:
                    server.login(self.user, self.password)

                msg = MIMEMultipart('alternative')

                msg['To'] = self.to
                if self.cc:
                    msg['Cc'] = self.cc

                msg['Subject'] = self.subject
                msg.attach(MIMEText(self.body, 'html'))

                for a in self.attachments:
                    with open(a, "rb") as f:
                        part = MIMEApplication(f.read(), Name=os.path.basename(a))
                    # After the file is closed
                    part[
                        'Content-Disposition'
                    ] = 'attachment; filename="%s"' % os.path.basename(a)
                    msg.attach(part)

                server.sendmail(
                    self.onbehalf,
                    [email.strip() for email in (self.to).split(";")]
                    + [email.strip() for email in (self.cc).split(";")],
                    msg.as_string(),
                )

            self.logger.info(f'Email has been sent. Subject: {self.subject}')

        except Exception as e:
            self.logger.error(f'Error while sending Email! {e}')
