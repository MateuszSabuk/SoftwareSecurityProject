import concurrent.futures
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select

from Tests.Test import Test


class DOM_XSS_DVWS(Test):
    def __init__(self):
        super().__init__()
        self.cancel = False
        self.name = "DOM XSS DVWS"
        self.future = None

        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)

    def run(self, url: str):
        self.cancel = False
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self.future = executor.submit(self.check_xss_Dom, url)
        self.future = None

    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from bs4 import BeautifulSoup
    from selenium.webdriver.support.ui import Select

    def authenticate_Dom(self, url):
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
        return driver.get(url), soup, driver

    # 1. Check form on the page.
    def check_xss_Dom(self, url):
        if self.cancel:
            self.cancel_result(url)
            return
        if "dvwa" in str(url):
            driver = self.authenticate_Dom(url)[2]
            self.authenticate_Dom(url)[0]

            soup = self.authenticate_Dom(url)[1]
        else:
            chrome_options: Options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(chrome_options=chrome_options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")

        forms = soup.find_all("form")
        details = {}
        script_matches = ["document.URL", "document.write", "document.location", "eval(", "window.location"]

        for form in forms:
            if self.cancel:
                self.cancel_result(url)
                return

            inputs = []

            for input_tag in form.find_all("input"):
                if self.cancel:
                    self.cancel_result(url)
                    return
                input_type = input_tag.attrs.get("type", "text")
                input_name = input_tag.attrs.get("name")
                input_value = input_tag.attrs.get("value", "")
                inputs.append({"type": input_type, "name": input_name, "value": input_value})
            for select in form.find_all("select"):
                if self.cancel:
                    self.cancel_result(url)
                    return
                select_name = select.attrs.get("name")
                select_type = "select"
                select_options = []
                select_default_value = ""
                # iterate over options and get the value of each
                for select_option in select.find_all("option"):
                    if self.cancel:
                        self.cancel_result(url)
                        return
                    # get the option value used to submit the form
                    option_value = select_option.attrs.get("value")
                    if option_value:
                        select_options.append(option_value)
                        if select_option.attrs.get("selected"):
                            # if 'selected' attribute is set, set this option as default
                            select_default_value = option_value
                if not select_default_value and select_options:
                    # if the default is not set, and there are options, take the first option as default
                    select_default_value = select_options[0]
                # add the select to the inputs list
                inputs.append(
                    {"type": select_type, "name": select_name, "values": select_options, "value": select_default_value})
            for textarea in form.find_all("textarea"):
                if self.cancel:
                    self.cancel_result(url)
                    return
                textarea_name = textarea.attrs.get("name")
                textarea_type = "textarea"
                textarea_value = textarea.attrs.get("value", "")
                inputs.append({"type": textarea_type, "name": textarea_name, "value": textarea_value})

            # Submitting the data and getting the URL of Submission
            for input_tag in inputs:
                if self.cancel:
                    self.cancel_result(url)
                    return
                if input_tag['type'] == 'email':
                    driver.find_element("name", input_tag['name']).send_keys("michael.jreij@gmail.com")
                if input_tag['type'] == 'text' or input_tag['type'] == 'textarea' or input_tag['type'] == 'password' or \
                        input_tag['type'] == 'search':
                    driver.find_element("name", input_tag['name']).send_keys("Hello World11234")

            import time
            for submit_button in inputs:
                if self.cancel:
                    self.cancel_result(url)
                    return
                if submit_button['type'] == 'submit':
                    submit_value = submit_button['value']
                    driver.find_element(By.XPATH, "//input[@value='" + str(submit_value) + "']").click()
                    time.sleep(2.4)
                    submitted_url = str(driver.current_url)

                    # search the names of input in the Sumbitted URL
                    url_val = []
                    for input_name in inputs:
                        if self.cancel:
                            self.cancel_result(url)
                            return
                        if str(input_name['name']) in submitted_url:
                            print("DOM XXS Vulnerability discovered in the input field with name is: " + str(
                                input_name['name']) + "at: " + url)
                            url_val.append(
                                {"type": input_name['type'], "name": input_name['name'], "value": input_name['value']})
                            self.success(url, input_name)

                            # search through all the names of the input and see if they appear in <script>
                            scripts = soup.find_all("script")
                            for script in scripts:
                                if self.cancel:
                                    self.cancel_result(url)
                                    return
                                for match in script_matches:
                                    if self.cancel:
                                        self.cancel_result(url)
                                        return
                                    for val in url_val:
                                        if self.cancel:
                                            self.cancel_result(url)
                                            return
                                        if str(match) in str(script) and str(val['name']) in str(script):
                                            print("the field is related to Vulnerable JS Components: " + str(
                                                match) + " " + str(val["name"]))

    def success(self, url, input_name):
        result = f'''DOM XXS Vulnerability discovered for page {url}\n'''\
                f'''in the input field with name: {input_name['name']}'''
        self.results.append((time.time(), result))

    def cancel_result(self, url):
        result = f'''DOM XSS for page {url}\n''' \
                 '''Was canceled\n'''
        self.results.append((time.time(), result))
