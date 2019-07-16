from unittest import TestCase

# from ..validate import *

class TestValidate(TestCase):
    def testIsString(self):
        s = "hi"
        self.assertTrue(isinstance(s, str))
