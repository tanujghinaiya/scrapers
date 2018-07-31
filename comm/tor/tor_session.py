import random
import shutil
import string
import subprocess

import stem.process
import tempfile

from stem import Signal
from stem.control import Controller


class TorSession:
    def __init__(self, data_directory=None, control_password=None):
        if data_directory is None:
            data_directory = tempfile.mkdtemp()

        if control_password is None:
            control_password = self.generate_random_password(20)

        self.data_directory = data_directory
        self.control_password = control_password

        self.socks_port, self.control_port, self.tor_process = self.init_tor_process()

    def init_tor_process(self, attempt=0, max_attempt=5):
        socks_port = random.randint(10240, 65535)
        control_port = random.randint(10240, 65535)

        try:
            process = stem.process.launch_tor_with_config(
                config={
                    'SocksPort': str(socks_port),
                    'ControlPort': str(control_port),
                    'HashedControlPassword': self.generate_tor_password(self.control_password),
                    'DataDirectory': self.data_directory
                },
                init_msg_handler=self.print_bootstrap_lines
            )
            return socks_port, control_port, process
        except OSError:
            if attempt < max_attempt:
                return self.init_tor_process(attempt + 1, max_attempt)
            raise

    def renew_identity(self):
        print('renewing tor session identity for tor:{}....'.format(self.socks_port))
        with Controller.from_port(port=self.control_port) as controller:
            controller.authenticate(password=self.control_password)
            controller.signal(Signal.NEWNYM)
        print('session identity renewed')

    def terminate(self):
        if self.tor_process is None:
            print("not running, ignoring terminate command for tor:{}".format(self.socks_port))
            return
        print("terminating tor:{}...".format(self.socks_port))
        self.tor_process.terminate()
        shutil.rmtree(self.data_directory, ignore_errors=True)
        self.tor_process = None
        print("tor:{} terminated".format(self.socks_port))

    @staticmethod
    def generate_tor_password(pwd):
        p = subprocess.Popen(['tor', '--hash-password', str(pwd)], stdout=subprocess.PIPE, universal_newlines=True)
        pwd, error = p.communicate()

        if error is not None:
            raise Exception(error)

        return pwd.strip()

    @staticmethod
    def print_bootstrap_lines(line):
        if 'Done' in line:
            # print(term.format(line, term.Color.BLUE))
            print('tor ready..')

    @staticmethod
    def generate_random_password(length):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

    @property
    def proxies(self):
        return {
            'http': 'socks5://127.0.0.1:{}'.format(self.socks_port),
            'https': 'socks5://127.0.0.1:{}'.format(self.socks_port)
        }

    def __del__(self):
        self.terminate()
