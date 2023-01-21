from mQtWrapper.mGuiWrapper import MGuiWrapper

# Import your tests here
from Tests import Test
from mUtilities.WebCrawler import WebCrawler

# Application beginning
if __name__ == '__main__':
    # Gui initialization
    app = MGuiWrapper()

    tests = []
    # Add the tests here ####################

    for i in range(0, 60):
        tests.append(Test.Test(f"Example test name {i}"))

    #########################################

    # running tests
    for test in tests:
        app.addTest(test.name, test.run)

    # Show window
    app.run()
# End of main
