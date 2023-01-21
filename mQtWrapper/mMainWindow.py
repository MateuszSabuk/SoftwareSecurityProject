import concurrent.futures
from concurrent.futures import Future
from threading import Thread

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QPlainTextEdit, QGroupBox, QCheckBox, \
    QSplitter, QScrollArea
from PyQt5.QtCore import Qt

from mUtilities.DataBaseHandler import DataBaseHandler
from mUtilities.WebCrawler import WebCrawler


class _URLInput(QPlainTextEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setPlaceholderText("URL to scan")


class _TestGroupBox(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)


class _StartScanButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.clicked.connect(parent.startScan)
        self.setText("Start test")


# Main
class MMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.cancel = False
        self.run_future = None
        self.web_crawler = None
        self.tests_to_run = []

        self.windowClosed.connect(self.stop_scan())

        self.central = QWidget()
        self.setWindowTitle("Scanner project")
        self.setWindowIcon(QIcon('mQtWrapper\\windowIcon.png'))
        self.wrapper = parent
        self.vbox = QVBoxLayout(self.central)

        window_splitter = QSplitter(Qt.Vertical)
        self.vbox.addWidget(window_splitter)

        top_section = QSplitter(Qt.Horizontal)
        window_splitter.addWidget(top_section)

        bottom_section = QWidget()
        window_splitter.addWidget(bottom_section)

        # Create the top-left section and add it to the top section
        top_left_section = QWidget()
        top_left_section.setLayout(QVBoxLayout(self.central))
        top_section.addWidget(top_left_section)

        # Create the top-right section and add it to the top section
        top_right_section = QWidget()
        top_right_section.setLayout(QVBoxLayout(self.central))
        top_section.addWidget(top_right_section)
        top_right_section.layout().addWidget(_URLInput(self))
        self.scan_button = _StartScanButton(self)
        top_right_section.layout().addWidget(self.scan_button)
        self.stop_button = QPushButton(self)
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        top_right_section.layout().addWidget(self.stop_button)
        self.crawl_first_check_box = QCheckBox("Crawl first")
        self.crawl_first_check_box.setChecked(True)
        top_right_section.layout().addWidget(self.crawl_first_check_box)

        # Adding widgets

        self.testGroupBox = _TestGroupBox(self)
        self.testGroupBox.vbox.setAlignment(Qt.AlignTop)
        self.testGroupBox.vbox.setSpacing(5)
        self.testGroupBox.vbox.setContentsMargins(10, 10, 10, 10)
        # self.testGroupBox.setTitle("Available tests")

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.testGroupBox)
        scroll_area.setWidgetResizable(True)

        top_left_section.layout().addWidget(scroll_area)


        # Setting window parameters
        self.vbox.setAlignment(Qt.AlignTop)
        self.vbox.setSpacing(10)
        self.vbox.setContentsMargins(10, 10, 10, 10)

        self.press_control = 0

        self.setCentralWidget(self.central)

        window_splitter.setSizes([300, 200])

        # Get style from css
        with open(r'mQtWrapper\mainWindow.css', 'r') as style:
            self.setStyleSheet(style.read())

        # Logic functions
        self.tests = []


    def addTest(self, name, function):
        test = QCheckBox(name)
        test.setObjectName(str(len(self.tests)))
        self.tests.append({"id": test.objectName(), "name": name, "function": function})
        self.testGroupBox.vbox.addWidget(test)
        self.update()

    def startScan(self):
        pdf = self.wrapper.pdf

        url = self.findChild(_URLInput).toPlainText()

        # TODO MATEUSZ: validate url here

        self.tests_to_run = []
        for checkbox in self.findChildren(QCheckBox):
            if checkbox.isChecked():
                for test in self.tests:
                    if test["id"] == checkbox.objectName():
                        self.tests_to_run.append(test)
        pdf.addP(f"Checked url: {url}")
        pdf.addH("Tests to be done:")
        pdf.pdf.add_page()

        Thread(target=self.start_run_thread, args=(url,)).start()

    def start_run_thread(self, url):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self.run_future = executor.submit(self.run_thread, url)

    def run_thread(self, url):
        self.scan_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        if self.crawl_first_check_box.isChecked():
            self.web_crawler = WebCrawler()
            self.web_crawler.run_crawl(url)
            dbh = DataBaseHandler()
            dbh.run_tests_for_links(self.run_tests)
        else:
            self.run_tests(url)
        self.stop_button.setEnabled(False)
        self.scan_button.setEnabled(True)
        self.cancel = False

    def run_tests(self, url):
        pdf = self.wrapper.pdf
        for test in self.tests_to_run:
            if not self.cancel:
                index = str(self.tests_to_run.index(test) + 1)
                print(f"Running test {index}/{len(self.tests_to_run)}: \"{test['name']}\"")
                try:
                    pdf.addH(test["name"])
                    test["function"](url, pdf)
                    pdf.generate()
                except:
                    print(f"Test {index} failed - something went wrong")

    def stop_scan(self):
        if self.web_crawler.future is not None:
            self.web_crawler.future.cancel()
            self.web_crawler.cancel = True
        if self.run_future is not None:
            self.run_future.cancel()
            self.cancel = True
        print(self.run_future is None, self.web_crawler.future is None)
        if self.run_future is None and self.web_crawler.future is None:
            self.stop_button.setEnabled(False)
            self.scan_button.setEnabled(True)


# End of MMainWindow class
