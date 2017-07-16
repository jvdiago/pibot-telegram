import unittest
from datetime import datetime
from parse_ssh import SSHLog
from ipaddress import IPv4Address


class TestLogSSH(unittest.TestCase):

    def setUp(self):
        pass

    def test_parse_line_correct_access(self):
        ssh_access = 'Jun  4 12:53:04 XPS-12 sshd[26251]: Accepted password for user from 127.0.0.1 port 38906 ssh2'
        correct_match = ['127.0.0.1', 'user', 'Jun  4 12:53:04', None, 200]

        match = SSHLog.parse_line(ssh_access)
        self.assertListEqual(match, correct_match)

        ssh_log = SSHLog(match)
        self.assertTrue(isinstance(ssh_log.get_date(), datetime))
        self.assertTrue(isinstance(ssh_log.get_user(), str))
        self.assertTrue(isinstance(ssh_log.get_status(), int))
        self.assertTrue(isinstance(ssh_log.get_ip(), IPv4Address))

    def test_parse_line_sudo_access(self):
        sudo_access = 'Jun  4 12:53:22 XPS-12 sudo:    user : TTY=pts/20 ; PWD=/home/user ; USER=root ; COMMAND=/bin/su -'
        correct_match = [None, 'user', 'Jun  4 12:53:22', '/bin/su -', 200]

        match = SSHLog.parse_line(sudo_access)
        self.assertListEqual(match, correct_match)

    def test_parse_line_ssh_failure(self):
        ssh_failure = 'Jun  4 12:53:18 XPS-12 sudo: pam_unix(sudo:auth): authentication failure; logname=user uid=1000 euid=0 tty=/dev/pts/20 ruser=user rhost=  user=user'
        correct_match = [None, 'pam_unix', 'Jun  4 12:53:18', None, 400]

        match = SSHLog.parse_line(ssh_failure)
        self.assertListEqual(match, correct_match)

    def test_parse_line_ssh_incorrect(self):
        ssh_failure = 'error'

        match = SSHLog.parse_line(ssh_failure)
        self.assertIsNone(match)


if __name__ == '__main__':
    unittest.main()
