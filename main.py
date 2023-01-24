from Tests.CSRF import CSRF
from Tests.DOM_XSS import DOM_XSS
from Tests.Dom_XXS_new import DOM_XSS_DVWS
from Tests.HTTP_Flood import HTTP_Flood
from Tests.Reflected_XSS import Reflected_XSS
from Tests.Reflected_XXS_new import Reflected_XSS_DVWS
from Tests.SQLI import SQLI
from Tests.Stored_XSS import Stored_XSS
from Tests.Stored_XXS_new import Stored_XSS_DVWS
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

    # dx = DOM_XSS()
    # tests.append(dx)

    dx_dvws = DOM_XSS_DVWS()
    tests.append(dx_dvws)

    # rx = Reflected_XSS()
    # tests.append(rx)

    rx_dvws = Reflected_XSS_DVWS()
    tests.append(rx_dvws)

    # sx = Stored_XSS()
    # tests.append(sx)

    sx_dvws = Stored_XSS_DVWS()
    tests.append(sx_dvws)

    #########################################

    # running tests
    for test in tests:
        app.addTest(test)

    # Show window
    app.run()
# End of main
