from collections import OrderedDict
from abc import ABCMeta

from six import add_metaclass

# import ipdb

from itertools import chain

class DeclaredMeta(ABCMeta):

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        return OrderedDict()

    def __new__(cls, name, bases, namespace):

        @classmethod
        def _is_declaration(cls, name, obj):
            declared_types = getattr(cls, 'declared_types', ())
            if isinstance(obj, declared_types):
                return True
            if hasattr(cls, 'is_declaration') and cls.is_declaration(name, obj):
                return True
            return getattr(obj, '__declaration__', None)

        namespace['_is_declaration'] = _is_declaration
        klass = super(DeclaredMeta, cls).__new__(cls, name, bases, namespace)
        
        declarations_dict = OrderedDict()
        for key, obj in namespace.items():
            if not klass._is_declaration(key, obj):
                continue
            # obj.attr_name = key
            declarations_dict[key] = obj

        klass._declarations = OrderedDict()
        for key, obj in declarations_dict.items():
            build = getattr(klass, 'build_declaration', None)
            if build:
                obj = build(obj)
            else:
                build = getattr(obj, 'build_declaration', None)
                if build:
                    obj = build(klass)
            klass._declarations[key] = obj
        return klass


@add_metaclass(DeclaredMeta)
class Declared(object):
    pass


class ProcessDeclared(Declared):
    __declaration__ = True
    
    def __init__(self, *args, **kw):
        declared_in = kw.pop('declared_in', None)
        if declared_in:
            filter_func = lambda key: self._is_declaration(*key)
            self._declarations = OrderedDict(
                filter(filter_func, declared_in._declarations.items())
            )
        evaluate_it = list(self.evaluate_it(*args, **kw))
        self.__dict__.update(evaluate_it)
        if declared_in:
            declared_in.__dict__.update(evaluate_it)
    
    def evaluate_it(self, *args, **kw):
        '''default implementation
        '''
        for name, decl in self._declarations.items():
            yield name, decl(*args, **kw)

    def get_declarations(self):
        def items():
            for name in self._declarations:
                yield name, getattr(self, name)
        return OrderedDict(items())