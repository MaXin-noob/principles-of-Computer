#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @File : tool.py
# @Project : 计算机模拟机
# @Software: PyCharm
# @Author : 大红昕
# @Time : 2020/6/14 11:51
note = {
    "ADD": "0000 1100",
    "SUB": "0000 1000",
    "LDI": "1110"
}


class ToolFunction:
    def __init__(self):
        pass

    @staticmethod
    def compile(instruction):
        """
        将汇编代码编译成机器码
        :param instruction: 分离后的汇编代码
        :return: 机器码
        """
        pass

    @staticmethod
    def analyze(line):
        """
         分离指令与操作数
        :param line: 代码内容
        :return: 分离后的数据，以列表形式返回
        """
        context = []
        line = line.upper()
        space = line.find(" ")
        if space == -1:
            context.append("nop")
            return context
        order = line[:space]
        context.append(order.strip())
        data = line[space:]
        comma = data.find(",")
        if comma == -1:
            context.append(data.strip())
            return context
        parameter_1 = data[:comma]
        context.append(parameter_1.strip())
        parameter_2 = data[comma + 1:]
        context.append(parameter_2.strip())
        return context

    @staticmethod
    def readFile(fileName):
        """
        :param fileName: 汇编指令代码文件
        :return: 每一行行号以及汇编代码构建成的字典
        """
        context = dict()
        try:
            with open(fileName, mode="r", encoding="ANSI") as f:
                for num, line in enumerate(f.readlines()):
                    context[hex(num + 1)] = line.strip()
        except FileNotFoundError:
            print("请检查文件路径已经文件扩展名是否正确！")
        else:
            return context
