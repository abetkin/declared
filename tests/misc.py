
from declared import Declared, ProcessDeclared

from collections import OrderedDict

# class Processor(object):

import ipdb



class Fields(ProcessDeclared):

    @classmethod
    def is_declaration(cls, name, obj):
        return isinstance(obj, type) or getattr(obj, 'transformer', None)

    def evaluate_it(self, data):
        for name, decl in self._declarations.items():
            yield name, decl(data[name])

    def __repr__(self):
        return repr(self.get_declarations())


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

res = Fields({'name': 'Reena', 'age': 27,
                'assistant': {
                    'name': 'Kate',
                    'service': 'personal image',
                }
                
                }, declared_in=con)

myjson = MyJson(con)


