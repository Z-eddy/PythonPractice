class Dog():
    def __init__(self, name, age):
        self.name_ = name
        self.age_ = age

    def getName(self):
        return self.name_


def foo(numA, numB):
    val = 10
    val += numA + numB
    return val
