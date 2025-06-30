import os
import shutil


class SearchCopyFile(object):
    def __init__(self, origiPath, purposePath):
        self._origiPath = origiPath
        self._purposePath = purposePath
        self.absOrigiPath = os.path.abspath(self._origiPath)
        self.absPurposePath = os.path.abspath(self._purposePath)
        # 创建输出目录（如果不存在）
        os.makedirs(purposePath, exist_ok=True)

    # 查找txt
    def findFiles(self):
        filelist = []
        for root, dirs, files in os.walk(self._origiPath):
            for name in files:
                if name.endswith('.txt'):
                    filelist.append(os.path.join(root, name))
        return filelist

    def copyFile(self, file, path):
        fileName = file.split("\\")
        fileName = fileName[len(fileName) - 1]
        newPath = self._purposePath + '\\' + fileName
        shutil.copy(file, newPath)
        print(file, " copy done")

    def do(self):
        files = self.findFiles()
        for file in files:
            self.copyFile(file, self._purposePath)


if __name__ == '__main__':
    search = SearchCopyFile("T:\\story","T:\\storyOut")
    search.do()
