import concurrent.futures
import datetime
import re
import sys
import time
from concurrent.futures import Future
from threading import Thread
from urllib.parse import urlparse

from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QPlainTextEdit, QGroupBox, QCheckBox, \
    QSplitter, QScrollArea, QMessageBox, QTableWidget, QHeaderView, QTableWidgetItem, QTextEdit, QLabel
from PyQt5.QtCore import Qt, pyqtSignal

from mUtilities.DataBaseHandler import DataBaseHandler
from mUtilities.WebCrawler import WebCrawler


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


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
        self.vbox.setAlignment(Qt.AlignTop)
        self.vbox.setSpacing(5)
        self.vbox.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.vbox)


class _ActionButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent


class _StartScanButton(_ActionButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.clicked.connect(parent.startScan)
        self.setText("Start test")


class _UrlTable(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["URL", "Start Time", "End Time", "Elapsed Time", "Status", "Reason"])
        self.table.setColumnWidth(0, 350)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 100)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

    def add_url_to_table(self, url_dict):
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        self.table.setItem(row_count, 0, QTableWidgetItem(url_dict["url"]))
        self.table.setItem(row_count, 1, QTableWidgetItem(str(datetime.datetime.fromtimestamp(int(url_dict["start_time"])))))
        self.table.setItem(row_count, 2, QTableWidgetItem(str(datetime.datetime.fromtimestamp(int(url_dict["end_time"])))))
        self.table.setItem(row_count, 3, QTableWidgetItem(str(url_dict["elapsed"])))
        self.table.setItem(row_count, 4, QTableWidgetItem(str(url_dict["status"])))
        self.table.setItem(row_count, 5, QTableWidgetItem(url_dict["reason"]))
        self.table.scrollToBottom()

    def clear_table(self):
        for i in range(self.table.rowCount(), -1, -1):
            self.table.removeRow(i)


class _ConsoleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.NoWrap)

        sys.stdout = self
        title = QLabel()
        title.setText("Output")

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.text_edit)

        self.setLayout(layout)

    def write(self, text):
        if text in ["\n", ""]:
            return
        time.sleep(0.01)    # so the display doesn't brake
        self.text_edit.append(text)
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.text_edit.setTextCursor(cursor)

    def __del__(self):
        sys.stdout = sys.__stdout__


class _AdditionalAddresses(QWidget):
    def __init__(self):
        super().__init__()
        self.text_edit = QTextEdit()
        title = QLabel()
        title.setText("Additional paths")

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.text_edit)

        self.setLayout(layout)


# Main
class MMainWindow(QMainWindow):
    add_log_signal = pyqtSignal(dict)
    dbh = DataBaseHandler()

    def __init__(self, parent=None):
        super().__init__()
        self.cancel = False
        self.run_future = None
        self.web_crawler = None
        self.tests_to_run = []

        self.add_log_signal.connect(self.add_log)

        self.central = QWidget()
        self.setWindowTitle("Scanner project")
        self.setWindowIcon(QIcon('mQtWrapper\\windowIcon.png'))
        self.wrapper = parent
        self.vbox = QVBoxLayout(self.central)

        window_splitter = QSplitter(Qt.Vertical)
        self.vbox.addWidget(window_splitter)

        top_section = QSplitter(Qt.Horizontal)
        window_splitter.addWidget(top_section)

        self.bottom_section = QSplitter(Qt.Horizontal)
        self.url_table = _UrlTable()
        self.bottom_section.addWidget(self.url_table)
        self.console = _ConsoleWidget()
        self.bottom_section.addWidget(self.console)
        window_splitter.addWidget(self.bottom_section)

        self.console.show()


        # Create the top-left section and add it to the top section
        top_left_section = QWidget()
        top_left_section.setLayout(QVBoxLayout(self.central))
        top_section.addWidget(top_left_section)

        # Create the top-right section and add it to the top section
        top_middle_section = QWidget()
        top_middle_section.setLayout(QVBoxLayout(self.central))
        top_right_section = _AdditionalAddresses()
        top_right_section.setLayout(QVBoxLayout(self.central))
        top_section.addWidget(top_middle_section)
        top_section.addWidget(top_right_section)
        top_middle_section.layout().addWidget(_URLInput(self))
        self.scan_button = _StartScanButton(self)
        top_middle_section.layout().addWidget(self.scan_button)
        self.stop_button = _ActionButton(self)
        self.stop_button.setText("Stop test")
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        top_middle_section.layout().addWidget(self.stop_button)
        self.crawl_first_check_box = QCheckBox("Crawl first")
        self.crawl_first_check_box.setChecked(True)
        top_middle_section.layout().addWidget(self.crawl_first_check_box)
        self.run_from_db_check_box = QCheckBox("Run from existing db")
        self.run_from_db_check_box.setChecked(False)
        self.run_from_db_check_box.setEnabled(False)
        top_middle_section.layout().addWidget(self.run_from_db_check_box)

        # Adding widgets

        self.testGroupBox = _TestGroupBox(self)
        # self.testGroupBox.setTitle("Available tests")

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.testGroupBox)
        scroll_area.setWidgetResizable(True)

        top_left_section.layout().addWidget(QLabel("Tests"))
        top_left_section.layout().addWidget(scroll_area)

        # Setting window parameters
        self.vbox.setAlignment(Qt.AlignTop)
        self.vbox.setSpacing(10)
        self.vbox.setContentsMargins(10, 10, 10, 10)

        self.press_control = 0

        self.setCentralWidget(self.central)

        top_section.setSizes([250, 400, 350])
        self.bottom_section.setSizes([600, 400])
        window_splitter.setSizes([300, 200])

        # Get style from css
        with open(r'mQtWrapper\mainWindow.css', 'r') as style:
            self.setStyleSheet(style.read())

        # Logic functions
        self.tests = []

    def closeEvent(self, event):
        result = QMessageBox.question(self, "Confirm Exit...", "Are you sure you want to exit ?",
                                      QMessageBox.Yes | QMessageBox.No)
        event.ignore()

        if result == QMessageBox.Yes:
            sys.stdout = sys.__stdout__
            self.stop_scan()
            event.accept()

    def addTest(self, name, function):
        test = QCheckBox(name)
        test.setObjectName(str(len(self.tests)))
        self.tests.append({"id": test.objectName(), "name": name, "function": function})
        self.testGroupBox.vbox.addWidget(test)
        self.update()

    def startScan(self):
        url = self.findChild(_URLInput).toPlainText()
        if not is_valid_url(url):
            if not is_valid_url(f"http://{url}"):
                # TODO tell user its not a good url
                return
            url = f"http://{url}"
            self.findChild(_URLInput).setPlainText(url)

        pdf = self.wrapper.pdf

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
            self.url_table.clear_table()
            self.crawl_first_check_box.setChecked(False)
            self.run_from_db_check_box.setChecked(True)
            self.run_from_db_check_box.setEnabled(True)
            self.web_crawler = WebCrawler(self)
            self.web_crawler.run_crawl(url)
            self.dbh.run_tests_for_links(self.run_tests)

        elif self.run_from_db_check_box.isChecked():
            self.dbh.run_tests_for_links(self.run_tests)
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

    def add_log(self, url_dict):
        self.url_table.add_url_to_table(url_dict)

    def stop_scan(self):
        if self.web_crawler is None:
            return

        self.web_crawler.cancel = True
        self.cancel = True

        self.stop_button.setEnabled(False)
        self.scan_button.setEnabled(True)

# End of MMainWindow class
