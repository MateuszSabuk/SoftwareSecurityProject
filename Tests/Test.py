import time


class Test:
    def __init__(self, num=None):
        self.results = []
        self.name = f"Test"
        if num is not None:
            self.name = f"Test {num}"
        self.cancel = False

    def run(self, url: str):
        print(f"This is run of an example test with url: {url}")
        result = f'''This is run of an example test with url {url}\n''' \
                 '''Was a success'''
        self.results.append((time.time(), result))
