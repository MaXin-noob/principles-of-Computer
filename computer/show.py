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
        self.machine_code = []
        self.the_number_of_clicks = 0
        self.computer = main.CPU()
        self.ui = Interface.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.listWidget_5.addItem("IAD     IValue")
        self.set_control_memory()
        self.ui.pushButton.clicked.connect(self.open_file_success_click_button)
        self.ui.pushButton_2.clicked.connect(self.single_cycle_execution_click_button)

    def open_file_success_click_button(self):
        """
        选择汇编文件并且转机器码，同时显示
        :return:
        """
        s = ""
        filename = QFileDialog.getOpenFileName(self, '选择文件', './', '*.data')
        self.assembly_code = ToolFunction.readFile(filename[0])
        if self.assembly_code:
            for line in self.assembly_code:
                self.ui.listWidget.addItem(line)
            self.machine_code = self.computer.compile(self.assembly_code)
            for key, value in enumerate(self.machine_code):
                for i in range(0, len(value), 4):
                    s += value[i:i + 4]
                    s += " "
                self.ui.listWidget_2.addItem(s)
                self.ui.listWidget_5.addItem("{0:x}    {1:s}".format(key + 4096, value))
                s = ""
            self.ui.lineEdit_pc.setText("{0:0>4x}".format(self.computer.PC))

    def single_cycle_execution_click_button(self):
        """
        单步执行，当前只能一次性执行一条指令，无法细化为微操作
        :return:
        """
        note = self.computer.run(self.machine_code[self.the_number_of_clicks])
        for value in note:
            self.ui.listWidget_4.addItem(value)
        self.set_all_register()
        self.the_number_of_clicks += 1

    def set_all_register(self):
        """
        一次性设置所有UI界面
        :return:
        """
        self.ui.lineEdit_pc.setText("{0:0>4X}".format(self.computer.PC))
        self.ui.lineEdit_R0.setText("{0:0>4X}".format(self.computer.R0))
        self.ui.lineEdit_R1.setText("{0:0>4X}".format(self.computer.R1))
        self.ui.lineEdit_R2.setText("{0:0>4X}".format(self.computer.R2))
        self.ui.lineEdit_R3.setText("{0:0>4X}".format(self.computer.R3))
        self.ui.lineEdit_R4.setText("{0:0>4X}".format(self.computer.R4))
        self.ui.lineEdit_R5.setText("{0:0>4X}".format(self.computer.R5))
        self.ui.lineEdit_R6.setText("{0:0>4X}".format(self.computer.R6))
        self.ui.lineEdit_R7.setText("{0:0>4X}".format(self.computer.R7))
        self.ui.lineEdit_sr.setText("{0:0>4X}".format(self.computer.SR))
        self.ui.lineEdit_bus.setText("{0:0>4X}".format(self.computer.BUS))
        self.ui.lineEdit_imar.setText("{0:0>4X}".format(self.computer.IMAR))

    def set_control_memory(self):
        """
        显示控存的内容
        :return:
        """
        for key in self.computer.control_memory.keys():
            s = "{0}\t{1}".format(key, self.computer.control_memory.get(key)["micros"])
            self.ui.listWidget_3.addItem(s)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    show = MyWindow()
    show.show()
    sys.exit(app.exec_())
