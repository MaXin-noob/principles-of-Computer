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
from hardware import Hardware


class CPU(Hardware):
    def __init__(self):
        super().__init__()
        # 指令集
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
        # 控存
        self.control_memory = {
            "000": {
                "micros": "000101110000000001101",
                "micro-order": "PC->BUS,BUS->MAR,READ,CLEAR LA,1->C0,ADD,ALU->LT"
            },
            "001": {
                "micros": "001100100000000000010",
                "micro-order": "LT->BUS,BUS->PC,WAIT"
            },
            "002": {
                "micros": "00100100000000000000",
                "micro-order": "MDR->BUS,BUS->IR"
            },
            "100": {
                "micros": "00000000000000000000",
                "micro-order": ""
            }
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
            code = self.instruction_set.get(context[0])  # 从指令集中找对应的指令
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
            if len(context) == 1:
                context_.append(code)
                continue
        return context_

    # def PLA(self):
    #     print("PLA")
