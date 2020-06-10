with open("./temp/piDigits.txt") as piObj:
    i=0
    for line in piObj:  #piObj.readlines(0) 从0行开始读取
        print(line.strip()+" line:"+str(i))
        i+=1
