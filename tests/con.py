
from declared import Declared

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


class Fields(Declared):


    def evaluate_it(self, data):
        for name, decl in self._declarations.items():
            # ipdb.set_trace()
            yield name, decl(data[name])

    def __repr__(self):
        return self.get_declarations()

    # is_declared = False
    # process -> process_declared

    # @classmethod
    # def __subclasshook__(cls, C):
    #     if issubclass(cls, Mark):
    #         return True
    #     return NotImplemented

# ipdb.set_trace()
class fields(Declared):

    name = str
    age = int

    class assistant(Fields):
        name = str
        service = str

        # is_mark = True

    # assistant = is_mark(assistant)


f = fields()
res = Fields.process_object(f, {'name': 'Reena', 'age': 27,
                'assistant': {
                    'name': 'Kate',
                    'service': 'private',
                }
                
                })
# f.__dict__.update(res)
