import os
import requests

from comm.sessions import create_session
from comm.tor import TorSession


class RequestsHandler:
    def __init__(self, use_tor=True, tor_session_renew_list=(403, 408, 429), max_renews=5):
        self.max_renews = max_renews
        self.renew_list = tor_session_renew_list
        self.use_tor = use_tor

        if use_tor:
            self.tor_session = TorSession()
        else:
            self.tor_session = None

        self.proxies = self.tor_session.proxies if use_tor else {}
        self.session = create_session(proxies=self.proxies)

    def renew_session(self):
        if self.session is not None:
            self.session.close()
            self.session = None

        if self.use_tor:
            self.tor_session.renew_identity()

        self.session = create_session(proxies=self.proxies)

    def get(self, url, attempt=0, **kwargs):
        try:
            res = self.session.get(url, **kwargs)

            if res.status_code in self.renew_list and attempt < self.max_renews:
                self.renew_session()
                return self.get(url, attempt=attempt + 1, **kwargs)

            return res
        except requests.ConnectTimeout as e:
            print(e)
        except requests.ConnectionError as e:
            print(e)
        except requests.HTTPError as e:
            print(e)

    def get_file(self, url, file_path):
        if os.path.isfile(file_path):
            print('Already Exists : %s' % file_path.split('/')[-1])
            return

        req = self.get(url=url, stream=True)

        if req.status_code is 200:
            with open(file_path, 'wb') as f:
                for chunk in req.iter_content(1024):
                    f.write(chunk)

            return True
        else:
            print(req.status_code)
            # print(req.content)
            return False

    def close(self):
        if hasattr(self, 'session') and self.session:
            self.session.close()

    def __del__(self):
        self.close()
