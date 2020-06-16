import re
#构建检测的规则
ruleStr=r".*"
ruleObj=re.compile(ruleStr,re.DOTALL)   #编译时加入re.DOTALL可以匹配一切字符,否则换行符无法匹配到
#具体检测的值
message="the phone is \n(028)1234567."
mo=ruleObj.search(message)
if(mo):
    print(mo.group())
else:
    print("can't find")
