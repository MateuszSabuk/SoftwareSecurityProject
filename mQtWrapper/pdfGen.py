from fpdf import FPDF
from datetime import datetime


class PdfGen:
    def __init__(self):
        self.font = "Arial"
        self.headerCounter = 1
        self.pdf = FPDF('P', 'mm', 'A4')
        self.pdf.set_margins(25.2, 25.2, 25.2)
        self.pdf.add_page()
        self.pdf.set_font(self.font, size=26)
        self.pdf.cell(200, 10, txt="Scan report", ln=1, align='L')
        self.pdf.set_font(self.font, size=16)
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        self.pdf.cell(200, 10, txt=dt_string, ln=1, align="L")

    '''Adds a paragraph to the '''
    def addP(self, txt: str):
        self.pdf.set_font(self.font, size=12)
        self.pdf.multi_cell(0, 6, txt=txt, align="L")

    def addH(self, txt: str, number=None, numbered=True):
        if numbered:
            if number is None:
                number = self.headerCounter
                self.headerCounter = number + 1
            txt = str(number) + '. ' + txt

        self.pdf.set_font(self.font, size=22)
        self.pdf.cell(200, 10, txt=txt, ln=1, align='L')

    def generate(self):
        self.pdf.output("Report.pdf")
