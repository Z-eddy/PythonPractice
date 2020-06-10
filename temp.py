fileName="./temp/piDigits.txt"
with open(fileName,"a") as fileObj:#r w r+ a四种模式,只能写入字符串
    fileObj.write("\nthis append text!")