import json
import os

from scrapers.file_scraper import FileScraper
from scrapers.se_daily.archives_scraper import SEDailyFeedScraper
from tasks.handler import exec_tasks


def scrape_task_from_podcast(podcast, out_dir):
    audio_url = podcast['audio']
    yield FileScraper(audio_url, os.path.join(out_dir, podcast['post-id'], audio_url.split("/")[-1]))

    transcript_url = podcast['transcript']
    if transcript_url is not None:
        yield FileScraper(transcript_url, os.path.join(out_dir, podcast['post-id'], transcript_url.split("/")[-1]))


def scrape_se_daily_podcast_tasks(podcasts, out_dir):
    for podcast in podcasts:
        for task in scrape_task_from_podcast(podcast, out_dir):
            yield task


def get_all_podcasts(out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    podcasts_fp = os.path.join(os.path.join(out_dir, "podcasts.json"))
    if os.path.exists(podcasts_fp):
        with open(podcasts_fp) as f:
            podcasts = json.load(f)
    else:
        scraper = SEDailyFeedScraper()
        podcasts = scraper.scrape_feeds(podcasts_fp)
    return podcasts


if __name__ == '__main__':
    output_dir = os.path.join(os.getcwd(), 'res')
    podcasts = get_all_podcasts(output_dir)
    exec_tasks(scrape_se_daily_podcast_tasks(podcasts, output_dir))
