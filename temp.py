from theModule import getFormattedName
import unittest

class nameTest(unittest.TestCase):  #通过继承TestCase
    def testFirstLastName(self):    #只有以test开头才会运行
        name=getFormattedName("jian")
        self.assertEqual(name,"ian Que")

    def testFirstLastName(self):    #只有以test开头才会运行
        name=getFormattedName("jian","que")
        self.assertEqual(name,"Jian Que")

unittest.main()
