from collections import OrderedDict
from abc import ABCMeta

from six import add_metaclass

class SkipMark(Exception):
    pass

import ipdb

def is_mark(obj):
    obj.is_mark = True
    return obj

@add_metaclass(ABCMeta)
class Mark(object):

    collect_into = '_declared_marks'

    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def build_mark(self, owner):
        return self


class DeclaredMeta(ABCMeta):
    '''
    The metaclass collects `Mark` instances from the classdict
    and then removes from the class namespace.
    '''

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        return OrderedDict()

    def __new__(cls, name, bases, namespace):
        extract = namespace.get('__extract__', ())
        # ipdb.set_trace()
        to_extract = [Mark]
        if not isinstance(extract, (tuple, list)):
            to_extract.append(extract)
        else:
            to_extract.extend(extract)

        marks_dict = OrderedDict()
        for key, obj in namespace.items():
            if not isinstance(obj, tuple(to_extract)) and not getattr(obj, 'is_mark', None):
                continue
            obj.attr_name = key
            marks_dict[key] = obj

        # namespace['process_declared']

        klass = super(DeclaredMeta, cls).__new__(cls, name, bases, namespace)
        for key, obj in marks_dict.items():
            if isinstance(obj, Mark):
                collect_into = obj.collect_into
                # obj = obj.build(klass)
            else:
                collect_into = Mark.collect_into
                # collect_into = getattr(klass, 'collect_declared_into', None) or Mark.collect_into
            # ipdb.set_trace()
            build_mark = getattr(obj, 'build_mark', None)
            if build_mark:
                obj = build_mark(klass)
                # print 'built:', obj
            setattr(klass, key, obj)
            if not getattr(klass, collect_into, None):
                setattr(klass, collect_into, OrderedDict())
            getattr(klass, collect_into)[key] = obj
        return klass

    def __init__(cls, *args, **kwds):
        kwds.pop('extract', None)
        super(DeclaredMeta, cls).__init__(*args)



# def process_declared(container, *args, **kwargs):
#     for key in self.lazy:
#         self.marks_dict[key] = self.marks_dict[key].func(self.owner)
#     collect_into = self.mark_type.collect_into
#     setattr(self.owner, collect_into, OrderedDict())
#     for key, mark in self.marks_dict.items():
#         try:
#             built = self.mark_type.build(mark, self.owner, self.marks_dict)
#         except SkipMark:
#             continue
#         setattr(self.owner, key, built)
#         getattr(self.owner, collect_into)[key] = built

# class ProcessDeclared:
#
#     def __get__(self, instance, klass):
#         if instance:
#             return instance._process_declared
#         return process_declared
#
# 
# 
# @add_metaclass(DeclaredMeta)
# class Declared(object):
#     
#     def _process_declared(self, )
