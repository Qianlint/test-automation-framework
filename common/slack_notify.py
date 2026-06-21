import os
import requests
from conf.operation_config import OperationConfig
from common.record_log import logs

conf = OperationConfig()


class SlackNotify:

    def __init__(self):
        self.webhook_url = os.environ.get('SLACK_WEBHOOK_URL') or conf.get_section_for_data('SLACK', 'webhook_url')

    def send(self, message: str):
        payload = {"text": message}
        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 200:
                logs.info('Slack notification sent successfully')
            else:
                logs.error(f'Slack notification failed: {response.status_code}')
        except Exception as e:
            logs.error(f'Slack notification error: {e}')
