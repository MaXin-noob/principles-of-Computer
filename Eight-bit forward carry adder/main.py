#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File : main.py
# @Project : 超前加法器
# @Software: PyCharm
# @Author : 大红昕
# @Time : 2020/6/16 17:21

from PyQt5.QtWidgets import QApplication, QMainWindow
import untitled
import sys
from PyQt5.QtCore import Qt

a = [0, 0, 0, 0, 0, 0, 0, 0]
b = [0, 0, 0, 0, 0, 0, 0, 0]
p = [0, 0, 0, 0, 0, 0, 0, 0]
g = [0, 0, 0, 0, 0, 0, 0, 0]
c = [0, 0, 0, 0, 0, 0, 0, 0]
s = [0, 0, 0, 0, 0, 0, 0, 0]
m = [0]


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = untitled.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.success_click_button)

    def success_click_button(self):
        self.is_chick()
        self.progressive_calculate()
        self.local_calculate()
        self.carry_calculate()
        self.res_calculate()

    def is_chick(self):
        """
        判断多选框中的值
        :return:无
        """
        if self.ui.a0.isChecked():
            a[0] = 1
        else:
            a[0] = 0
        if self.ui.a1.isChecked():
            a[1] = 1
        else:
            a[1] = 0
        if self.ui.a2.isChecked():
            a[2] = 1
        else:
            a[2] = 0
        if self.ui.a3.isChecked():
            a[3] = 1
        else:
            a[3] = 0
        if self.ui.a4.isChecked():
            a[4] = 1
        else:
            a[4] = 0
        if self.ui.a5.isChecked():
            a[5] = 1
        else:
            a[5] = 0
        if self.ui.a6.isChecked():
            a[6] = 1
        else:
            a[6] = 0
        if self.ui.a7.isChecked():
            a[7] = 1
        else:
            a[7] = 0
        if self.ui.b0.isChecked():
            b[0] = 1
        else:
            b[0] = 0
        if self.ui.b1.isChecked():
            b[1] = 1
        else:
            b[1] = 0
        if self.ui.b2.isChecked():
            a[2] = 1
        else:
            b[2] = 0
        if self.ui.b3.isChecked():
            b[3] = 1
        else:
            b[3] = 0
        if self.ui.b4.isChecked():
            b[4] = 1
        else:
            b[4] = 0
        if self.ui.b5.isChecked():
            b[5] = 1
        else:
            b[5] = 0
        if self.ui.b6.isChecked():
            b[6] = 1
        else:
            b[6] = 0
        if self.ui.b7.isChecked():
            b[7] = 1
        else:
            b[7] = 0

    def progressive_calculate(self):
        """
        计算递进位并传参
        :return: 无
        """
        for key in range(len(p)):
            p[key] = a[key] ^ b[key]
        self.ui.lineEdit_p0.setText(str(p[0]))
        self.ui.lineEdit_p1.setText(str(p[1]))
        self.ui.lineEdit_p2.setText(str(p[2]))
        self.ui.lineEdit_p3.setText(str(p[3]))
        self.ui.lineEdit_p4.setText(str(p[4]))
        self.ui.lineEdit_p5.setText(str(p[5]))
        self.ui.lineEdit_p6.setText(str(p[6]))
        self.ui.lineEdit_p7.setText(str(p[7]))

    def local_calculate(self):
        for key in range(len(g)):
            g[key] = a[key] & b[key]
        self.ui.lineEdit_g0.setText(str(g[0]))
        self.ui.lineEdit_g1.setText(str(g[1]))
        self.ui.lineEdit_g2.setText(str(g[2]))
        self.ui.lineEdit_g3.setText(str(g[3]))
        self.ui.lineEdit_g4.setText(str(g[4]))
        self.ui.lineEdit_g5.setText(str(g[5]))
        self.ui.lineEdit_g6.setText(str(g[6]))
        self.ui.lineEdit_g7.setText(str(g[7]))

    def carry_calculate(self):
        c[0] = g[0] | p[0] & m[0];
        c[1] = g[1] | p[1] & g[0] | p[1] & p[0] & m[0];
        c[2] = g[2] | p[2] & g[1] | p[2] & p[1] & g[0] | p[2] & p[1] & p[0] & m[0];
        c[3] = g[3] | p[3] & g[2] | p[3] & p[2] & g[1] | p[3] & p[2] & p[1] & g[0] | p[3] & p[2] & p[1] & p[0] & m[0]
        c[4] = g[4] | p[4] & g[3] | p[4] & p[3] & g[2] | p[4] & p[3] & p[2] & g[1] | p[4] & p[3] & p[2] & p[1] & g[0] | \
               p[4] & p[3] & p[2] & p[1] & p[0] & m[0]
        c[5] = g[5] | p[5] & g[4] | p[5] & p[4] & g[3] | p[5] & p[4] & p[3] & g[2] | p[5] & p[4] & p[3] & p[2] & g[1] | \
               p[5] & p[4] & p[3] & p[2] & p[1] & g[0] | p[5] & p[4] & p[3] & p[2] & p[1] & p[0] & m[0]
        c[6] = g[6] | p[6] & g[5] | p[6] & p[5] & g[4] | p[6] & p[5] & p[4] & g[3] | p[6] & p[5] & p[4] & p[3] & g[2] | \
               p[6] & p[5] & p[4] & p[3] & p[2] & g[1] | p[6] & p[5] & p[4] & p[3] & p[2] & p[1] & g[0] | p[6] & p[5] & \
               p[4] & p[3] & p[2] & p[1] & p[0] & m[0]
        c[7] = g[7] | p[7] & g[6] | p[7] & p[6] & g[5] | p[7] & p[6] & p[5] & g[4] | p[7] & p[6] & p[5] & p[4] & g[3] | \
               p[7] & p[6] & p[5] & p[4] & p[3] & g[2] | p[7] & p[6] & p[5] & p[4] & p[3] & p[2] & g[1] | p[7] & p[6] & \
               p[5] & p[4] & p[3] & p[2] & p[1] & g[0] | p[7] & p[6] & p[5] & p[4] & p[3] & p[2] & p[1] & p[0] & m[0]
        self.ui.c0.setChecked(c[0])
        self.ui.c1.setChecked(c[1])
        self.ui.c2.setChecked(c[2])
        self.ui.c3.setChecked(c[3])
        self.ui.c4.setChecked(c[4])
        self.ui.c5.setChecked(c[5])
        self.ui.c6.setChecked(c[6])
        self.ui.c7.setChecked(c[7])

    def res_calculate(self):
        res = ''
        s[0] = (a[0] ^ b[0]) ^ m[0];
        s[1] = (a[1] ^ b[1]) ^ ((a[0] & b[0]) | (a[0] ^ b[0]) & m[0]);
        s[2] = (a[2] ^ b[2]) ^ ((a[1] & b[1]) | (a[1] ^ b[1]) & (a[0] & b[0]) | (a[1] ^ b[1]) & (a[0] & b[0]) & m[0]);
        s[3] = (a[3] ^ b[3]) ^ (
                (a[2] & b[2]) | (a[2] ^ b[2]) & (a[1] & b[1]) | (a[2] ^ b[2]) & (a[1] ^ b[1]) & (a[0] & b[0]) | (
                a[2] ^ b[2]) & (a[1] ^ b[1]) & (
                        a[0] & b[0]) & m[0]);
        s[4] = (a[4] ^ b[4]) ^ (
                (a[3] & b[3]) | (a[3] ^ b[3]) & (a[2] & b[2]) | (a[3] ^ b[3]) & (a[2] ^ b[2]) & (a[1] & b[1]) | (
                a[3] ^ b[3]) & (a[2] ^ b[2]) & (
                        a[1] ^ b[1]) & (a[0] & b[0]) | (a[3] ^ b[3]) & (a[2] ^ b[2]) & (a[1] ^ b[1]) & (a[0] ^ b[0]) &
                m[0]);
        s[5] = (a[5] ^ b[5]) ^ (
                (a[4] & b[4]) | (a[4] ^ b[4]) & (a[3] & b[3]) | (a[4] ^ b[4]) & (a[3] ^ b[3]) & (a[2] & b[2]) | (
                a[4] ^ b[4]) & (a[3] ^ b[3]) & (
                        a[2] ^ b[2]) & (a[1] & b[1]) | (a[4] ^ b[4]) & (a[3] ^ b[3]) & (a[2] ^ b[2]) & (a[1] ^ b[1]) & (
                        a[0] & b[0]) | (a[4] ^ b[4]) & (
                        a[3] ^ b[3]) & (a[2] ^ b[2]) & (a[1] ^ b[1]) & (a[0] ^ b[0]) & m[0]);
        s[6] = (a[6] ^ b[6]) ^ (
                (a[5] & b[5]) | (a[5] ^ b[5]) & (a[4] & b[4]) | (a[5] ^ b[5]) & (a[4] ^ b[4]) & (a[3] & b[3]) | (
                a[5] ^ b[5]) & (a[4] ^ b[4]) & (
                        a[3] ^ b[3]) & (a[2] & b[2]) | (a[5] ^ b[5]) & (a[4] ^ b[4]) & (a[3] ^ b[3]) & (a[2] ^ b[2]) & (
                        a[1] & b[1]) | (a[5] ^ b[5]) & (
                        a[4] ^ b[4]) & (a[3] ^ b[3]) & (a[2] ^ b[2]) & (a[1] ^ b[1]) & (a[0] & b[0]) | (a[5] ^ b[5]) & (
                        a[4] ^ b[4]) & (
                        a[3] ^ b[3]) & (a[2] ^ b[2]) & (a[1] ^ b[1]) & (a[0] ^ b[0]) & m[0]);
        s[7] = (a[7] ^ b[7]) ^ (
                (a[6] & b[6]) | (a[6] ^ b[6]) & (a[5] & b[5]) | (a[6] ^ b[6]) & (a[5] ^ b[5]) & (a[4] & b[4]) | (
                a[6] ^ b[6]) & (a[5] ^ b[5]) & (
                        a[4] ^ b[4]) & (a[3] & b[3]) | (a[6] ^ b[6]) & (a[5] ^ b[5]) & (a[4] ^ b[4]) & (a[3] ^ b[3]) & (
                        a[2] & b[2]) | (a[6] ^ b[6]) & (
                        a[5] ^ b[5]) & (a[4] ^ b[4]) & (a[3] ^ b[3]) & (a[2] ^ b[2]) & (a[1] & b[1]) | (a[6] ^ b[6]) & (
                        a[5] ^ b[5]) & (
                        a[4] ^ b[4]) & (a[3] ^ b[3]) & (a[2] ^ b[2]) & (a[1] ^ b[1]) & (a[0] & b[0]) | (a[6] ^ b[6]) & (
                        a[5] ^ b[5]) & (
                        a[4] ^ b[4]) & (a[3] ^ b[3]) & (a[2] ^ b[2]) & (a[1] ^ b[1]) & (a[0] ^ b[0]) & m[0]);
        for i in s[::-1]:
            res += str(i)
        self.ui.lineEdit_result.setText(res)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    show = MyWindow()
    show.show()
    sys.exit(app.exec_())
