import re
#构建检测的规则
ruleStr=r"[\(]?(\d{3})[\)]?[._-]?(\d{7})"
ruleObj=re.compile(ruleStr)
#具体检测的值
message="the phone is (028)1234567."
mo=ruleObj.search(message)
if(mo):
    print(mo.groups())  #.groups返回python的元组
else:
    print("can't find")
