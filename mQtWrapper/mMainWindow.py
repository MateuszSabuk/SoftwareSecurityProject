from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QPlainTextEdit, QGroupBox, QCheckBox
from PyQt5.QtCore import Qt

# class _TopBarButton(QPushButton):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.parent = parent
#         self.setGeometry()


# class _TopBar(QLabel):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.parent = parent
#
#     def mousePressEvent(self, e):
#         if e.button() == Qt.LeftButton:
#             if self.parent.press_control == 0:
#                 self.pos = e.pos()
#                 self.main_pos = self.parent.pos()
#         super().mousePressEvent(e)
#
#     def mouseMoveEvent(self, e):
#         if self.parent.cursor().shape() == Qt.ArrowCursor:
#             self.last_pos = e.pos() - self.pos
#             self.main_pos += self.last_pos
#             self.parent.move(self.main_pos)
#         super(_TopBar, self).mouseMoveEvent(e)

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
    def __init__(self):
        super().__init__()
        self.central = QWidget()
        self.setWindowTitle("Scanner project")
        self.setWindowIcon(QIcon('mQtWrapper\\windowIcon.png'))

        self.vbox = QVBoxLayout(self.central)

        # # If I want to add my own top bar
        # self.setWindowFlags(Qt.FramelessWindowHint)
        # topBar = _TopBar(self)
        # topBar.setStyleSheet(style)
        # self.vbox.addWidget(topBar)

        # Adding widgets
        self.vbox.addWidget(_URLInput(self))

        self.testGroupBox = _TestGroupBox(self)

        self.testGroupBox.vbox.setAlignment(Qt.AlignTop)
        self.testGroupBox.vbox.setSpacing(5)
        self.testGroupBox.vbox.setContentsMargins(10, 10, 10, 10)
        # self.testGroupBox.setTitle("Available tests")
        self.vbox.addWidget(self.testGroupBox)

        self.vbox.addWidget(_StartScanButton(self))

        # Setting window parameters
        self.vbox.setAlignment(Qt.AlignTop)
        self.vbox.setSpacing(10)
        self.vbox.setContentsMargins(10, 10, 10, 10)

        self.press_control = 0

        self.setCentralWidget(self.central)
        self.resize(800, 500)

        # Get style from css
        with open('mQtWrapper\\mainWindow.css', 'r') as style:
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
        url = self.findChild(_URLInput).toPlainText()

        # TODO MATEUSZ: validate url here

        functionsToRun = []
        for checkbox in self.findChildren(QCheckBox):
            if checkbox.isChecked():
                for test in self.tests:
                    if test["id"] == checkbox.objectName():
                        functionsToRun.append(test["function"])
        for fun in functionsToRun:
            print(end="" "Test: ")
            print("Test return:", fun(url))

# End of MMainWindow class
