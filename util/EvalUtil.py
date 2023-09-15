# -*- coding: utf-8 -*-
# python 3.x
# Filename: EvalUtil.py
# 定义一个EvalUtil工具类实现执行str代码相关的功能
# https://pythonjishu.com/python-eval-exec/


class EvalUtil:
    @staticmethod
    def eval(expression, globals: dict = {}, locals: dict = {}):
        """
        执行指定表达式，并返回结果
        :param expression: 函数表达式
        :param globals: 全局命名空间
        :param locals: 局部命名空间
        :return: 执行结果
        """
        return eval(expression, globals, locals)

    @staticmethod
    def exec(expression, globals: dict = {}, locals: dict = {}):
        """
        执行任何字符串类型的Python代码，但是没有返回值
        :param expression: 任何字符串类型的Python代码
        :param globals: 全局命名空间
        :param locals: 局部命名空间
        """
        exec(expression, globals, locals)


if __name__ == "__main__":
    print(EvalUtil.eval('x + y', locals={'x': 1, 'y': 2}))
    # 定义全局命名空间和本地命名空间
    myGlobals = {'x': 3, 'y': 6, 'z': 0}
    myLocals = {'a': 1, 'b': 2, 'c': 0}
    EvalUtil.exec('z = x + y; c = a + b;', globals=myGlobals, locals=myLocals)
    print(myGlobals.get('z'))
    print(myLocals.get('c'))
