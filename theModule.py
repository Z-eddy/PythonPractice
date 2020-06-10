class Dog():
    def __init__(self, name, age):
        self.name_ = name
        self.age_ = age

    def sit(self):
        print(self.name_+" is sit")

    def petAge(self):
        print("the age is:"+str(self.age_))
    
    def setAge(self,age):
        self.age_=age

    def readAge(self):
        return self.age_

num=9.3