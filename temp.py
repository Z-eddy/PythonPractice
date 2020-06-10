normalDict={}
normalDict["cda"]="theC"
normalDict["abd"]="theA"
normalDict["b"]="theB"
normalDict["num"]=17.8
# print(normalDict)
for key,val in normalDict.items():
    print(key,val)

from collections import OrderedDict
ordDict=OrderedDict()
ordDict["cda"]="theC"
ordDict["abd"]="theA"
ordDict["b"]="theB"
ordDict["num"]=17.8
# print(ordDict)
for key,val in ordDict.items():
    print(key,val)