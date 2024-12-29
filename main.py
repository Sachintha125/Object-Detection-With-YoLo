from GUIs.guis import *
from PyQt5.QtWidgets import QApplication
import sys

def main():
    app = QApplication(sys.argv)
    home_window = Home()
    home_window.show()
    app.exec_()

if __name__ == '__main__':
    main()
