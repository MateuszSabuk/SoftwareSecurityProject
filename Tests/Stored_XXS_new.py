import concurrent.futures
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from Tests.Test import Test


class Stored_XSS_DVWS(Test):
    def __init__(self):
        super().__init__()
        self.cancel = False
        self.name = "Stored XSS DVWS"
        self.future = None

    def run(self, url: str):
        self.cancel = False
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self.future = executor.submit(self.xssStored, url)
        self.future = None

    def xssStored(self, url):
        message = "alert found --> XSS stored attack detected on page: " + url
        self.get_form_details_stored(url)
        self.get_form_details_stored(url)

    def authenticate_stored(self, url):
        message = ""
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
        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.accept()
            print("nullifying alert")
            message = "alert found --> XSS stored attack detected on page: " + url
            print(message)
            self.success(url)
            return message
            return
        except TimeoutException:
            soup = BeautifulSoup(driver.page_source, "html.parser")

        return driver.get(url), soup, driver, message

    def get_form_details_stored(self, url):
        if self.authenticate_stored(url) == "alert found --> XSS stored attack detected on page: " + url:
            return
        if "dvwa" in str(url):
            driver = self.authenticate_stored(url)[2]
            self.authenticate_stored(url)[0]
        else:
            chrome_options: Options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(chrome_options=chrome_options)
            driver.get(url)

        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.accept()
            print("nullifying alert")
            message = "alert found --> XSS stored attack detected on page: " + url
            print(message)
            self.success(url)
            return message
            return
        except TimeoutException:

            if "dvwa" in str(url):
                soup = self.authenticate_stored(url)[1]
            else:
                soup = BeautifulSoup(driver.page_source, "html.parser")

            forms = soup.find_all("form")
            for form in forms:
                # get the form action (target url)
                # action = form.attrs.get("action", "").lower()
                # get the form method (POST, GET, etc.)
                # method = form.attrs.get("method", "get").lower()
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
            for select in form.find_all("select"):
                select_name = select.attrs.get("name")
                select_type = "select"
                select_options = []
                select_default_value = ""
                # iterate over options and get the value of each
                for select_option in select.find_all("option"):
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

            print(inputs)

        i = 0
        while i < len(inputs):
            if (inputs[i]['type'] == 'textarea'):
                driver.find_element("name", inputs[i]['name']).send_keys("<script>alert('hi')</script>")

            if (inputs[i]['type'] == 'text'):
                driver.find_element("name", inputs[i]['name']).send_keys("Michael")

            i = i + 1

        driver.find_element(By.XPATH, "//input[@type ='submit']").click()

    def success(self, url):
        result = f'''Stored XXS Vulnerability discovered for page {url}'''
        self.results.append((time.time(), result))

    def cancel_result(self, url):
        result = f'''Stored XSS for page {url}\n'''\
                '''Was canceled\n'''
        self.results.append((time.time(), result))