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
    for i in range(0, 60):
        tests.append(Test.Test(i))

    #########################################

    # running tests
    for test in tests:
        app.addTest(test)

    # Show window
    app.run()
# End of main
