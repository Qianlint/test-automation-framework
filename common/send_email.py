import smtplib
from email.mime.text import MIMEText
from conf.operation_config import OperationConfig
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication  # Attachment
from conf import setting
from common.record_log import logs
import re

conf = OperationConfig()


class SendEmail(object):
    """Build the email subject, body, and attachment."""

    def __init__(
            self,
            host=conf.get_section_for_data('EMAIL', 'host'),
            user=conf.get_section_for_data('EMAIL', 'user'),
            passwd=conf.get_section_for_data('EMAIL', 'passwd')):
        self.__host = host
        self.__user = user
        self.__passwd = passwd

    def build_content(self, subject, email_content, addressee=None, atta_file=None):
        """
        Build the email body and attachment.
        @param subject: Email subject.
        @param addressee: Recipients, separated by semicolons in the configuration file.
        @param email_content: Email body.
        @return:
        """
        user = 'liaison officer' + '<' + self.__user + '>'
        # Recipients
        if addressee is None:
            addressee = conf.get_section_for_data('EMAIL', 'addressee').split(';')
        else:
            addressee = addressee.split(';')
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = user
        message['To'] = ';'.join([re.search(r'(.*)(@)', emi).group(1) + "<" + emi + ">" for emi in addressee])

        # Email body
        text = MIMEText(email_content, _subtype='plain', _charset='utf-8')
        message.attach(text)

        if atta_file is not None:
            # Attachment
            atta = MIMEApplication(open(atta_file, 'rb').read())
            atta['Content-Type'] = 'application/octet-stream'
            atta['Content-Disposition'] = 'attachment; filename="testresult.xls"'
            message.attach(atta)

        try:
            service = smtplib.SMTP_SSL(self.__host)
            service.login(self.__user, self.__passwd)
            service.sendmail(user, addressee, message.as_string())
        except smtplib.SMTPConnectError as e:
            logs.error('Failed to connect to the email server!', e)
        except smtplib.SMTPAuthenticationError as e:
            logs.error('Email server authentication failed. Enable POP3/SMTP and use an authorization code as the password!', e)
        except smtplib.SMTPSenderRefused as e:
            logs.error('The sender address has not been verified!', e)
        except smtplib.SMTPDataError as e:
            logs.error('The email contains prohibited information or was identified as spam!', e)
        except Exception as e:
            logs.error(e)
        else:
            logs.info('Email sent successfully!')
            service.quit()


class BuildEmail(SendEmail):
    """Send an email."""

    # def __int__(self, host, user, passwd):
    #     super(BuildEmail, self).__init__(host, user, passwd)

    def main(self, success, failed, error, not_running, atta_file=None, *args):
        """
        :param success: list type
        :param failed: list type
        :param error: list type
        :param not_running: list type
        :param atta_file: Attachment path.
        :param args:
        :return:
        """
        success_num = len(success)
        fail_num = len(failed)
        error_num = len(error)
        notrun_num = len(not_running)
        total = success_num + fail_num + error_num + notrun_num
        execute_case = success_num + fail_num
        pass_result = "%.2f%%" % (success_num / execute_case * 100)
        fail_result = "%.2f%%" % (fail_num / execute_case * 100)
        err_result = "%.2f%%" % (error_num / execute_case * 100)
        # Set the email subject, recipients, and body.
        subject = conf.get_section_for_data('EMAIL', 'subject')
        addressee = conf.get_section_for_data('EMAIL', 'addressee').split(';')
        content = "     ***Project API tests: %s APIs tested, %s passed, %s failed, %s errors, %s not run; pass rate %s, failure rate %s, error rate %s." \
                  "See the attachment for detailed test results." % (
                      total, success_num, fail_num, error_num, notrun_num, pass_result, fail_result, err_result)
        self.build_content(addressee, subject, content, atta_file)
