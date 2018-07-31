import json

from bs4 import BeautifulSoup

from comm import RequestsHandler


class SEDailyFeedScraper:
    SE_DAILY_FEED = "https://softwareengineeringdaily.com/feed/podcast/"

    def __init__(self, request_handler=None):
        self.session = request_handler or RequestsHandler()

    def feeds(self, feed_base_url, n=None):
        i = 0
        while not n or i < n:
            formed_url = "{}?paged={}".format(feed_base_url, i + 1)
            print("GET {}".format(formed_url))
            r = self.session.get(formed_url)
            print(r.status_code)
            if 200 <= r.status_code < 300:
                i += 1
                yield r
            else:
                break

    def scrape_feeds(self, file_path=None):
        podcasts = []
        for feed in self.feeds(self.SE_DAILY_FEED):
            podcasts.extend(self.parse_feed(feed))

        if file_path is not None:
            self.write_to_json(podcasts, file_path)
        return podcasts

    def parse_feed(self, feed):
        items = []

        feed_soup = BeautifulSoup(feed.content, 'lxml')
        for item in feed_soup.find_all("item"):
            items.append(self.parse_item(item))

        return items

    def parse_item(self, entry_soup):
        audio_link = entry_soup.find("enclosure")
        transcripts = list(filter(lambda x: x.endswith('.pdf'),
                                  map(lambda l: l.attrs['href'], entry_soup.find("content:encoded").find_all("a"))))
        return {
            "post-id": entry_soup.find("post-id").text,
            "title": entry_soup.find("title").text,
            "audio": audio_link.attrs["url"] if "audio" in audio_link.attrs["type"] else None,
            "transcript": transcripts[0] if len(transcripts) > 0 else None
        }

    @staticmethod
    def write_to_json(podcasts, file_path):
        with open(file_path, 'w') as f:
            json.dump(podcasts, f, indent=4)


if __name__ == '__main__':
    a = SEDailyFeedScraper()
    a.scrape_feeds("res.json")
