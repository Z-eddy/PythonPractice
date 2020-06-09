def foo(val=88):
    """foo函数定义"""   #文档字符串注释
    return ("hello "+str(val)).title()

ms=foo(99)
print(ms)