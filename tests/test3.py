from collections import OrderedDict
from declared import Mark, Declared

class serializers_Field:
    pass

class field(Mark):
    collect_into = '_declared_fields'

    @classmethod
    def __subclasshook__(cls, C):            # yes, Mark inherits from ABC
        if issubclass(C, serializers_Field):
            return True
        return NotImplemented


from util import case

class Person(Declared, extract=field):
    name = serializers_Field()
    age = serializers_Field()

case.assertSequenceEqual(
    list(Person._declared_fields.keys()),
    ['name', 'age'])
