# -*- coding: utf-8 -*-

"""
Module implementing Form.
"""
from PyQt5 import QtCore, QtGui, QtWidgets

import test


class Form(QtWidgets.QWidget, test.Ui_Form):
    """
    Class documentation goes here.
    """

    def __init__(self, parent=None):
        """
        Constructor
        """
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.opa = 1.0
        self.timer1 = QtCore.QTimer()
        self.timer2 = QtCore.QTimer()

        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL("clicked()"), self.start_timer1)
        QtCore.QObject.connect(self.timer1, QtCore.SIGNAL("timeout()"), self.fade_out)
        QtCore.QObject.connect(self.pushButton_2, QtCore.SIGNAL("clicked()"), self.start_timer2)
        QtCore.QObject.connect(self.timer2, QtCore.SIGNAL("timeout()"), self.fade_in)


    def start_timer1(self):
        self.timer1.start(50)

    def start_timer2(self):
        self.timer2.start(50)

    def fade_out(self):
        self.opa += -0.1
        self.setWindowOpacity(self.opa)
        if self.opa <= 0.2:
            self.timer1.stop()
            # self.close()

    def fade_in(self):
        self.opa += 0.1
        self.setWindowOpacity(self.opa)
        if self.opa >= 1.0:
            self.timer2.stop()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    dlg = Form()
    dlg.show()
    sys.exit(app.exec_())

