import os
import shutil
class  SearchFile(object):

    def __init__(self,path='.'):
        self._path=path
        self.abspath=os.path.abspath(self._path) # 默认目录
        print("***"+self.abspath)

    def findfile(self,keyword,root):
        filelist=[]
        for root,dirs,files in os.walk(root):
            for name in files:
                filelist.append(os.path.join(root, name))
        print('...........................................')
        dstFiles=[]
        for i in filelist:            
            if os.path.isfile(i):
                if keyword in os.path.split(i)[1]:
                    dstFiles.append(i)
                    # print(i)    # 绝对路径
        return dstFiles

    def __call__(self):
        root = self.abspath   # 把当前工作目录作为工作目录
        # keyword = input('the keyword you want to find:')
        keyword = "副本"
        if(keyword!=""):
           files=self.findfile(keyword, root)  # 查找带指定字符的文件
        #    print(files)
           for file in files:
               os.remove(file)

    def copyFileTo(self,file,path):
        print(file)
        fileName=file.split("\\")
        fileName=fileName[len(fileName)-1]
        postfix=fileName.split(".")
        postfix= postfix[len(postfix)-1]
        if(postfix== "jpg" or postfix=="png"):
            newPath=path+fileName
            shutil.copy(file,newPath)



if __name__ == '__main__':
    search = SearchFile()
    search()
