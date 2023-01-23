import concurrent.futures
import time

from urllib3 import PoolManager
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from http.cookies import SimpleCookie
import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from pprint import pprint

from Tests.Test import Test


class SQLI(Test):
    def __init__(self):
        super().__init__()
        self.results = []
        self.name = f"SQL Injection"
        self.cancel = False
        self.future = None
        self.s = requests.Session()
        self.s.headers[
            "User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"

    def run(self, url: str):
        self.cancel = False
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self.future = executor.submit(self.sql_injection_scan, url)
        self.future = None

    def sql_injection_scan(self, url):
        if self.cancel:
            self.cancel_result(url)
            return

        print("running")
        forms = self.get_forms(url)
        print(f"[+] Detected {len(forms)} forms on {url}.")

        for form in forms:
            if self.cancel:
                self.cancel_result(url)
                return

            details = self.form_details(form)

            for c in "\"'":
                if self.cancel:
                    self.cancel_result(url)
                    return

                data = {}

                for input_tag in details["inputs"]:
                    if self.cancel:
                        self.cancel_result(url)
                        return

                    if input_tag["type"] == "hidden" or input_tag["value"]:
                        data[input_tag["name"]] = input_tag["value"] + c
                    elif input_tag["type"] != "submit":
                        data[input_tag["name"]] = f"test{c}"

                if details["method"] == "post":
                    res = self.s.post(url, data=data)
                elif details["method"] == "get":
                    res = self.s.get(url, params=data)
                if self.vulnerable(res):
                    print("SQL Injection attack vulnerability detected in link:", url)
                else:
                    break

    def get_forms(self, url):
        soup = BeautifulSoup(self.s.get(url).content, "html.parser")
        return soup.find_all("form")

    def form_details(self, form):
        detailsOfForm = {}
        action = form.attrs.get("action").lower()
        method = form.attrs.get("method", "get").lower()
        inputs = []

        for input_tag in form.find_all("input"):
            input_type = input_tag.attrs.get("type", "text")
            input_name = input_tag.attrs.get("name")
            input_value = input_tag.attrs.get("value", "")
            inputs.append(
                {"type": input_type, "name": input_name, "value": input_value}
            )

        detailsOfForm["action"] = action
        detailsOfForm["method"] = method
        detailsOfForm["inputs"] = inputs
        return detailsOfForm

    def vulnerable(self, response):
        errors = {"quoted string not properly terminated",
                  "unclosed quotation mark after the character string",
                  "you have an error in your sql syntax;"}

        for error in errors:
            if error in response.content.decode().lower():
                return True
        return False

    def cancel_result(self, url):
        result = f'''SQL Injection for page {url}\n''' \
                 '''Was canceled\n'''
        self.results.append((time.time(), result))

