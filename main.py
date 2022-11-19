from mQtWrapper.mGuiWrapper import MGuiWrapper

from Tests import ExampleTest


# Application beginning
if __name__ == '__main__':
    # Gui initialization
    app = MGuiWrapper()

    # Add the tests here ####################

    app.addTest("Name", ExampleTest.main)

    #########################################

    # Show window
    app.run()
# End of main
