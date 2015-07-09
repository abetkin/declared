from collections import OrderedDict
from abc import ABCMeta

from six import add_metaclass

import ipdb


class DeclaredMeta(ABCMeta):
    '''
    The metaclass collects `Mark` instances from the classdict
    and then removes from the class namespace.
    '''

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        return OrderedDict()

    def __new__(cls, name, bases, namespace):
        klass = super(DeclaredMeta, cls).__new__(cls, name, bases, namespace)
        declared_types = getattr(klass, 'declared_types', ())
        marks_dict = OrderedDict()
        for key, obj in namespace.items():
            if not isinstance(obj, tuple(declared_types)) \
                    and not getattr(obj, 'is_declaration', None):
                continue
            obj.attr_name = key
            marks_dict[key] = obj

        
        klass._declarations = OrderedDict()
        for key, obj in marks_dict.items():
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
    
    is_declaration = True
    
    # @classmethod
    # def evaluate(cls, *args, **kw):
    #     return cls(*args, **kw)
    # 
    def filter_declarations(self, declarations):
        return declarations
    
    def __init__(self, *args, **kw):
        # ipdb.set_trace()
        declarations_from = kw.pop('declarations_from', None)
        if declarations_from: # declared_in ?
            self._declarations = declarations_from._declarations
        self._declarations = self.filter_declarations(self._declarations)
        evaluate_it = self.evaluate_it(*args, **kw)
        self.__dict__.update(evaluate_it)
    
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
