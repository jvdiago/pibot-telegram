import unittest
from datetime import datetime
from parse_nginx import NginxLog
from ipaddress import IPv4Address


class TestLogNginx(unittest.TestCase):

    def setUp(self):
        pass

    def test_parse_line_correct_access(self):
        http_access = '127.0.0.1 - user [17/Apr/2017:12:23:40 +0200] "GET /url/ HTTP/1.1" 200 3269 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"'

        correct_match = [
            '127.0.0.1',
            'user',
            '17/Apr/2017:12:23:40 +0200',
            '/url/',
            '200',
            '3269',
            '-',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36']

        match = NginxLog.parse_line(http_access)

        self.assertListEqual(match, correct_match)

        nginx_log = NginxLog(match)
        self.assertTrue(isinstance(nginx_log.get_date(), datetime))
        self.assertTrue(isinstance(nginx_log.get_user(), str))
        self.assertTrue(isinstance(nginx_log.get_status(), int))
        self.assertTrue(isinstance(nginx_log.get_resource(), str))
        self.assertTrue(isinstance(nginx_log.get_ip(), IPv4Address))

    def test_parse_line_incorrect_access(self):
        incorrect_access = '127.0.0.1 - user [22/Jun/2017:12:25:35 +0200] "GET /url/ HTTP/1.1" 401 323 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"'
        correct_match = [
            '127.0.0.1',
            'user',
            '22/Jun/2017:12:25:35 +0200',
            '/url/',
            '401',
            '323',
            '-',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36']

        match = NginxLog.parse_line(incorrect_access)
        self.assertListEqual(match, correct_match)

    def test_parse_line_nginx_incorrect(self):
        nginx_failure = 'error'

        match = NginxLog.parse_line(nginx_failure)
        self.assertIsNone(match)


if __name__ == '__main__':
    unittest.main()
