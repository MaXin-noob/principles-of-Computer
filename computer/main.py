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
            "LD": "1001xxxxxxxx1ddd",
            "NOP": "0000000000000000",
        }
        # 控存
        # TODO：控存尚未写完，大部分指令没有加测试判断以及下址，没有 # 符号的都没设计完成
        self.control_memory = {
            "000": {
                "micros": "000101101000000001101000001",  #
                "micro-order": "PC->BUS,BUS->MAR,READ,CLEAR LA,1->C0,ADD,ALU->LT"
            },
            "001": {
                "micros": "001100100000000000010000002",  #
                "micro-order": "LT->BUS,BUS->PC,WAIT"
            },
            "002": {
                "micros": "001001000000000000000100000",  #
                "micro-order": "MDR->BUS,BUS->IR"
            },
            "100": {
                "micros": "000000000000000000000000000",  #
                "micro-order": ""
            },
            "102": {
                "micros": "010000000010000000000000202",  #
                "micro-order": "Rs->BUS,BUS->SR"
            },
            "103": {
                "micros": "010000000010000000000000203",  #
                "micro-order": "Rs->BUS,BUS->SR"
            },
            "112": {
                "micros": "010000001000000001010",
                "micro-order": "Rs->BUS,BUS->MAR,READ,WAIT"
            },
            "125": {
                "micros": "001000000010000000000",
                "micro-order": "MAR->BUS,BUS->IR"
            },
            "200": {
                "micros": "000000000000000000000",
                "micro-order": ""
            },
            "202": {
                "micros": "010100000001000000000000271",  #
                "micro-order": "Rd->BUS,BUS->LA"
            },
            "203": {
                "micros": "010100001000000001010000271",  #
                "micro-order": "Rd->BUS,BUS->MAR,READ,WAIT"
            },
            "270": {
                "micros": "011001100000000000000",
                "micro-order": "SR->BUS,ADD,ALU->LT"
            },
            "271": {
                "micros": "011010100000000000000000300",  #
                "micro-order": "SR->BUS,BUS->Rd"
            },
            "273": {
                "micros": "001110100000000000000",
                "micro-order": "LT->BUS,BUS->Rd"
            }
        }
        self.PC = 4096
        self.assembly_code_2 = []

    def compile(self, assembly_code):
        """
        将汇编代码编译成机器码
        :param assembly_code: 汇编文件
        :return: 机器码
        """
        context_ = list()
        for value in assembly_code:
            context = ToolFunction.analyze(value)#将汇编指令分解
            code = self.instruction_set.get(context[0])  # 从指令集中找对应的指令
            if len(context) == 3:
                if context[0] == "LDI" or context[0] == "LD":
                    code = code.replace("ddd", "{:0>3b}".format(int(context[1][context[1].find("R") + 1])))
                    code = code.replace("xxxxxxxx", '{:0>8b}'.format(int(context[2], 16)))
                    context_.append(code)
                elif context[0] == "MOV" or context[0] == "SUB" or context[0] == "ADD" or context[0] == "AND":
                    #判断寻址方式，暂时只判断寄存器寻址，寄存器间址，尚未判断自增型寄存器间址以及自增型双间址
                    if "(" in context[2]:
                        code = ToolFunction.replace_char(code, "1", 6)
                    if "(" in context[1]:
                        code = ToolFunction.replace_char(code, "1", 12)
                    code = code.replace("ddd", "{:0>3b}".format(int(context[1][context[1].find("R") + 1])))
                    code = code.replace("sss", "{:0>3b}".format(int(context[2][context[2].find("R") + 1])))
                    context_.append(code)
                    print(code[6])
                continue
            if len(context) == 2:
                code = code.replace("ddd", "{:0>3b}".format(int(context[1][context[1].find("R") + 1])))
                context_.append(code)
                continue
            if len(context) == 1:
                context_.append(code)
                continue
        return context_

    def PLA(self, machine_code):
        """
        找到 machine_code 对应的微指令入口
        :param machine_code: 机器码
        :return:
        """
        entrance_code = ""
        if machine_code[:4] == "1110":  # LDI指令入口
            entrance_code = "102"
        if machine_code[:4] == "1010":  # MOV指令入口
            if machine_code[6] == "0":  # 寄存器寻址
                entrance_code = "102"
            if machine_code[6] == "1":  # 寄存器间址
                entrance_code = "103"
        return entrance_code

    def run(self, machine_code):
        """
        执行一条机器码
        :param machine_code: 机器码
        :return: 微操作序列
        """
        note = []
        entrance_code = "000"  # 公共微指令地址设为000
        self.PC += 1  # PC自增
        while entrance_code != "300":  # 当前微程序结束
            if entrance_code != "300":
                note.append(self.control_memory[entrance_code]["micro-order"])  # 记录微操作
            case = self.control_memory[entrance_code]["micros"][21:24]  # 确定测试判断
            if case == "100":  # 下址PLA给出
                entrance_code = self.PLA(machine_code)
            if case == "000":  # 顺序执行
                entrance_code = self.control_memory[entrance_code]["micros"][24:27]
        source_operand = "R" + str(int(machine_code[13:16], 2))  # 获取源操作数
        destination_operand = "R" + str(int(machine_code[7:10], 2))  # 获取目的操作数
        if machine_code[:4] == "1110":
            self.set_register_value(source_operand, int(machine_code[4:12], 2))
        if machine_code[:4] == "1010":
            if machine_code[6] == "0":  # 寄存器寻址
                self.set_register_value(source_operand, self.judgment_register(destination_operand))
            if machine_code[6] == "1":  # 寄存器间址
                self.set_register_value(source_operand,
                                        self.judgment_register("R" + str(self.judgment_register(destination_operand))))
        return note

    def set_register_value(self, source_operand, value):
        """
        设置对应寄存器的值,适用于LDI和MOV指令
        :param source_operand: 寄存器编号（字符串形式）
        :param value: 需要设置的值
        :return:
        """
        if source_operand == "R0":
            self.R0 = value
        elif source_operand == "R1":
            self.R1 = value
        elif source_operand == "R2":
            self.R2 = value
        elif source_operand == "R3":
            self.R3 = value
        elif source_operand == "R4":
            self.R4 = value
        elif source_operand == "R5":
            self.R5 = value
        elif source_operand == "R6":
            self.R6 = value
        elif source_operand == "R7":
            self.R7 = value
        self.BUS = value
        self.SR = self.BUS
        self.IMAR = self.PC - 1

    def judgment_register(self, register):
        """
        根据字符串返回对应的寄存器
        :param register: 字符串形式寄存器的值
        :return: 寄存器的值
        """
        if register == "R0":
            return self.R0
        elif register == "R1":
            return self.R1
        elif register == "R2":
            return self.R2
        elif register == "R3":
            return self.R3
        elif register == "R4":
            return self.R4
        elif register == "R5":
            return self.R5
        elif register == "R6":
            return self.R6
        elif register == "R7":
            return self.R7
