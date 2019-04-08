import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from SpaceXprotocol.ihm.test import Ui_Dialog
from SpaceXprotocol.ihm.IHMlogin import Login
import SpaceXprotocol.ihm.wid1 as wid1
import SpaceXprotocol.ihm.wid2 as wid2

# class AppWindow(QtWidgets.QDialog):
#
#     def __init__(self, parent=None):
#         super().__init__()
#         self.montrerLogin()
#         self.login = Login()
#         self.dialog = Ui_Dialog()
#         self.montrerLogin()
#
#
#
#     def montrerLogin(self):
#         self.dialog.setupUi(self)
#         self.dialog.pushButton.clicked.connect(self.montrerIHM)
#         self.show()
#
#     def montrerIHM(self):
#         print("PUTTTTAIN")
#         self.login.setupUi(self)
#         self.show()
#


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setGeometry(50, 50, 400, 450)
        self.setFixedSize(400, 450)
        self.montrer1()


    def montrer1(self):
        self.premier = wid1.Ui_Form()
        self.setCentralWidget(self.premier)
        self.premier.pushButton(self.montrer2)
        self.show()
    def montrer2(self):
        self.deuz = wid2.Ui_Form()
        self.setCentralWidget(self.deuz)
        self.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())