import re
from datetime import datetime
import tzlocal
from log_utils import LogRecord
from ipaddress import ip_address
from collections import namedtuple


class SSHLog(LogRecord):
    result = namedtuple(
        'result',
        'succesful_login failed_login sudo')._make([200, 400, 200])

    def __init__(self, log):
        self.ip = log[0]
        self.user = log[1]
        self.str_datetime = log[2]
        self.resource = log[3]
        self.status = log[4]

    @staticmethod
    def parse_line(line):
        log_result = None
        # match a login
        if "Accepted password for" in line:
            log_result = SSHLog.result.succesful_login
        # match a failed login
        elif "Failed password for" in line:
            log_result = SSHLog.result.failed_login
        # match failed auth
        elif ":auth): authentication failure;" in line:
            log_result = SSHLog.result.failed_login
        elif "sudo:" in line:
            log_result = SSHLog.result.sudo

        if log_result:
            resource = SSHLog._parse_cmd(line)
            user = SSHLog._parse_usr(line)
            ip = SSHLog._parse_ip(line)
            str_datetime = SSHLog._parse_date(line)

            return [ip, user, str_datetime, resource, log_result]

        return None

    @staticmethod
    def _parse_usr(line):
        usr = None
        if "Accepted password" in line:
            usr = re.search(r'(\bfor\s)(\w+)', line)
        elif "sudo:" in line:
            usr = re.search(r'(sudo:\s+)(\w+)', line)
        elif "authentication failure" in line:
            usr = re.search(r'USER=\w+', line)
        elif "for invalid user" in line:
            usr = re.search(r'(\buser\s)(\w+)', line)
        if usr is not None:
            return usr.group(2)

        return None

    # parse an IP from a line
    @staticmethod
    def _parse_ip(line):
        ip = re.search(r'(\bfrom\s)(\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b)', line)
        if ip is not None:
            return ip.group(2)

        return None

    # parse a date from the line
    @staticmethod
    def _parse_date(line):
        date = re.search(
            r'^[A-Za-z]{3}\s*[0-9]{1,2}\s[0-9]{1,2}:[0-9]{2}:[0-9]{2}', line)
        if date is not None:
            return date.group(0)

        return None

    # parse a command from a line
    @staticmethod
    def _parse_cmd(line):
        # parse command to end of line
        cmd = re.search(r'(\bCOMMAND=)(.+?$)', line)
        if cmd is not None:
            return cmd.group(2)

        return None

    def get_date(self):
        tz = tzlocal.get_localzone()

        # '2017 ' + 'Jun  4 12:53:04'
        now = datetime.now(tz)
        year = now.strftime('%Y')
        zone = now.strftime('%z')
        full_date = '{0} {1} {2}'.format(
            year,
            self.str_datetime,
            zone
        )
        return datetime.strptime(full_date, "%Y %b  %d %H:%M:%S %z")

    def get_ip(self):
        try:
            return ip_address(self.ip)
        except Exception as e:
            return None

    def get_user(self):
        return self.user

    def get_resource(self):
        return self.resource

    def get_status(self):
        return int(self.status)

    def __str__(self):
        return 'SSH access of user {0} from {1} to {2} on {3}'.format(
            self.get_user(),
            self.get_ip(),
            self.get_resource(),
            self.get_date()
        )
