import concurrent.futures
import time

from urllib3 import PoolManager
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from http.cookies import SimpleCookie
import requests

from Tests.Test import Test


class SQLI(Test):
    HTTP = PoolManager()
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }

    def __init__(self):
        super().__init__()
        self.results = []
        self.name = f"SQLI"
        self.cancel = False
        self.future = None

    def run(self, url: str):
        self.cancel = False
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self.future = executor.submit(self.bruteCracking, url)
        self.future = None

    # In order to receive the cookies sent in the request, we use This function, note: we already have a login page
    def connexion_page(self, response, username, password, base_url, folder=""):
        scrapper = BeautifulSoup(response.data, features="lxml")
        formulaire = scrapper.find_all(
            "form")  # being used to store a list of all the HTML "form" elements found in the page source.
        form = formulaire[0]
        action_page = form["action"] if '/' == form["action"][0] else "/" + form["action"]
        action_folder = ""

        if folder != "":
            action_folder = "/" + folder
        target_url = "http://" + urlparse(base_url).hostname + action_folder + action_page
        payload = {}

        inputs = form.find_all("input")

        for i in inputs:
            if i["name"] == "username":
                payload["username"] = username
            elif i["name"] == "password":
                payload["password"] = password
            else:
                payload[i["name"]] = i["value"]
        cookie = SimpleCookie()
        cookie.load(response.getheader("Set-Cookie"))
        cookies = {}

        for key, morsel in cookie.items():
            cookies[key] = morsel.value
        r = requests.post(target_url, payload, cookies=cookies)

        if "Failed attempt of login" in r.text:

            print("Failed attempt of login")
            pass
        else:

            return cookies

    # The output of This function are all the forms of the page we want to scan
    def get_form(self, url, cookie):
        soup_object = BeautifulSoup(requests.get(url, headers=self.HEADERS, cookies=cookie).content, "html.parser")
        return soup_object.find_all("forms")

    # Output: All the information  from a form
    def get_form_info(self, forms):
        info = {}

        for form in forms:
            try:
                action = form.attrs.get("action").lower()
            except:
                action = None
            method = form.attrs.get("method", "get").lower()
            inputs = []

            for input_tag in form.find_all("input"):
                input_type = input_tag.attrs.get("type", "text")
                input_name = input_tag.attrs.get("name")
                input_value = input_tag.attrs.get("value", "")
                inputs.append({"type": input_type, "name": input_name, "value": input_value})
            info["action"] = action
            info["method"] = method
            info["inputs"] = inputs

        return info

    # Tests if the url is vulnerable to the sql injection, returns true or false
    def vulnerable_url(self, response):
        errors = {
            " error in the sql syntax;",
            "warning: mysql",
            "Unproper end after the string character",
            "quoted string is not properly terminated",
        }
        for error in errors:
            if error in response.content.decode().lower() or response.status_code >= 500:
                return True
        return False

    # the input : incomplete sql request of a form , Output: determine if it is vulnerable to an sql injection
    def sql_injection_scanner(self, url, cookie={}):
        status = 0
        forms = self.get_form(url, cookie)
        print(f"{len(forms)} forms detected on {url}.")
        form_infos = self.get_form_info(forms)
        for c in "\"'":
            data = {}
            for input_tag in form_infos["inputs"]:
                if input_tag["type"] == "hidden" or input_tag["value"]:
                    try:
                        data[input_tag["name"]] = input_tag["value"] + c
                    except:
                        pass
                elif input_tag["type"] != "submit":
                    data[input_tag["name"]] = f"test{c}"
            url = urljoin(url, form_infos["action"])
            if form_infos["method"] == "post":
                res = requests.post(url, headers=self.HEADERS, data=data, cookies=cookie)
            elif form_infos["method"] == "get":
                res = requests.get(url, headers=self.HEADERS, params=data, cookies=cookie)
            if self.vulnerable_url(res):
                status = 1
                vulnerable_form = form_infos
                break
        if status == 1:
            print(f"One SQL injection vulnerability is detected on the form {vulnerable_form}")
        else:
            print("No SQL Injection vulnerability detected")

    def sqli_main(self, target_test_url):
        response = self.HTTP.request('GET URL', target_test_url, None, self.HEADERS)
        if response.status == 200:
            pass
        try:
            redirect_url = response.retries.history[-1].redirect_location
            if 'Login' in redirect_url:
                print()
                answer = input("Do you need to login ? [Yes/No] : ")
                if answer == 'Yes' or answer == '':
                    username = input("Fill in the username : ")
                    password = input("Fill in the password : ")
                    dvwa = input("Are you using DVWA ? [Yes/No] : ")
                    if dvwa == 'Yes' or answer == '':
                        folder = "DVWA"
                    else:
                        folder = ""
                    cookie = self.connexion_page(response, username, password, target_test_url, folder)
                    self.sql_injection_scanner(target_test_url, cookie)
                else:
                    answer = input("Do you want to try SQL injection on this page ? [Yes/No] : ")
                    if answer == 'Yes' or answer == '':
                        self.sql_injection_scanner(target_test_url)
            else:
                self.sql_injection_scanner(redirect_url)
        except:
            self.sql_injection_scanner(target_test_url)
