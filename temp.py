from theModule import getFormattedName
import unittest

class nameTest(unittest.TestCase):  #通过继承TestCase
    def testFirstLastName(self):
        name=getFormattedName("jian","que")
        self.assertEqual(name,"Jian Que")

unittest.main()
