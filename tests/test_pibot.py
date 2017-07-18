import unittest
from log_utils import LogReader, LogRecord
from io import StringIO
from unittest import mock
import types
from pibot import logparser_job, cmd_job, auto_start, job_status
from datetime import datetime
import ipaddress
import settings
import tzlocal


class TestLogReader(unittest.TestCase):

    def setUp(self):
        settings.LOG_FILE = None
        settings.JOBS = {
            'nginx': {
                'log_file': 'test.log',
                'log_reader': None,
                'status_limits': [200, 400],
                'filter_networks': [],
                'default_interval': 300,
            },
            'test': {}
        }

    @mock.patch(
        'log_utils.open',
        mock.MagicMock(return_value=StringIO('test1\ntest2\n')))
    def test_get_record(self):
        log_record = mock.create_autospec(LogRecord)
        log_record.parse_line.return_value = [0]

        log_reader = LogReader(log_record, 'test')
        record = log_reader.get_records()

        self.assertIsInstance(record, types.GeneratorType)
        self.assertEqual(len(list(record)), 2)
        self.assertTrue(log_record.parse_line.called)

    @mock.patch('pibot.LogReader', autospec=True)
    def test_logparser_job(self, log_reader_mock):
        log_record = mock.create_autospec(LogRecord)

        tz = tzlocal.get_localzone()
        log_record.get_date.return_value = datetime.now(tz)
        log_record.get_status.side_effect = [200, 500]
        log_record.get_ip.return_value = ipaddress.ip_network('10.0.0.1/32')

        log_reader_mock.return_value.get_records.side_effect = [
            [log_record, log_record],
        ]
        job = mock.MagicMock(interval=5)
        job.configure_mock(name='nginx')
        bot = mock.MagicMock()

        logparser_job(bot, job)
        self.assertEqual(bot.sendMessage.call_count, 1)

    @mock.patch('pibot.LocalCommand', autospec=True)
    def test_cmd_job(self, command_mock):
        command_mock.return_value.execute.return_value = ['', '', 0]

        cmd = 'test'
        settings.CMD = {
            cmd: cmd
        }

        bot = mock.MagicMock()
        update = mock.MagicMock()

        cmd_job(bot, update, [cmd], None, None)
        cmd_job(bot, update, ['fail'], None, None)

        self.assertEqual(command_mock.return_value.execute.call_count, 1)
        self.assertEqual(update.message.reply_text.call_count, 2)

    def test_auto_start(self):
        job_queue = mock.MagicMock()
        bot = mock.MagicMock()
        auto_start(bot, job_queue)
        self.assertEqual(job_queue.run_repeating.call_count, 1)

    def test_job_status(self):
        job_name = 'nginx'
        wrong_job_name = 'test'

        job_queue = mock.MagicMock()
        job_name_mock = mock.MagicMock()
        job_name_mock.configure_mock(name=job_name)
        job_queue.jobs.return_value = [job_name_mock]
        update = mock.MagicMock()

        job_status(
            bot=None,
            update=update,
            job_queue=job_queue,
            args=[job_name],
            chat_data=None)
        update.message.reply_text.assert_called_with(
            '{0} job is running'.format(job_name))

        job_status(
            bot=None,
            update=update,
            job_queue=job_queue,
            args=[wrong_job_name],
            chat_data=None)
        update.message.reply_text.assert_called_with(
            '{0} job is not running'.format(wrong_job_name))


if __name__ == '__main__':
    unittest.main()
