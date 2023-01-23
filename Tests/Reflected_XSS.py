import concurrent.futures
import time
from Tests.Test import Test
import requests
from pprint import pprint
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin


class Reflected_XSS(Test):
    def __init__(self):
        super().__init__()
        self.cancel = False
        self.name = "Reflected XSS"
        self.future = None

    def run(self, url: str):
        self.cancel = False
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self.future = executor.submit(self.scan_xss, url)
        self.future = None

    def scan_xss(self, url):
        """
        Given a `url`, it prints all XSS vulnerable forms and
        returns True if any is vulnerable, False otherwise
        """
        if self.cancel:
            self.cancel_result(url)
            return

        # get all the forms from the URL
        forms = self.get_all_forms(url)
        print(f"[+] Detected {len(forms)} forms on {url}.")
        js_script = "<Script>alert('hi')</scripT>"
        # returning value
        is_vulnerable = False
        # iterate over all forms
        for form in forms:
            if self.cancel:
                self.cancel_result(url)
                return
            form_details = self.get_form_details(form)
            content = self.submit_form(form_details, url, js_script).content.decode()
            if js_script in content:
                print(f"[+] XSS Detected on {url}")
                print(f"[*] Form details:")
                pprint(form_details)
                is_vulnerable = True
                # won't break because we want to print other available vulnerable forms
        return is_vulnerable

    def get_all_forms(self, url):
        """Given a `url`, it returns all forms from the HTML content"""
        soup = bs(requests.get(url).content, "html.parser")
        return soup.find_all("form")

    def get_form_details(self, form):
        """
        This function extracts all possible useful information about an HTML `form`
        """
        details = {}
        # get the form action (target url)
        action = form.attrs.get("action", "").lower()
        # get the form method (POST, GET, etc.)
        method = form.attrs.get("method", "get").lower()
        # get all the input details such as type and name
        inputs = []
        for input_tag in form.find_all("input"):
            input_type = input_tag.attrs.get("type", "text")
            input_name = input_tag.attrs.get("name")
            inputs.append({"type": input_type, "name": input_name})

        for textarea in form.find_all("textarea"):
            # get the name attribute
            textarea_name = textarea.attrs.get("name")
            # set the type as textarea
            textarea_type = "textarea"
            # get the textarea value
            textarea_value = textarea.attrs.get("value", "")
            # add the textarea to the inputs list
            inputs.append({"type": textarea_type, "name": textarea_name, "value": textarea_value})
        # put everything to the resulting dictionary
        details["action"] = action
        details["method"] = method
        details["inputs"] = inputs
        return details

    def submit_form(self, form_details, url, value):
        """
        Submits a form given in `form_details`
        Params:
           form_details (list): a dictionary that contain form information
           url (str): the original URL that contain that form
           value (str): this will be replaced to all text and search inputs
        Returns the HTTP Response after form submission
        """
        # construct the full URL (if the url provided in action is relative)
        target_url = urljoin(url, form_details["action"])
        # get the inputs
        inputs = form_details["inputs"]
        data = {}
        for input in inputs:
            # replace all text and search values with `value`
            if input["type"] == "text" or input["type"] == "search" or input["type"] == "textarea":
                input["value"] = value
            input_name = input.get("name")
            input_value = input.get("value")
            if input_name and input_value:
                # if input name and value are not None,
                # then add them to the data of form submission
                data[input_name] = input_value

        print(f"[+] Submitting malicious payload to {target_url}")
        print(f"[+] Data: {data}")
        if form_details["method"] == "post":
            return requests.post(target_url, data=data)
        else:
            # GET request
            return requests.get(target_url, params=data)

    def cancel_result(self, url):
        result = f'''Reflected XSS for page {url}\n''' \
                 '''Was canceled\n'''
        self.results.append((time.time(), result))
