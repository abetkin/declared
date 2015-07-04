
from declared import Mark, Declared, is_mark

# class Processor(object):

import ipdb



class field(Mark):

    def __init__(self, transform):
        self.transform = transform

    # def process(self, value):
    #     return self.transform(value)

    def process(self, value):
        result = self.transform(value)
        # setattr(container, self.attr_name, result)
        return result


# class List(field):
#
#     def prosess(self, value, container=None)


class Fields(Declared):

    # @classmethod
    @classmethod
    def build_mark(cls, owner):
        # can raise SkipMark
        # print 'to build:', mark
        return cls()

    # @classmethod
    def process(self, data):
        with ipdb.launch_ipdb_on_exception():
            result = {}
            for attr, mark in self._declared_marks.items():
                # ipdb.set_trace()
                value_in = data[attr]
                value_out = mark.process(value_in)
                result[attr] = value_out
            self.__dict__.update(result)
            return self # _odict
                # setattr(container, attr, value_out)

    # is_declared = False
    # process -> process_declared

    # @classmethod
    # def __subclasshook__(cls, C):
    #     if issubclass(cls, Mark):
    #         return True
    #     return NotImplemented

# ipdb.set_trace()
class fields(Declared):

    name = field(str)
    age = field(int)


    class assistant(Fields):
        name = field(str)
        service = field(str)

        is_mark = True

    # assistant = is_mark(assistant)


f = fields()
res = Fields.process.__func__(f, {'name': 'Reena', 'age': 27,
                'assistant': {
                    'name': 'Kate',
                    'service': 'private',
                }
                
                })
# f.__dict__.update(res)
