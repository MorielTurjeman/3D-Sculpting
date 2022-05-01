# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets, QtOpenGL
from gluttut import OpenGLEngine


class Ui_MainWindow(QtWidgets.QMainWindow):
    def setupUi(self, MainWindow: QtWidgets.QMainWindow):
        super(Ui_MainWindow, self).__init__(MainWindow)
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        glformat = QtOpenGL.QGLFormat()
        glformat.setVersion(3, 3)
        glformat.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        glformat.setSampleBuffers(True)

        # glformat.setProfile(QtOpenGL.QGLFormat.C)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(30, 60, 113, 32))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(30, 120, 113, 32))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(30, 170, 113, 32))
        self.pushButton_3.setObjectName("pushButton_3")
        self.openGLWidget = GlutTutWidget(glformat, parent=self.centralWidget)
        # self.openGLWidget.setGeometry(QtCore.QRect(189, 59, 511, 351))
        # self.openGLWidget.setObjectName("openGLWidget")
        MainWindow.setCentralWidget(self.openGLWidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 24))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        # self.openGLWidget.setParent(self.centralWidget())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Rotate"))
        self.pushButton_2.setText(_translate("MainWindow", "Scale"))
        self.pushButton_3.setText(_translate("MainWindow", "Move"))


class GlutTutWidget(QtOpenGL.QGLWidget):

    visible = False

    def __init__(self, format=None, parent=None):
        super(GlutTutWidget, self).__init__(format)
        self.setMinimumSize(800, 800)
        self.openGlEngine = None

    def initializeGL(self) -> None:
        self.openGlEngine = OpenGLEngine()

    def showEvent(self, a0) -> None:
        self.visible = True

    def paintGL(self) -> None:
        if self.visible:
            size = self.size()
            self.openGlEngine.framebuffer.update_dimensions(size.width(),
                                                            size.height())
            self.openGlEngine.render_scene()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
