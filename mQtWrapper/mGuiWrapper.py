from PyQt5.QtWidgets import QApplication
from mQtWrapper import mMainWindow


class MGuiWrapper:
    def __init__(self):
        self.app = QApplication([])
        self.window = mMainWindow.MMainWindow()

    def run(self):
        self.window.show()
        self.app.exec()

    def addTest(self, name: str, function):
        """Adds a checkbox to the gui\n
        Name is the text displayed next to the checkbox\n
        Function is the reference to the test starting function\n
        ! Function has to have an url (string) argument"""
        self.window.addTest(name, function)
