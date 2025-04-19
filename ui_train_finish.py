# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'train_finish.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFormLayout, QLabel,
    QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(251, 121)
        self.formLayoutWidget = QWidget(Dialog)
        self.formLayoutWidget.setObjectName(u"formLayoutWidget")
        self.formLayoutWidget.setGeometry(QRect(10, 10, 231, 106))
        self.formLayout = QFormLayout(self.formLayoutWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.formLayoutWidget)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.correct_words_count = QLabel(self.formLayoutWidget)
        self.correct_words_count.setObjectName(u"correct_words_count")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.correct_words_count)

        self.label_2 = QLabel(self.formLayoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.errors_count = QLabel(self.formLayoutWidget)
        self.errors_count.setObjectName(u"errors_count")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.errors_count)

        self.label_3 = QLabel(self.formLayoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.correctness_percentage = QLabel(self.formLayoutWidget)
        self.correctness_percentage.setObjectName(u"correctness_percentage")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.correctness_percentage)

        self.label_4 = QLabel(self.formLayoutWidget)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_4)

        self.train_time = QLabel(self.formLayoutWidget)
        self.train_time.setObjectName(u"train_time")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.train_time)

        self.label_5 = QLabel(self.formLayoutWidget)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_5)

        self.learned_count = QLabel(self.formLayoutWidget)
        self.learned_count.setObjectName(u"learned_count")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.learned_count)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0432\u0435\u0440\u043d\u044b\u0445 \u043e\u0442\u0432\u0435\u0442\u043e\u0432", None))
        self.correct_words_count.setText("")
        self.label_2.setText(QCoreApplication.translate("Dialog", u"\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043e\u0448\u0438\u0431\u043e\u043a", None))
        self.errors_count.setText("")
        self.label_3.setText(QCoreApplication.translate("Dialog", u"\u041f\u0440\u043e\u0446\u0435\u043d\u0442 \u0432\u0435\u0440\u043d\u044b\u0445 \u043e\u0442\u0432\u0435\u0442\u043e\u0432", None))
        self.correctness_percentage.setText("")
        self.label_4.setText(QCoreApplication.translate("Dialog", u"\u0412\u0440\u0435\u043c\u044f \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f", None))
        self.train_time.setText("")
        self.label_5.setText(QCoreApplication.translate("Dialog", u"\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u0435 \u0432\u044b\u0443\u0447\u0435\u043d\u043d\u044b\u0445 \u0441\u043b\u043e\u0432", None))
        self.learned_count.setText("")
    # retranslateUi

