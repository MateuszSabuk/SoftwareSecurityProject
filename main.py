from mQtWrapper.mGuiWrapper import MGuiWrapper

# Import your tests here
from Tests import Test


# Application beginning
if __name__ == '__main__':
    # Gui initialization
    app = MGuiWrapper()

    tests = []
    # Add the tests here ####################

    tests.append(Test.Test("Example test name"))

    #########################################

    # running tests
    for test in tests:
        app.addTest(test.name, test.run)

    # Show window
    app.run()
# End of main
