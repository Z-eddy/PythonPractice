import os

dirPath=r"D:\各种学习\语言\人工智能\万门大学\Python版"
# dirPath = r"C:\Users\Administrator\Desktop\temp\测试文件"
files = os.listdir(dirPath)
for fileName in files:
    index = fileName.find(".ts")
    if index == -1:
        newName = fileName+".ts"
        os.rename(dirPath+"\\"+fileName, dirPath+"\\"+newName)
