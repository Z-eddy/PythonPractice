n0=5
n1=0
try:
    result=n0/n1
    print("no pass?")#自动跳过了！
    with open("other") as fileObj:#自动跳过了！
        fileObj.read()
except ZeroDivisionError:
    print("devide 0!")
else:
    print("other error")