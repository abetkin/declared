from collections import OrderedDict
from abc import ABCMeta

from six import add_metaclass

class SkipMark(Exception):
    pass

@add_metaclass(ABCMeta)
class Mark(object):

    collect_into = '_declared_marks'

    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def build(self, owner):
        return self


class DeclaredMeta(type):
    '''
    The metaclass collects `Mark` instances from the classdict
    and then removes from the class namespace.
    '''

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        return OrderedDict()

    def __new__(cls, name, bases, namespace):
        extract = namespace.get('__extract__', ())
        to_extract = [Mark]
        if not isinstance(extract, (tuple, list)):
            to_extract.append(extract)
        else:
            to_extract.extend(extract)

        marks_dict = OrderedDict()
        for key, obj in namespace.items():
            if not isinstance(obj, tuple(to_extract)):
                continue
            marks_dict[key] = obj

        klass = super(DeclaredMeta, cls).__new__(cls, name, bases, namespace)
        for key, obj in marks_dict.items():
            if isinstance(obj, Mark):
                collect_into = obj.collect_into
                obj = obj.build(klass)
            else:
                collect_into = Mark.collect_into
                # collect_into = getattr(klass, 'collect_declared_into', None) or Mark.collect_into
            setattr(klass, key, obj)
            if not getattr(klass, collect_into, None):
                setattr(klass, collect_into, OrderedDict())
            getattr(klass, collect_into)[key] = obj
        return klass

    def __init__(cls, *args, **kwds):
        kwds.pop('extract', None)
        super(DeclaredMeta, cls).__init__(*args)


@add_metaclass(DeclaredMeta)
class Declared(object):
    pass
