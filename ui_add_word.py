# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_word.ui'
##
## Created by: Qt User Interface Compiler version 6.6.3
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFormLayout, QLabel, QLineEdit, QSizePolicy,
    QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(382, 81)
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(290, 20, 81, 241))
        self.buttonBox.setOrientation(Qt.Vertical)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close|QDialogButtonBox.Save)
        self.formLayoutWidget = QWidget(Dialog)
        self.formLayoutWidget.setObjectName(u"formLayoutWidget")
        self.formLayoutWidget.setGeometry(QRect(10, 20, 271, 52))
        self.formLayout = QFormLayout(self.formLayoutWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.formLayoutWidget)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.word1 = QLineEdit(self.formLayoutWidget)
        self.word1.setObjectName(u"word1")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.word1)

        self.label_2 = QLabel(self.formLayoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.word2 = QLineEdit(self.formLayoutWidget)
        self.word2.setObjectName(u"word2")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.word2)


        self.retranslateUi(Dialog)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"\u0421\u043b\u043e\u0432\u043e \u0438\u043b\u0438 \u0444\u0440\u0430\u0437\u0430", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"\u041f\u0435\u0440\u0435\u0432\u043e\u0434", None))
    # retranslateUi

