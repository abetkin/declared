from copy import copy
from collections import OrderedDict
from abc import ABCMeta

class SkipMark(Exception):
    pass

class Mark(metaclass=ABCMeta):

    collect_into = '_declared_marks'

    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    @classmethod
    def build(cls, mark, owner, marks_dict):
        # can raise SkipMark
        return mark


class lazy(Mark):

    def __init__(self, func):
        self.func = func


class DeclaredMeta(type):
    '''
    The metaclass collects `Mark` instances from the classdict
    and then removes from the class namespace.
    '''

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        return OrderedDict()

    def __new__(cls, name, bases, namespace, extract=Mark):
        cls.extract_type = extract
        marks_dict = OrderedDict()
        for key, obj in namespace.items():
            if not isinstance(obj, (extract, lazy)):
                continue
            # make clones if necessary so that all marks
            # were different objects
            if obj in marks_dict.values():
                obj = copy(obj)
            marks_dict[key] = obj

        # clear the namespace
        for _name in marks_dict:
            del namespace[_name]

        lazy_marks = [k for k,v in marks_dict.items()
                      if isinstance(v, lazy)]
        if lazy_marks:
            def process_declared(owner):
                for name in lazy_marks:
                    marks_dict[name] = marks_dict[name].func(owner)
                return cls._process_declared(owner, marks_dict)

            namespace['process_declared'] = process_declared

        klass = type.__new__(cls, name, bases, namespace)
        if not lazy_marks:
            cls._process_declared(klass, marks_dict)

        return klass

    def __init__(cls, *args, extract=Mark):
        return type.__init__(cls, *args)

    @classmethod
    def _process_declared(cls, owner, marks_dict):
        collect_into = cls.extract_type.collect_into
        setattr(owner, collect_into, OrderedDict())
        for key, mark in marks_dict.items():
            built = cls.extract_type.build(mark, owner, marks_dict)
            getattr(owner, collect_into)[key] = built

class Declared(metaclass=DeclaredMeta):
    pass
