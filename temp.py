import json

dataNum=[3,2,1,4,6,3]
fileName="testJson.json"
with open(fileName,"w") as jsObj:
    json.dump(dataNum,jsObj)

with open(fileName,"r") as jsObj:
    data=json.load(jsObj)
    print(data)