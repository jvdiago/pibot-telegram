# Global variables
import ipaddress
from parse_ssh import SSHLog
from parse_nginx import NginxLog

# filename to log to file, None to log on the console.
LOG_FILE = 'pibot.log'

JOBS = {
    'ssh': {
        'log_file': '/var/log/auth.log',
        'log_reader': SSHLog,
        'status_limits': [200, 400],
        'filter_networks': [ipaddress.ip_network('192.168.1.0/24')]
    },
    'nginx': {
        'log_file': '/var/log/nginx/access.log',
        'log_reader': NginxLog,
        'status_limits': [200, 400],
        'filter_networks': [ipaddress.ip_network('192.168.1.0/24')]
    }
}

CMD = {
    'hostname': ['hostname', '-s'],
    'reboot': ['reboot']
}

TELEGRAM_TOKEN = ""
