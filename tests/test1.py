
from collections import OrderedDict

from declared import Mark as mark, Declared

class custom(mark):

    collect_into = '_declared_numbers'

    def __call__(self, f):
        self.value = f()
        return self

    def build(self, *args):
        return int(self.value)


class MarkedApp(Declared, extract=custom):

    mark1 = mark2 = custom(value=1)

    @custom()
    def mark3():
        return 2

from util import case

case.assertSequenceEqual(
    MarkedApp._declared_numbers,
    OrderedDict([('mark1', 1), ('mark2', 1), ('mark3', 2)]))
