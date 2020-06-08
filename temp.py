keyValue={"key":"theKey","val0":123,"val1":123}
keyValue["add"]=12.59

for key in set(keyValue.values()):    #默认只访问键名
    print(key)