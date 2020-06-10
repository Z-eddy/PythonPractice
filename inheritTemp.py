from theModule import Dog

class SpottyDog(Dog):
    def __init__(self,name,age,spottyNum):
        super().__init__(name,age)
        self.spottyNum_=spottyNum
    def spottyN(self):
        return self.spottyNum_