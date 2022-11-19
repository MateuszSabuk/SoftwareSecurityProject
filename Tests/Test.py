# This is an example of a test

class Test:
    def __init__(self, name):
        self.results = ""
        self.name = name

    def run(self, url: str):
        print("This is run of an example test with url:", url)
        self.results = "Test outputs that will go to pdf not yet sure in what format"
