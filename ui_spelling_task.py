# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'spelling_task.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
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
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(480, 196)
        self.word_to_translate = QLabel(Dialog)
        self.word_to_translate.setObjectName(u"word_to_translate")
        self.word_to_translate.setGeometry(QRect(10, 10, 461, 31))
        font = QFont()
        font.setPointSize(16)
        self.word_to_translate.setFont(font)
        self.answer_field = QLineEdit(Dialog)
        self.answer_field.setObjectName(u"answer_field")
        self.answer_field.setGeometry(QRect(10, 50, 461, 41))
        self.answer_field.setFont(font)
        self.check_answer_button = QPushButton(Dialog)
        self.check_answer_button.setObjectName(u"check_answer_button")
        self.check_answer_button.setGeometry(QRect(10, 140, 221, 51))
        self.check_answer_button.setFont(font)
        self.answer = QLabel(Dialog)
        self.answer.setObjectName(u"answer")
        self.answer.setGeometry(QRect(10, 100, 461, 31))
        self.answer.setFont(font)
        self.continue_button = QPushButton(Dialog)
        self.continue_button.setObjectName(u"continue_button")
        self.continue_button.setGeometry(QRect(250, 140, 221, 51))
        self.continue_button.setFont(font)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.word_to_translate.setText(QCoreApplication.translate("Dialog", u"TextLabel", None))
        self.check_answer_button.setText(QCoreApplication.translate("Dialog", u"\u041f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c", None))
        self.answer.setText(QCoreApplication.translate("Dialog", u"TextLabel", None))
        self.continue_button.setText(QCoreApplication.translate("Dialog", u"\u041f\u0440\u043e\u0434\u043e\u043b\u0436\u0438\u0442\u044c", None))
    # retranslateUi

