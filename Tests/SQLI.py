import concurrent.futures
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import requests

from Tests.Test import Test


class SQLI(Test):
    def __init__(self):
        super().__init__()
        self.results = []
        self.name = f"SQL Injection"
        self.cancel = False
        self.future = None
        self.s = requests.Session()

    def run(self, url: str):
        self.cancel = False
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self.future = executor.submit(self.sql_injection_scan, url)
        self.future = None


    def authenticate(self, url):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=chrome_options)

        driver.get("http://127.0.0.1/dvwa/login.php")
        driver.find_element("name", "username").send_keys("admin")
        driver.find_element("name", "password").send_keys("password")
        driver.find_element("name", "Login").click()

        # get difficulty to low
        driver.get("http://127.0.0.1/dvwa/security.php")
        ddelement = Select(driver.find_element(By.XPATH, "//select[@name='security']"))
        ddelement.select_by_visible_text('Low')
        driver.find_element("name", "seclev_submit").click()
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        return driver.get(url), soup

    def get_forms(self, url):
        if "dvwa" in str(url):
            soup = self.authenticate(url)[1]
        else:
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

    def sql_injection_scan(self, url):
        print(f"running SQLI for {url}")
        forms = self.get_forms(url)
        print(f"[+] Detected {len(forms)} forms on {url}.")

        for form in forms:
            details = self.form_details(form)

            for c in ["\"", "'", "'--", '"--']:
                data = {}

                for input_tag in details["inputs"]:
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
                    self.success()
                else:

                    break

    def success(self, url):
        result = f'''SQL Injection attack vulnerability detected in link {url}'''
        self.results.append((time.time(), result))

    def cancel_result(self, url):
        result = f'''SQL Injection for page {url}\n''' \
                 '''Was canceled\n'''
        self.results.append((time.time(), result))

