#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @File : tool.py
# @Project : computer
# @Software: PyCharm
# @Author : 大红昕
# @Time : 2020/6/14 11:51


class ToolFunction:
    def __init__(self):
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
            context.append("NOP")
            return context
        context.append(line[:space].strip())
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
        :return: 包含汇编代码的列表
        """
        context = list()
        try:
            with open(fileName, mode="r", encoding="ANSI") as f:
                for line in f.readlines():
                    if line.strip():
                        context.append(line.strip("\n"))
        except FileNotFoundError:
            print("请检查文件路径已经文件扩展名是否正确！")
        else:
            return context

    @staticmethod
    def replace_char(string, char, *args):
        """
        修改特定位置的字符
        :param string: 原字符串
        :param char: 修改后的字符
        :param *args: 要修改的位置,不定长参数
        :return:
        """
        string = list(string)
        for i in args:
            string[i] = char
        return ''.join(string)