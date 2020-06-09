class Dog():
    def __init__(self, name, age):
        self.name_ = name
        self.age_ = age

    def sit(self):
        print(self.name_+" is sit")

    def petAge(self):
        print("the age is:"+str(self.age_))


myDog = Dog("nameA",3)
print(myDog.name_,myDog.age_)
myDog.sit()
myDog.petAge()
