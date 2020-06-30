#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @File : show.py
# @Project : computer
# @Software: PyCharm
# @Author : 大红昕
# @Time : 2020/6/30 17:50

from tool import ToolFunction
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem
import Interface
import main
from tool import ToolFunction


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.assembly_code = []
        self.computer = main.CPU()
        self.ui = Interface.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.listWidget_5.addItem("IAD     IValue")
        self.ui.pushButton.clicked.connect(self.open_file_success_click_button)

    def open_file_success_click_button(self):
        s = ""
        filename = QFileDialog.getOpenFileName(self, '选择文件', './', '*.data')
        self.assembly_code = ToolFunction.readFile(filename[0])
        if self.assembly_code:
            for line in self.assembly_code:
                self.ui.listWidget.addItem(line)
            machine_code = self.computer.compile(self.assembly_code)
            for key, value in enumerate(machine_code):
                for i in range(0, len(value), 4):
                    s += value[i:i + 4]
                    s += " "
                self.ui.listWidget_2.addItem(s)
                self.ui.listWidget_5.addItem("{0:x}    {1:s}".format(key + 4096, value))
                s = ""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    show = MyWindow()
    show.show()
    sys.exit(app.exec_())
