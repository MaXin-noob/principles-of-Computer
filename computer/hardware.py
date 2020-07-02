#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @File : hardware.py
# @Project : computer
# @Software: PyCharm
# @Author : 大红昕
# @Time : 2020/7/1 19:12

from abc import ABCMeta, abstractmethod


# 底层硬件
class Hardware(metaclass=ABCMeta):
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

    @abstractmethod
    def PLA(self):
        """
        译码器,须在子类实现
        :return:
        """
        pass
