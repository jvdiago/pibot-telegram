import unittest
from unittest import mock
from command_utils import LocalCommand


class TestCommand(unittest.TestCase):

    def setUp(self):
        pass

    @mock.patch('command_utils.subprocess.Popen')
    def test_local_command(self, subprocess_mock):
        process_mock = mock.MagicMock()
        attrs = {'communicate.return_value': (b'output', b'error')}
        process_mock.configure_mock(**attrs)
        subprocess_mock.return_value = process_mock

        cmd = LocalCommand('cmd_test')
        c_out, c_err, c_returncode = cmd.execute()

        self.assertEqual(subprocess_mock.call_count, 1)
        self.assertEqual(c_out, 'output')
        self.assertEqual(c_err, 'error')