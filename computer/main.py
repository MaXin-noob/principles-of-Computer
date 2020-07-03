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
        # 格式：操作码（4位） 目的操作数寻址方式（3位） 目的操作数（3位） 源操作数寻址方式（3位） 源操作数（3位）
        self.instruction_set = {
            # 单操作数指令
            "INC": "1011000000000ddd",
            "DEC": "1101000000000ddd",
            "NEC": "1011000000000ddd",
            "JMP": "0111000000000ddd",
            "NEC": "1000000000000ddd",
            "JC": "1000000000000ddd",
            # 双操作数指令
            "ADD": "0001000sss000ddd",
            "SUB": "0010000sss000ddd",
            "AND": "0100000sss000ddd",
            "MOV": "1010000sss000ddd",
            "NOP": "0000000000000000",
            "LDI": "1110xxxxxxxx0ddd",
            "LD": "1001xxxxxxxx1ddd",
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
            ##################以上为通用操作######################
            "102": {
                "micros": "010000000010000000000000202",  #
                "micro-order": "Rs->BUS,BUS->SR"
            },
            "103": {
                "micros": "010000000010000000000000203",  #
                "micro-order": "Rs->BUS,BUS->SR"
            },
            "104": {
                "micros": "001100000001000000000000110",  #
                "micro-order": "LT->BUS,BUS->LA"
            },
            "105": {
                "micros": "000000000000000000000000300",  #
                "micro-order": "NOP"
            },
            "106": {
                "micros": "010000000010000000000000206",  #
                "micro-order": "Rs->BUS,BUS->SR"
            },
            "107": {
                "micros": "010000000010000000000000207",  #
                "micro-order": "Rs->BUS,BUS->MAR,READ,WAIT"
            },
            "108": {
                "micros": "001000000001000000000000300",  #
                "micro-order": "MDR->BUS,BUS->LA,INC"
            },
            "109": {
                "micros": "001000000001000000000000300",  #
                "micro-order": "SR->BUS,0->C0,AND"
            },
            "110": {
                "micros": "010100000000000000001000204",  #
                "micro-order": "Rd->BUS,0->C0,ADD"
            },
            "202": {
                "micros": "010100000001000000000000271",  #
                "micro-order": "Rd->BUS,BUS->LA"
            },
            "203": {
                "micros": "010100001000000001010000271",  #
                "micro-order": "Rd->BUS,BUS->MAR,READ,WAIT"
            },
            "204": {
                "micros": "001100010000000001010000272",  #
                "micro-order": "LT->BUS,BUS->MAR,READ,WAIT"
            },
            "206": {
                "micros": "001100010000000001010000270",  #
                "micro-order": "Rd->BUS,BUS->LA"
            },
            "207": {
                "micros": "010100000001000000000000270",  #
                "micro-order": "Rd->BUS,BUS->LA"
            },
            "270": {
                "micros": "011001100000000000000000300",  #
                "micro-order": "SR->BUS,ADD,ALU->LT"
            },
            "271": {
                "micros": "011010100000000000000000300",  #
                "micro-order": "SR->BUS,BUS->Rd"
            },
            "272": {
                "micros": "001000000001000000000000300",  #
                "micro-order": "MDR->BUS,BUS->LA,DEC"
            },
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
            context = ToolFunction.analyze(value)  # 将汇编指令分解
            code = self.instruction_set.get(context[0])  # 从指令集中找对应的指令
            if len(context) == 3:
                if context[0] == "LDI" or context[0] == "LD":
                    code = code.replace("ddd", "{:0>3b}".format(int(context[1][context[1].find("R") + 1])))
                    code = code.replace("xxxxxxxx", '{:0>8b}'.format(int(context[2], 16)))
                    context_.append(code)
                elif context[0] == "MOV" or context[0] == "SUB" or context[0] == "ADD" or context[0] == "AND":
                    # 判断寻址方式，暂时只判断寄存器寻址，寄存器间址，自增型寄存器间址,尚未判断自增型双间址
                    # 寄存器间址
                    if "(" in context[2]:  # 源操作数寻址方式
                        code = ToolFunction.replace_char(code, "1", 6)
                    if "(" in context[1]:  # 目的操作数寻址方式
                        code = ToolFunction.replace_char(code, "1", 12)
                    # 自增型间址
                    if "+" in context[2]:
                        code = ToolFunction.replace_char(code, "1", 4)
                    code = code.replace("ddd", "{:0>3b}".format(int(context[1][context[1].find("R") + 1])))
                    code = code.replace("sss", "{:0>3b}".format(int(context[2][context[2].find("R") + 1])))
                    context_.append(code)
                continue
            if len(context) == 2:
                # 寄存器间址
                if "(" in context[1]:
                    code = ToolFunction.replace_char(code, "1", 6)
                # 变址寻址，都带有括号，所以先判断是否含有括号
                if "X" in context[1]:
                    code = ToolFunction.replace_char(code, "1", 4)
                # 自增双间址
                if "@" in context[1]:
                    code = ToolFunction.replace_char(code, "1", 5)
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
            if machine_code[4:7] == "000":  # 寄存器寻址
                entrance_code = "102"
            if machine_code[4:7] == "001":  # 寄存器间址
                entrance_code = "103"
        if machine_code[:4] == "1101":  # DEC指令入口
            if machine_code[4:7] == "000":  # 寄存器寻址
                entrance_code = "102"
            if machine_code[4:7] == "001":  # 寄存器间址
                entrance_code = "103"
            if machine_code[4:7] == "101":  # 自增双间址
                entrance_code = "104"
        if machine_code[:4] == "0000":  # NOP指令
            entrance_code = "105"
        if machine_code[:4] == "0001":  # ADD指令
            if machine_code[4:7] == "000":  # 寄存器寻址
                entrance_code = "106"
            if machine_code[4:7] == "001":  # 寄存器间址
                entrance_code = "107"
            if machine_code[4:7] == "101":  # 自增型间址
                entrance_code = "106"
        if machine_code[:4] == "0010":  # SUB指令
            if machine_code[4:7] == "000":  # 寄存器寻址
                entrance_code = "106"
            if machine_code[4:7] == "001":  # 寄存器间址
                entrance_code = "107"
        if machine_code[:4] == "1011":  # INC指令
            if machine_code[4:7] == "011":  # 自增型双间址
                entrance_code = "108"
        if machine_code[:4] == "1001":  # LD指令
            entrance_code = "102"
        if machine_code[:4] == "0100":  # AND指令
            entrance_code = "109"

        return entrance_code

    def run(self, machine_code):
        """
        执行一条机器码
        :param machine_code: 机器码
        :return: 微操作序列
        """
        note = []
        entrance_code = "000"  # 公共微指令地址设为000
        self.PC += 2  # PC自增
        while entrance_code != "300":  # 当前微程序结束
            if entrance_code != "300":
                note.append(self.control_memory[entrance_code]["micro-order"])  # 记录微操作
            case = self.control_memory[entrance_code]["micros"][21:24]  # 确定测试判断
            if case == "100":  # 下址PLA给出
                entrance_code = self.PLA(machine_code)
            if case == "000":  # 顺序执行
                entrance_code = self.control_memory[entrance_code]["micros"][24:27]
        source_operand = str(int(machine_code[13:16], 2))  # 获取源操作数
        destination_operand = str(int(machine_code[7:10], 2))  # 获取目的操作数
        self.SR = int(machine_code[13:16], 2)
        if machine_code[:4] == "1110":  # LDI指令
            self.set_register_value(source_operand, int(machine_code[4:12], 2))
            self.SR = self.BUS
        if machine_code[:4] == "1010":  # MOV指令
            if machine_code[4:7] == "000":  # 寄存器寻址
                self.set_register_value(source_operand, self.judgment_register(destination_operand))
            if machine_code[4:7] == "001":  # 寄存器间址
                self.set_register_value(source_operand,
                                        self.judgment_register(str(self.judgment_register(destination_operand))))
        if machine_code[:4] == "1101":  # DEC指令
            if machine_code[4:7] == "000":  # 寄存器寻址
                self.set_register_value("MAR", self.judgment_register(source_operand) - 1)
            if machine_code[4:7] == "001":  # 寄存器间址
                self.set_register_value("MAR",
                                        self.judgment_register(str(self.judgment_register(source_operand))) - 1)
            if machine_code[4:7] == "101":  # 自增双间址
                self.set_register_value("MAR",
                                        self.judgment_register(
                                            str(self.judgment_register(source_operand) + self.PC)) - 1)
                self.memory[str(self.judgment_register(source_operand) + self.PC)] = self.MAR  # 写入内存
        if machine_code[:4] == "0001":  # ADD指令
            if machine_code[4:7] == "000":  # 寄存器寻址
                self.set_register_value(source_operand,
                                        self.judgment_register(destination_operand) + self.judgment_register(
                                            source_operand))
            if machine_code[4:7] == "001":  # 寄存器间址
                self.set_register_value(source_operand, self.judgment_register(
                    str(self.judgment_register(destination_operand))) + self.judgment_register(source_operand))
            if machine_code[4:7] == "101":  # 自增型间址
                self.set_register_value(source_operand, self.judgment_register(
                    str(self.judgment_register(destination_operand))) + self.judgment_register(source_operand))
                self.set_register_value(destination_operand, self.judgment_register(destination_operand) + 1)
        if machine_code[:4] == "0010":  # SUB指令
            if machine_code[4:7] == "000":  # 寄存器寻址
                self.set_register_value(source_operand, self.judgment_register(
                    source_operand) -
                                        self.judgment_register(destination_operand))
            if machine_code[4:7] == "001":  # 寄存器间址
                self.set_register_value(source_operand, self.judgment_register(source_operand) - self.judgment_register(
                    str(self.judgment_register(destination_operand))))
        if machine_code[:4] == "1011":  # INC指令
            if machine_code[4:7] == "011":  # 自增型双间址
                self.set_register_value("MAR", self.judgment_register(
                    str(self.judgment_register(str(self.judgment_register(source_operand))))) + 1)  # 写入MAR
                self.set_register_value(source_operand, self.judgment_register(source_operand) + 1)  # 自增
                self.memory[str(self.judgment_register(str(self.judgment_register(source_operand))))] = self.MAR  # 写入内存
        if machine_code[:4] == "1001":  # LD指令
            self.set_register_value(source_operand, self.judgment_register(str(int(machine_code[4:12], 2))))
            self.memory[str(int(machine_code[4:12], 2))] = self.judgment_register(source_operand)
        if machine_code[:4] == "0100":  # AND指令
            self.set_register_value(source_operand,
                                    self.judgment_register(destination_operand) ^ self.judgment_register(
                                        source_operand))
        self.IMDR = int(machine_code, 2)
        self.IMAR = self.PC - 2
        return note

    def set_register_value(self, source_operand, value):
        """
        设置对应寄存器的值,适用于LDI和MOV指令
        :param source_operand: 寄存器编号（字符串形式）
        :param value: 需要设置的值
        :return:
        """
        if source_operand == "0":
            self.R0 = value
        elif source_operand == "1":
            self.R1 = value
        elif source_operand == "2":
            self.R2 = value
        elif source_operand == "3":
            self.R3 = value
        elif source_operand == "4":
            self.R4 = value
        elif source_operand == "5":
            self.R5 = value
        elif source_operand == "6":
            self.R6 = value
        elif source_operand == "7":
            self.R7 = value
        elif source_operand == "MAR":
            self.MAR = value
        self.BUS = value

    def judgment_register(self, register):
        """
        根据字符串返回对应的寄存器
        :param register: 字符串形式寄存器的值
        :return: 寄存器的值
        """
        if register == "0":
            return self.R0
        elif register == "1":
            return self.R1
        elif register == "2":
            return self.R2
        elif register == "3":
            return self.R3
        elif register == "4":
            return self.R4
        elif register == "5":
            return self.R5
        elif register == "6":
            return self.R6
        elif register == "7":
            return self.R7
        else:  # 即返回该地址寄存器初始值
            return 0x000f
