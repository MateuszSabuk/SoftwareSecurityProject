import concurrent.futures
import os.path
import time

import requests
from bs4 import BeautifulSoup
import sqlite3
from threading import Thread

from mUtilities.DataBaseHandler import DataBaseHandler


def _get_domain(url):
    url_path = url.split("http://")
    if len(url_path) == 1:
        url_path = url.split("https://")
        if len(url_path) == 1:
            return None

    domain = url_path[1].split("/")[0]

    if domain[0:4] == "www.":
        domain = domain[4:]
    return domain


class WebCrawler:
    checked_urls = []
    pages_to_do = 0
    pages_done = 0
    cancel = False
    future = None

    def __init__(self):
        self.file_name = "file_name"
        self.dbh = DataBaseHandler()

    def run_crawl(self, url, pages_dict=None):
        self.checked_urls = []
        self.pages_to_do = 0
        self.pages_done = 0
        self.cancel = False
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self.future = executor.submit(self.crawl, url)
        self.future = None

    def crawl(self, url, pages_dict=None):
        if self.cancel:
            return
        # Check if the URL has already been visited
        if any(d['url'] == url for d in self.checked_urls):
            return

        self.pages_to_do = self.pages_to_do + 1
        print(f"Done: {self.pages_done}/{self.pages_to_do}")

        start_time = time.time()
        # Make an HTTP request to the URL
        response = requests.get(url)
        end_time = time.time()

        self.checked_urls.append({
            "url": url,
            "start_time": start_time,
            "end_time": end_time,
            "elapsed": response.elapsed.total_seconds(),
            "status": response.status_code,
            "reason": response.reason,
        })
        self.dbh.add_url_req_to_db(self.checked_urls[-1])

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Print the URLs of all the links on the page
        print(f"At {url} new links:")
        for link in soup.find_all('a'):
            next_link = str(link.get('href'))
            if _get_domain(next_link) is None and next_link[0] == '/':
                next_link = _get_domain(url) + next_link
            elif _get_domain(next_link) != _get_domain(url):
                continue
            print(next_link)
            self.crawl(next_link)

        if pages_dict is not None:
            for path in pages_dict:
                if url[-1] == "/":
                    next_link = url + path
                else:
                    next_link = url + "/" + path
                self.crawl(next_link)

        self.pages_done = self.pages_done + 1
        # END OF crawl
