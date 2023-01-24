import concurrent.futures
import os.path
import time

import requests
from bs4 import BeautifulSoup
import sqlite3
from threading import Thread

from mQtWrapper import mMainWindow
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
    cancel = False
    future = None

    def __init__(self, main_window_ref):
        self.main_window_ref = main_window_ref
        self.file_name = "file_name"
        self.dbh = DataBaseHandler()
        self.pages_list = None

    def run_crawl(self, url):
        self.checked_urls = []
        self.cancel = False
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self.future = executor.submit(self.crawl, url)
        self.future = None

    def crawl(self, url, additional_path=False):
        if self.cancel:
            return
        # Check if the URL has already been visited
        if any(d['url'] == url for d in self.checked_urls):
            return

        conn_fine = True
        start_time = time.time()
        # Make an HTTP request to the URL
        try:
            response = requests.get(url)
        except:
            print(f"Connection to {url} failed")
            conn_fine = False
        end_time = time.time()
        if conn_fine:
            self.checked_urls.append({
                "url": url,
                "start_time": start_time,
                "end_time": end_time,
                "elapsed": response.elapsed.total_seconds(),
                "status": response.status_code,
                "reason": response.reason,
            })
            self.dbh.add_url_req_to_db(self.checked_urls[-1])
            self.main_window_ref.add_log_signal.emit(self.checked_urls[-1])
            print(f"Added {url}")

            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')

            # Print the URLs of all the links on the page
            for link in soup.find_all('a'):
                next_link = str(link.get('href'))
                if _get_domain(next_link) is None and next_link[0] == '/':
                    next_link = str(_get_domain(url)) + str(next_link)
                elif _get_domain(next_link) != _get_domain(url):
                    continue
                if len(next_link) >= 7:
                    if next_link[0:7] != "http://" and next_link[0:8] != "https://":
                        next_link = f"http://{next_link}"
                self.crawl(next_link)
        # End of if conn_fine

        if self.pages_list is not None and additional_path != True:
            for path in self.pages_list:
                if url[-1] == "/":
                    next_link = url + path
                else:
                    next_link = url + "/" + path
                self.crawl(next_link, additional_path=True)

        # END OF crawl
