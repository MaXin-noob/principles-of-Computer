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
        self.R0 = 0x000F
        self.R1 = 0x000F
        self.R2 = 0x000F
        self.R3 = 0x000F
        self.R4 = 0x000F
        self.R5 = 0x000F
        self.R6 = 0x000F
        self.R7 = 0x000F
        # 特殊寄存器
        self.PC = 0x000F  # 程序计数器
        self.BUS = 0x000F  # 数据总线
        self.SR = 0x000F  # 源操作数寄存器
        self.DR = 0x000F  # 目的操作数寄存器
        self.MAR = 0x000F
        self.MDR = 0x000F
        self.IMAR = 0x000F
        self.IMDR = 0x000F
        # 控制存储器
        self.control_memory = {}
        # 内存
        self.memory = {}

    @abstractmethod
    def PLA(self):
        """
        译码器,须在子类实现
        :return:
        """
        pass

    @abstractmethod
    def run(self):
        """
        程序运行，子类实现
        :return:
        """
        pass
