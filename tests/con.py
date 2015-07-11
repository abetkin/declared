
from declared import Declared, ProcessDeclared

from collections import OrderedDict

# class Processor(object):

import ipdb



# class field(object):
#     
#     is_declared = True
# 
#     def __init__(self, transform):
#         self.transform = transform
# 
#     # def process(self, value):
#     #     return self.transform(value)
# 
#     def process_declared(self, value):
#         result = self.transform(value)
#         # setattr(container, self.attr_name, result)
#         return result
# 

# class List(field):
#
#     def prosess(self, value, container=None)


class Fields(ProcessDeclared):

    @classmethod
    def is_declaration(cls, name, obj):
        return isinstance(obj, type) or getattr(obj, 'transformer', None)

    def evaluate_it(self, data):
        for name, decl in self._declarations.items():
            yield name, decl(data[name])

    def __repr__(self):
        return repr(self.get_declarations())

    # is_declared = False
    # process -> process_declared

    # @classmethod
    # def __subclasshook__(cls, C):
    #     if issubclass(cls, Mark):
    #         return True
    #     return NotImplemented

# ipdb.set_trace()
class fields(Fields):

    name = str
    age = int

    class assistant(Fields):
        name = str
        service = str


class MyJson(ProcessDeclared):

    @classmethod
    def is_declaration(cls, name, obj):
        return name in cls.FIELDS

    def name(obj):
        return obj.name

    def assistant(obj):
        return obj.assistant.name

    FIELDS = ['name', 'assistant']


class Container(Declared):

    declared_types = type,

    name = str
    age = int

    class assistant(Fields):
        name = str
        service = str


con = Container()

# ipdb.set_trace()
res = Fields({'name': 'Reena', 'age': 27,
                'assistant': {
                    'name': 'Kate',
                    'service': 'private',
                }
                
                }, declared_in=con)

myjson = MyJson(con)
# f.__dict__.update(res)



class A(Declared):
    declared_types = int,

    age = 25

class B(A):
    height = 180
