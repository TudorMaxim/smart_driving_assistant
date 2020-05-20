import sys
from PyQt5.QtWidgets import QApplication
from gui.MainWidget import MainWidget


def main():
    app = QApplication(sys.argv)
    main_window = MainWidget()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
