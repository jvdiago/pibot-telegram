from abc import ABCMeta, abstractmethod


class LogReader:
    def __init__(self, log, log_path):
        self.log = log
        self.log_path = log_path

    def get_records(self):
        with open(self.log_path) as fp:
            for line in fp:
                # match = re.match(self.log.get_regex(), line)
                match = self.log.parse_line(line)
                if match:
                    yield self.log(match)


class LogRecord:
    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def parse_line(line):
        raise Exception("Not implemented")

    @abstractmethod
    def get_ip(self):
        return None

    @abstractmethod
    def get_user(self):
        return None

    @abstractmethod
    def get_resource(self):
        return None

    @abstractmethod
    def get_date(self):
        return None

    @abstractmethod
    def get_status(self):
        return None

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
