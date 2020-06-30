#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File : tool.py
# @Project : computer
# @Software: PyCharm
# @Author : 大红昕
# @Time : 2020/6/14 11:51

from tool import ToolFunction
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem
import Interface
import re


# 底层硬件
class Hardware:
    def __init__(self):
        # 通用寄存器
        self.R0 = 0x0000
        self.R1 = 0x0000
        self.R2 = 0x0000
        self.R3 = 0x0000
        self.R4 = 0x0000
        self.R5 = 0x0000
        self.R6 = 0x0000
        self.R7 = 0x0000
        # 特殊寄存器
        self.PC = 0x0000  # 程序计数器
        self.BUS = 0x0000  # 数据总线
        self.SR = 0x0000  # 源操作数寄存器
        self.DR = 0x0000  # 目的操作数寄存器
        self.MAR = 0x0000
        self.MDR = 0x0000
        self.IMAR = 0x0000
        self.IMDR = 0x0000
        # 控制存储器
        self.control_memory = {}


class CPU(Hardware):
    def __init__(self):
        super().__init__()
        self.instruction_set = {
            "ADD": "000100000ddd0sss",
            "SUB": "001000000ddd0sss",
            "AND": "010000000ddd0sss",
            "INC": "1011000000000ddd",
            "DEC": "1101000000000ddd",
            "NEC": "1011000000000ddd",
            "JMP": "0111000000000ddd",
            "NEC": "1000000000000ddd",
            "JC": "1000000000000ddd",
            "MOV": "1010000sss000ddd",
            "LDI": "1110xxxxxxxx0ddd",
            "LD": "1001000000001ddd",
            "NOP": "0000000000000000",
        }
        self.control_memory = {
            "0": "",
            "1":""
        }
        self.PC = 4096

    def compile(self, assembly_code):
        """
        将汇编代码编译成机器码
        :param assembly_code: 汇编文件
        :return: 机器码
        """
        context_ = list()
        for value in assembly_code:
            context = ToolFunction.analyze(value)
            code = self.instruction_set.get(context[0])
            if len(context) == 1:
                context_.append(code)
                continue
            if len(context) == 3:
                if context[0] == "LDI":
                    code = code.replace("ddd", "{:0>3b}".format(int(context[1][context[1].find("R") + 1])))
                    code = code.replace("xxxxxxxx", '{:0>8b}'.format(int(context[2], 16)))
                    context_.append(code)
                else:
                    code = code.replace("ddd", "{:0>3b}".format(int(context[1][context[1].find("R") + 1])))
                    code = code.replace("sss", "{:0>3b}".format(int(context[2][context[2].find("R") + 1])))
                    context_.append(code)
                continue
            if len(context) == 2:
                code = code.replace("ddd", "{:0>3b}".format(int(context[1][context[1].find("R") + 1])))
                context_.append(code)
                continue
        return context_
