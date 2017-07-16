import re
from log_utils import LogRecord
from ipaddress import ip_address
from datetime import datetime


class NginxLog(LogRecord):
    pat = (
        r''
        '(\d+.\d+.\d+.\d+)'  # IP address
        '\s-\s(-|\w+)\s'  # User
        '\[(.+)\]\s'  # datetime
        '"GET\s(.+)\s\w+/.+"\s'  # requested file
        '(\d+)\s'  # status
        '(\d+)\s'  # bandwidth
        '"(.+)"\s'  # referrer
        '"(.+)"'  # user agent
    )
    log_regex = re.compile(pat)

    def __init__(self, log):
        self.ip = log[0]
        self.user = log[1]
        self.str_datetime = log[2]
        self.resource = log[3]
        self.status = log[4]
        self.bandwidth = log[5]
        self.referrer = log[6]
        self.user_agent = log[7]

    @staticmethod
    def parse_line(line):
        match = re.match(NginxLog.log_regex, line)
        if match:
            return list(match.groups())

        return None

    def get_date(self):
        return datetime.strptime(self.str_datetime, "%d/%b/%Y:%H:%M:%S %z")

    def get_ip(self):
        return ip_address(self.ip)

    def get_user(self):
        return self.user

    def get_resource(self):
        return self.resource

    def get_status(self):
        return int(self.status)

    def __str__(self):
        return 'Web access of user {0} from {1} to {2} on {3}'.format(
            self.get_user(),
            self.get_ip(),
            self.get_resource(),
            self.get_date()
        )
