import logging
import time
import argparse
from urllib.parse import urljoin
from collections import deque
import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)

class Crawler:

    def __init__(self, urls=[], output_file=None):
        self.visited_urls = set()
        self.urls_to_visit = deque(urls)
        self.session = requests.Session()
        self.output_file = output_file

    def download_url(self, url):
        response = self.session.get(url)
        return response.text

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            yield path

    def add_url_to_visit(self, url):
        if url not in self.visited_urls and url not in self.urls_to_visit:
            self.urls_to_visit.append(url)

    def crawl(self, url):
        html = self.download_url(url)
        for url in self.get_linked_urls(url, html):
            self.add_url_to_visit(url)
        time.sleep(1) # add a delay of 1 second between requests

    def run(self):
        with (open(self.output_file, 'a') if self.output_file else None) as f:
            while self.urls_to_visit:
                url = self.urls_to_visit.popleft()
                logging.info(f'Crawling: {url}')
                try:
                    self.crawl(url)
                    if f:
                        f.write(url + '\n')
                    else:
                        print(url)
                except Exception:
                    logging.exception(f'Failed to crawl: {url}')
                finally:
                    self.visited_urls.add(url)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='Starting URL')
    parser.add_argument('--output-file', help='Output file path', default=None)
    args = parser.parse_args()
    
    Crawler(urls=[args.url], output_file=args.output_file).run()