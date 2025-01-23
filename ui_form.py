# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QGroupBox, QHBoxLayout,
    QLabel, QMainWindow, QMenuBar, QProgressBar,
    QPushButton, QSizePolicy, QStatusBar, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.folders_group = QGroupBox(self.centralwidget)
        self.folders_group.setObjectName(u"folders_group")
        self.folders_layout = QVBoxLayout(self.folders_group)
        self.folders_layout.setObjectName(u"folders_layout")
        self.input_layout = QHBoxLayout()
        self.input_layout.setObjectName(u"input_layout")
        self.input_folder_label = QLabel(self.folders_group)
        self.input_folder_label.setObjectName(u"input_folder_label")

        self.input_layout.addWidget(self.input_folder_label)

        self.input_folder_button = QPushButton(self.folders_group)
        self.input_folder_button.setObjectName(u"input_folder_button")

        self.input_layout.addWidget(self.input_folder_button)


        self.folders_layout.addLayout(self.input_layout)

        self.output_layout = QHBoxLayout()
        self.output_layout.setObjectName(u"output_layout")
        self.output_folder_label = QLabel(self.folders_group)
        self.output_folder_label.setObjectName(u"output_folder_label")

        self.output_layout.addWidget(self.output_folder_label)

        self.output_folder_button = QPushButton(self.folders_group)
        self.output_folder_button.setObjectName(u"output_folder_button")

        self.output_layout.addWidget(self.output_folder_button)


        self.folders_layout.addLayout(self.output_layout)

        # Add Launch LabelImg button to folders group
        self.launch_labelimg_button = QPushButton(self.folders_group)
        self.launch_labelimg_button.setObjectName(u"launch_labelimg_button")
        self.folders_layout.addWidget(self.launch_labelimg_button)

        self.verticalLayout.addWidget(self.folders_group)

        self.augmentation_group = QGroupBox(self.centralwidget)
        self.augmentation_group.setObjectName(u"augmentation_group")
        self.augmentation_layout = QVBoxLayout(self.augmentation_group)
        self.augmentation_layout.setObjectName(u"augmentation_layout")
        self.flip_horizontal = QCheckBox(self.augmentation_group)
        self.flip_horizontal.setObjectName(u"flip_horizontal")

        self.augmentation_layout.addWidget(self.flip_horizontal)

        self.flip_vertical = QCheckBox(self.augmentation_group)
        self.flip_vertical.setObjectName(u"flip_vertical")

        self.augmentation_layout.addWidget(self.flip_vertical)

        self.rotate = QCheckBox(self.augmentation_group)
        self.rotate.setObjectName(u"rotate")

        self.augmentation_layout.addWidget(self.rotate)

        self.brightness_check = QCheckBox(self.augmentation_group)
        self.brightness_check.setObjectName(u"brightness_check")

        self.augmentation_layout.addWidget(self.brightness_check)

        self.contrast_check = QCheckBox(self.augmentation_group)
        self.contrast_check.setObjectName(u"contrast_check")

        self.augmentation_layout.addWidget(self.contrast_check)

        self.augmentation_info = QLabel(self.augmentation_group)
        self.augmentation_info.setObjectName(u"augmentation_info")
        self.augmentation_info.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.augmentation_info.setWordWrap(True)

        self.augmentation_layout.addWidget(self.augmentation_info)

        self.verticalLayout.addWidget(self.augmentation_group)

        self.apply_button = QPushButton(self.centralwidget)
        self.apply_button.setObjectName(u"apply_button")

        self.verticalLayout.addWidget(self.apply_button)

        self.progress_bar = QProgressBar(self.centralwidget)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setValue(0)

        self.verticalLayout.addWidget(self.progress_bar)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 24))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"AugmentX", None))
        self.folders_group.setTitle(QCoreApplication.translate("MainWindow", u"Select Folders", None))
        self.input_folder_label.setText(QCoreApplication.translate("MainWindow", u"Input folder: not selected", None))
        self.input_folder_button.setText(QCoreApplication.translate("MainWindow", u"Select Input Folder", None))
        self.output_folder_label.setText(QCoreApplication.translate("MainWindow", u"Output folder: not selected", None))
        self.output_folder_button.setText(QCoreApplication.translate("MainWindow", u"Select Output Folder", None))
        self.launch_labelimg_button.setText(QCoreApplication.translate("MainWindow", u"Launch LabelImg", None))
        self.augmentation_group.setTitle(QCoreApplication.translate("MainWindow", u"Augmentation Settings", None))
        self.flip_horizontal.setText(QCoreApplication.translate("MainWindow", u"Horizontal Flip", None))
        self.flip_vertical.setText(QCoreApplication.translate("MainWindow", u"Vertical Flip", None))
        self.rotate.setText(QCoreApplication.translate("MainWindow", u"Rotation", None))
        self.brightness_check.setText(QCoreApplication.translate("MainWindow", u"Brightness Change", None))
        self.contrast_check.setText(QCoreApplication.translate("MainWindow", u"Contrast", None))
        self.augmentation_info.setText("")
        self.apply_button.setText(QCoreApplication.translate("MainWindow", u"Apply Augmentation", None))
    # retranslateUi
