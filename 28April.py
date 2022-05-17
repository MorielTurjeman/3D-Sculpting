# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '28April.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
from PyQt5 import QtCore, QtGui, QtWidgets, QtOpenGL
from gluttut import OpenGLEngine
from OpenGL.GL import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 1000)
        self.centralwidget = QtWidgets.QWidget(MainWindow) #
        self.centralwidget.setObjectName("centralwidget") #
        self.pushButton = QtWidgets.QPushButton(self.centralwidget) #
        self.pushButton.setGeometry(QtCore.QRect(420, 720, 113, 32)) #
        self.pushButton.setObjectName("pushButton") #
        self.horizontalSlider = QtWidgets.QSlider(self.centralwidget) #
        self.horizontalSlider.setGeometry(QtCore.QRect(290, 411, 411, 41)) #
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal) #
        self.horizontalSlider.setObjectName("horizontalSlider") #
        self.horizontalSlider.setMinimum(0)
        self.horizontalSlider.setMaximum(360)
        self.horizontalSlider.valueChanged.connect(self.x_rotation_event)
        self.horizontalSlider_2 = QtWidgets.QSlider(self.centralwidget) #
        self.horizontalSlider_2.setGeometry(QtCore.QRect(290, 460, 411, 41)) #
        self.horizontalSlider_2.setOrientation(QtCore.Qt.Horizontal) #
        self.horizontalSlider_2.setObjectName("horizontalSlider_2") #
        self.horizontalSlider_2.valueChanged.connect(self.y_rotation_event)
        self.horizontalSlider_2.setMaximum(360)
        self.horizontalSlider_2.setMinimum(0)
        self.label = QtWidgets.QLabel(self.centralwidget) #
        self.label.setGeometry(QtCore.QRect(189, 420, 81, 20)) #
        self.label.setObjectName("label") #
        self.label_2 = QtWidgets.QLabel(self.centralwidget) #
        self.label_2.setGeometry(QtCore.QRect(190, 470, 81, 20)) #
        self.label_2.setObjectName("label_2") #
        self.openGLWidget = GlutTutWidget(self.centralwidget)
        self.openGLWidget.setGeometry(QtCore.QRect(90, 20, 641, 391))
        self.openGLWidget.setObjectName("openGLWidget")
        self.horizontalSlider_3 = QtWidgets.QSlider(self.centralwidget) #
        self.horizontalSlider_3.setGeometry(QtCore.QRect(290, 510, 411, 41)) #
        self.horizontalSlider_3.setOrientation(QtCore.Qt.Horizontal) #
        self.horizontalSlider_3.setObjectName("horizontalSlider_3") #
        self.horizontalSlider_3.valueChanged.connect(self.z_rotation_event)
        self.horizontalSlider_3.setMaximum(360)
        self.horizontalSlider_3.setMinimum(0)
        self.label_3 = QtWidgets.QLabel(self.centralwidget) #
        self.label_3.setGeometry(QtCore.QRect(190, 520, 81, 20)) #
        self.label_3.setObjectName("label_3") #
        
        MainWindow.setCentralWidget(self.centralwidget) #
        
        self.menubar = QtWidgets.QMenuBar(MainWindow) #
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21)) #
        self.menubar.setObjectName("menubar") #
        MainWindow.setMenuBar(self.menubar) #
        self.statusbar = QtWidgets.QStatusBar(MainWindow) #
        self.statusbar.setObjectName("statusbar") #
        MainWindow.setStatusBar(self.statusbar) #

        self.retranslateUi(MainWindow) #
        QtCore.QMetaObject.connectSlotsByName(MainWindow) #

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate #
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow")) #
        self.pushButton.setText(_translate("MainWindow", "Zoom")) #
        self.label.setText(_translate("MainWindow", "X Rotation")) #
        self.label_2.setText(_translate("MainWindow", "Y Rotation")) #
        self.label_3.setText(_translate("MainWindow", "Z Rotation")) #

    def x_rotation_event(self):
        deg = self.horizontalSlider.value()
        self.openGLWidget.openGlEngine.rotate_yz(deg)
        self.openGLWidget.update()

    def y_rotation_event(self):
        deg = self.horizontalSlider_2.value()
        self.openGLWidget.openGlEngine.rotate_xz(deg)
        self.openGLWidget.update()
    
    def z_rotation_event(self):
        deg = self.horizontalSlider_3.value()
        self.openGLWidget.openGlEngine.rotate_xy(deg)
        self.openGLWidget.update()


class GlutTutWidget(QtOpenGL.QGLWidget):

    visible = False

    def __init__(self, parent=None):
        self.glformat = QtOpenGL.QGLFormat()
        self.glformat.setVersion(3, 3)
        self.glformat.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        self.glformat.setSampleBuffers(True)
        super(GlutTutWidget, self).__init__(self.glformat)
        self.setParent(parent)
        # self.setMinimumSize(400, 400)
        self.openGlEngine = None

    def initializeGL(self):
        print(self.format())
        self.openGlEngine = OpenGLEngine()
        # self.context().device().
        
    def showEvent(self, a0):
        self.visible = True

    def paintGL(self):
        size = self.size()
        self.openGlEngine.framebuffer.update_dimensions(size.width(),
                                                        size.height())
        self.openGlEngine.render_scene()


    def resizeGL(self, w: int, h: int):
        self.openGlEngine.framebuffer.update_dimensions(w,h)
        glViewport(0, 0, w, h);
        return super().resizeGL(w, h)

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())