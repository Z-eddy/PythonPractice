import unittest
from theModule import Dog

class TestDog(unittest.TestCase):
    def setUp(self):
        self.myPet_=Dog("nameA",2)
        self.li_=["nameB","nameA"]

    def testName(self):
        self.assertIn(self.myPet_.getName(),self.li_)

unittest.main()
