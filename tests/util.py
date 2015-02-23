import unittest

class Case(unittest.TestCase):
    def runTest(self):
        raise NotImplementedError()

case = Case('runTest')
