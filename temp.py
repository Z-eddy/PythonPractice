import re
#构建检测的规则
ruleStr=r"[0-9]+"
ruleObj=re.compile(ruleStr)
#具体检测的值
message="the phone is (028)1234567."
mo=ruleObj.findall(message)
if(mo):
    print(mo)
else:
    print("can't find")
