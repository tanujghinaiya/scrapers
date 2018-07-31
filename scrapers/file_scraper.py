import os
import shutil


class FileScraper:
    def __init__(self, url, fp):
        self.fp = fp
        self.url = url

    def __call__(self, requests_handler, *args, **kwargs):
        if os.path.exists(self.fp):
            print("file already exists")
            return

        print("downloading {} to {}".format(self.url, self.fp))

        if not os.path.exists(os.path.dirname(self.fp)):
            os.makedirs(os.path.dirname(self.fp))

        temp_fp = "{}.crdownload".format(self.fp)
        requests_handler.get_file(self.url, temp_fp)
        shutil.move(temp_fp, self.fp)

    def __str__(self):
        return str({
            "url": self.url,
            "fp": self.fp
        })
