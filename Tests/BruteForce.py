import concurrent.futures

from Tests.Test import Test
from mQtWrapper.pdfGen import PdfGen
import requests


class BruteForce(Test):
    usernames = None
    passwords = None

    def __init__(self, name):
        self.cancel = False
        with open(r"dictionaries\usernames.txt", "r") as usernames:
            self.usernames = [*usernames]
        with open(r"dictionaries\passwords.txt", "r") as passwords:
            self.passwords = [*passwords]
        self.results = ""
        self.name = name
        self.future = None

    def run(self, url: str, pdf: PdfGen):
        self.cancel = False
        pdf.addP(f"url: {url}")
        print("A")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self.future = executor.submit(self.bruteCracking, url)
        self.future = None

    def bruteCracking(self, url):
        print("B")
        count = 0
        user_count = 0
        pass_len = len(self.passwords)
        user_len = len(self.usernames)
        for username in self.usernames:
            user_count = user_count + 1
            for password in self.passwords:
                if self.cancel:
                    return
                password = password.strip()
                count = count + 1
                print(f'''Trying user ({user_count}/{user_len}): {username}\nTrying password ({count}/{pass_len}): {password}''')
                data_dict = {"email": username, "password": password}
                try:
                    response = requests.post(url, data=data_dict)
                except Exception as e:
                    print(e)
                    continue
                except:
                    print("Some Error Occurred Please Check Your Internet Connection !!")
                    continue
                if "Wrong password" in str(response.content):
                    continue
                elif "csrf" in str(response.content).lower():
                    print("CSRF Token Detected!! BruteF0rce Not Working This Website.")
                    exit()
                elif response.status_code != 200:
                    print("Username: ---> " + username)
                    print("Password: ---> " + password)
                    print("Wrong")
                else:
                    print("Username: ---> " + username)
                    print("Password: ---> " + password)
                    print("CORRECT")
                    print("This Site is vulnerable against the BruteForce attack!")
                    break

