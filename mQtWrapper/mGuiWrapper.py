from PyQt5.QtWidgets import QApplication
from mQtWrapper import mMainWindow
from mQtWrapper.pdfGen import PdfGen


class MGuiWrapper:
    def __init__(self):
        self.app = QApplication([])
        self.window = mMainWindow.MMainWindow(self)
        self.pdf = PdfGen()

    def run(self):
        self.window.showMaximized()
        self.app.exec()

    def addTest(self, name: str, function):
        """Adds a checkbox to the gui\n
        Name is the text displayed next to the checkbox\n
        Function is the reference to the test starting function\n
        ! Function has to have an url (string) argument"""
        self.window.addTest(name, function)
