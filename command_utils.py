import subprocess
from abc import ABCMeta


class Command:
    __metaclass__ = ABCMeta

    def execute(self):
        raise Exception("Not implemented")


class LocalCommand(Command):
    def __init__(self, command):
        self.command = command

    def execute(self):
        try:
            p1 = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

            c_out, c_err = p1.communicate()
            c_returncode = p1.returncode
        except Exception as e:
            c_out = ''
            c_err = str(e)
            c_returncode = -1

        return c_out.decode("utf-8"), c_err.decode("utf-8"), int(c_returncode)
