from mQtWrapper.pdfGen import PdfGen


class Test:
    def __init__(self, name):
        self.results = ""
        self.name = name
        self.cancel = False

    def run(self, url: str, pdf: PdfGen):
        print(f"This is run of an example test with url: {url}")
        pdf.addP(f"url: {url}")
