# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'net_settings.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFormLayout, QLabel, QLineEdit, QSizePolicy,
    QWidget)

class Ui_NetSettings(object):
    def setupUi(self, NetSettings):
        if not NetSettings.objectName():
            NetSettings.setObjectName(u"NetSettings")
        NetSettings.resize(400, 91)
        self.buttonBox = QDialogButtonBox(NetSettings)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(290, 20, 81, 241))
        self.buttonBox.setOrientation(Qt.Orientation.Vertical)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.formLayoutWidget = QWidget(NetSettings)
        self.formLayoutWidget.setObjectName(u"formLayoutWidget")
        self.formLayoutWidget.setGeometry(QRect(0, 10, 281, 71))
        self.formLayout = QFormLayout(self.formLayoutWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.ip = QLineEdit(self.formLayoutWidget)
        self.ip.setObjectName(u"ip")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.ip)

        self.label = QLabel(self.formLayoutWidget)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.label)

        self.username = QLineEdit(self.formLayoutWidget)
        self.username.setObjectName(u"username")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.username)

        self.label_2 = QLabel(self.formLayoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.label_2)


        self.retranslateUi(NetSettings)
        self.buttonBox.accepted.connect(NetSettings.accept)
        self.buttonBox.rejected.connect(NetSettings.reject)

        QMetaObject.connectSlotsByName(NetSettings)
    # setupUi

    def retranslateUi(self, NetSettings):
        NetSettings.setWindowTitle(QCoreApplication.translate("NetSettings", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("NetSettings", u"IP", None))
        self.label_2.setText(QCoreApplication.translate("NetSettings", u"Username", None))
    # retranslateUi

