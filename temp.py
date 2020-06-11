import unittest
from theModule import Dog

class TestDog(unittest.TestCase):
    def testName(self):
        myPet=Dog("nameA",2)
        li=["nameB","nameA"]
        self.assertIn(myPet.getName(),li)

unittest.main()
