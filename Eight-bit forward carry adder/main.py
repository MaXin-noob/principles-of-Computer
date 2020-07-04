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

addend1 = [0, 0, 0, 0, 0, 0, 0, 0]
addend2 = [0, 0, 0, 0, 0, 0, 0, 0]
p = [0, 0, 0, 0, 0, 0, 0, 0]
g = [0, 0, 0, 0, 0, 0, 0, 0]
c = [0, 0, 0, 0, 0, 0, 0, 0]
s = [0, 0, 0, 0, 0, 0, 0, 0]
m = [0]


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.text1_value = 0
        self.text2_value = 0
        self.ui = untitled.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.success_click_button)

    def success_click_button(self):
        addend = self.get_addend()  # 获取文本内容
        self.text1_value = int(addend[0])  # 转成整数类型
        self.text2_value = int(addend[1])  # 转成整数类型
        complement_1 = self.original_code_2_complement(self.true_2_original_code(self.text1_value))  # 求补码
        self.ui.lineEdit_3.setText(complement_1+ "(补码)")
        complement_2 = self.original_code_2_complement(self.true_2_original_code(self.text2_value))  # 求补码
        self.ui.lineEdit_4.setText(complement_2 + "(补码)")
        for key, value in enumerate(complement_1[::-1]):  # 存入列表
            addend1[key] = int(value)
        for key, value in enumerate(complement_2[::-1]):  # 存入列表
            addend2[key] = int(value)
        self.progressive_calculate()
        self.local_calculate()
        self.carry_calculate()
        self.res_calculate()
    def get_addend(self):
        """
        获取文本框内容
        :return: 文本框内容
        """
        text_1 = self.ui.lineEdit.text()
        text_2 = self.ui.lineEdit_2.text()
        return [text_1, text_2]

    def original_code_2_complement(self, str_bin: str) -> str:
        """
        原码转补码
        :param str_bin:原码
        :return:补码
        """
        str_new = ""
        flag = True
        if str_bin[0] == "0":
            complement = str_bin
        else:
            for i in str_bin[1:]:
                if i == "0":
                    str_new += "1"
                else:
                    str_new += "0"
            str_flash = '1' + str_new  # 反码
            i = len(str_flash) - 1
            while (flag):
                if (str_flash[i] == '1'):
                    i -= 1
                elif (str_flash[i] == '0'):
                    flag = False
            complement = str_flash[0:i] + '1' + (len(str_flash) - i - 1) * '0'
        return complement

    def true_2_original_code(self, truth_value: int) -> str:
        """
        真值转原码
        :param truth_value: 真值
        :return: 原码
        """
        if truth_value > 0:
            s = str(bin(truth_value))[2:]
            s = "0" + "{0:0>7b}".format(int(s, 2))
        else:
            s = str(bin(truth_value))[3:]
            s = "1" + "{0:0>7b}".format(int(s, 2))
        return s

    def progressive_calculate(self):
        """
        计算递进位并展示
        :return: 无
        """
        for key in range(len(p)):
            p[key] = addend1[key] ^ addend2[key]
        self.ui.lineEdit_p0.setText(str(p[0]))
        self.ui.lineEdit_p1.setText(str(p[1]))
        self.ui.lineEdit_p2.setText(str(p[2]))
        self.ui.lineEdit_p3.setText(str(p[3]))
        self.ui.lineEdit_p4.setText(str(p[4]))
        self.ui.lineEdit_p5.setText(str(p[5]))
        self.ui.lineEdit_p6.setText(str(p[6]))
        self.ui.lineEdit_p7.setText(str(p[7]))

    def local_calculate(self):
        """
        计算本地进位并展示
        :return:
        """
        for key in range(len(g)):
            g[key] = addend1[key] & addend2[key]
        self.ui.lineEdit_g0.setText(str(g[0]))
        self.ui.lineEdit_g1.setText(str(g[1]))
        self.ui.lineEdit_g2.setText(str(g[2]))
        self.ui.lineEdit_g3.setText(str(g[3]))
        self.ui.lineEdit_g4.setText(str(g[4]))
        self.ui.lineEdit_g5.setText(str(g[5]))
        self.ui.lineEdit_g6.setText(str(g[6]))
        self.ui.lineEdit_g7.setText(str(g[7]))

    def carry_calculate(self):
        """
        计算是否进位并展示
        :return:
        """
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
        """
        计算结果
        :return:
        """
        res = ''
        s[0] = (addend1[0] ^ addend2[0]) ^ m[0];
        s[1] = (addend1[1] ^ addend2[1]) ^ ((addend1[0] & addend2[0]) | (addend1[0] ^ addend2[0]) & m[0]);
        s[2] = (addend1[2] ^ addend2[2]) ^ (
                (addend1[1] & addend2[1]) | (addend1[1] ^ addend2[1]) & (addend1[0] & addend2[0]) | (
                addend1[1] ^ addend2[1]) & (addend1[0] & addend2[0]) & m[0]);
        s[3] = (addend1[3] ^ addend2[3]) ^ (
                (addend1[2] & addend2[2]) | (addend1[2] ^ addend2[2]) & (addend1[1] & addend2[1]) | (
                addend1[2] ^ addend2[2]) & (addend1[1] ^ addend2[1]) & (addend1[0] & addend2[0]) | (
                        addend1[2] ^ addend2[2]) & (addend1[1] ^ addend2[1]) & (
                        addend1[0] & addend2[0]) & m[0]);
        s[4] = (addend1[4] ^ addend2[4]) ^ (
                (addend1[3] & addend2[3]) | (addend1[3] ^ addend2[3]) & (addend1[2] & addend2[2]) | (
                addend1[3] ^ addend2[3]) & (addend1[2] ^ addend2[2]) & (addend1[1] & addend2[1]) | (
                        addend1[3] ^ addend2[3]) & (addend1[2] ^ addend2[2]) & (
                        addend1[1] ^ addend2[1]) & (addend1[0] & addend2[0]) | (addend1[3] ^ addend2[3]) & (
                        addend1[2] ^ addend2[2]) & (addend1[1] ^ addend2[1]) & (addend1[0] ^ addend2[0]) &
                m[0]);
        s[5] = (addend1[5] ^ addend2[5]) ^ (
                (addend1[4] & addend2[4]) | (addend1[4] ^ addend2[4]) & (addend1[3] & addend2[3]) | (
                addend1[4] ^ addend2[4]) & (addend1[3] ^ addend2[3]) & (addend1[2] & addend2[2]) | (
                        addend1[4] ^ addend2[4]) & (addend1[3] ^ addend2[3]) & (
                        addend1[2] ^ addend2[2]) & (addend1[1] & addend2[1]) | (addend1[4] ^ addend2[4]) & (
                        addend1[3] ^ addend2[3]) & (addend1[2] ^ addend2[2]) & (addend1[1] ^ addend2[1]) & (
                        addend1[0] & addend2[0]) | (addend1[4] ^ addend2[4]) & (
                        addend1[3] ^ addend2[3]) & (addend1[2] ^ addend2[2]) & (addend1[1] ^ addend2[1]) & (
                        addend1[0] ^ addend2[0]) & m[0]);
        s[6] = (addend1[6] ^ addend2[6]) ^ (
                (addend1[5] & addend2[5]) | (addend1[5] ^ addend2[5]) & (addend1[4] & addend2[4]) | (
                addend1[5] ^ addend2[5]) & (addend1[4] ^ addend2[4]) & (addend1[3] & addend2[3]) | (
                        addend1[5] ^ addend2[5]) & (addend1[4] ^ addend2[4]) & (
                        addend1[3] ^ addend2[3]) & (addend1[2] & addend2[2]) | (addend1[5] ^ addend2[5]) & (
                        addend1[4] ^ addend2[4]) & (addend1[3] ^ addend2[3]) & (addend1[2] ^ addend2[2]) & (
                        addend1[1] & addend2[1]) | (addend1[5] ^ addend2[5]) & (
                        addend1[4] ^ addend2[4]) & (addend1[3] ^ addend2[3]) & (addend1[2] ^ addend2[2]) & (
                        addend1[1] ^ addend2[1]) & (addend1[0] & addend2[0]) | (addend1[5] ^ addend2[5]) & (
                        addend1[4] ^ addend2[4]) & (
                        addend1[3] ^ addend2[3]) & (addend1[2] ^ addend2[2]) & (addend1[1] ^ addend2[1]) & (
                        addend1[0] ^ addend2[0]) & m[0]);
        s[7] = (addend1[7] ^ addend2[7]) ^ (
                (addend1[6] & addend2[6]) | (addend1[6] ^ addend2[6]) & (addend1[5] & addend2[5]) | (
                addend1[6] ^ addend2[6]) & (addend1[5] ^ addend2[5]) & (addend1[4] & addend2[4]) | (
                        addend1[6] ^ addend2[6]) & (addend1[5] ^ addend2[5]) & (
                        addend1[4] ^ addend2[4]) & (addend1[3] & addend2[3]) | (addend1[6] ^ addend2[6]) & (
                        addend1[5] ^ addend2[5]) & (addend1[4] ^ addend2[4]) & (addend1[3] ^ addend2[3]) & (
                        addend1[2] & addend2[2]) | (addend1[6] ^ addend2[6]) & (
                        addend1[5] ^ addend2[5]) & (addend1[4] ^ addend2[4]) & (addend1[3] ^ addend2[3]) & (
                        addend1[2] ^ addend2[2]) & (addend1[1] & addend2[1]) | (addend1[6] ^ addend2[6]) & (
                        addend1[5] ^ addend2[5]) & (
                        addend1[4] ^ addend2[4]) & (addend1[3] ^ addend2[3]) & (addend1[2] ^ addend2[2]) & (
                        addend1[1] ^ addend2[1]) & (addend1[0] & addend2[0]) | (addend1[6] ^ addend2[6]) & (
                        addend1[5] ^ addend2[5]) & (
                        addend1[4] ^ addend2[4]) & (addend1[3] ^ addend2[3]) & (addend1[2] ^ addend2[2]) & (
                        addend1[1] ^ addend2[1]) & (addend1[0] ^ addend2[0]) & m[0]);
        for i in s[::-1]:
            res += str(i)
        res = self.original_code_2_complement(res)
        add = self.text1_value+self.text2_value
        self.ui.lineEdit_result.setText(res + "（真值：%d）"%add)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    show = MyWindow()
    show.show()
    sys.exit(app.exec_())
