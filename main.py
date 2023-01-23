from Tests.CSRF import CSRF
from Tests.DOM_XSS import DOM_XSS
from Tests.HTTP_Flood import HTTP_Flood
from Tests.Reflected_XSS import Reflected_XSS
from Tests.SQLI import SQLI
from Tests.Stored_XSS import Stored_XSS
from mQtWrapper.mGuiWrapper import MGuiWrapper

# Import your tests here
from Tests import Test, BruteForce
from mUtilities.WebCrawler import WebCrawler

# Application beginning
if __name__ == '__main__':
    # Gui initialization
    app = MGuiWrapper()

    tests = []
    # Add the tests here ####################

    bf = BruteForce.BruteForce()
    tests.append(bf)

    csrf = CSRF()
    tests.append(csrf)

    http_flood = HTTP_Flood()
    tests.append(http_flood)

    sqli = SQLI()
    tests.append(sqli)

    dx = DOM_XSS()
    tests.append(dx)

    rx = Reflected_XSS()
    tests.append(rx)

    sx = Stored_XSS()
    tests.append(sx)

    #########################################

    # running tests
    for test in tests:
        app.addTest(test)

    # Show window
    app.run()
# End of main
