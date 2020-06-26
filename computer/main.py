#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File : tool.py
# @Project : 计算机模拟机
# @Software: PyCharm
# @Author : 大红昕
# @Time : 2020/6/14 11:51

from tool import ToolFunction
import sys


class CPU:
    def __init__(self):
        # 通用寄存器
        self.General_register = {
            "R0": "0000",
            "R1": "0000",
            "R2": "0000",
            "R3": "0000",
            "R4": "0000",
            "R5": "0000",
            "R6": "0000",
            "R7": "0000",
        }
        # 特使寄存器
        self.Special_register = {
            "PC": 0,  # 程序计数器
            "BUS": "0000",  # 数据总线
            "SR": "0000",  # 源操作数寄存器
            "DR": "0000",  # 目的操作数寄存器
            "MAR": "0000",  # 主存地址寄存器
            "MDR": "0000",  # 主存数据寄存器
            "IMAR": "0000",  # 指令地址寄存器
            "IMDR": "0000",  # 指令数据寄存器
        }


class Computer(CPU):
    def __init__(self, fileName):
        super().__init__()
        self.note = []
        self.code = ToolFunction.readFile(fileName)

    def order_LDI(self, pro_1, pro_2):
        """
        LDI指令操作函数
        :param pro_1: 目的操作数
        :param pro_2:源操作数
        :return:无
        """
        self.Special_register["BUS"] = pro_2
        self.Special_register["SR"] = self.Special_register["BUS"]
        self.note.append("Rs->BUS,BUS->SR")
        self.Special_register["BUS"] = "0000"
        self.note.append("Rd->BUS,BUS->LA")
        self.Special_register["BUS"] = self.Special_register["SR"]
        self.Special_register[pro_1] = self.Special_register["BUS"]
        self.note.append("SR->BUS,BUS->Rd")

    def order_MOV(self,pro_1,pro_2):
        """
        MOV指令操作函数
        :param pro_1: 目的操作数
        :param pro_2: 源操作数
        :return:无
        """
        

    def run(self):
        for step in self.code.keys():
            cotext = ToolFunction.analyze(self.code[step])
            self.Special_register["BUS"] = self.Special_register["PC"]
            self.Special_register["IMAR"] = self.Special_register["BUS"]
            self.note.append("PC->IBUS,IBUS->IMAR,IREAD")
            self.Special_register["PC"] = step
            self.note.append("PC->BUS,Clear LA,1->C0,ADD")
            self.note.append("LT->IBUS,IBUS->PC,IWAIT")
            self.note.append("PC->IBUS,IBUS->IMAR,IREAD")
            self.note.append("IMDR->IBUS,IBUS->IR")
            if cotext[0] == "LDI":
                self.order_LDI(cotext[1], cotext[2])
            else:
                break


compuer = Computer("./cesi1.data")
compuer.run()
for i in compuer.note:
    print(i)
