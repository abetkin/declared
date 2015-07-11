from collections import OrderedDict
from abc import ABCMeta

from six import add_metaclass

import ipdb


'''FIX: is_declaration on container
'''

class DeclaredMeta(ABCMeta):
    '''
    The metaclass collects `Mark` instances from the classdict
    and then removes from the class namespace.
    '''

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        return OrderedDict()


    # TODO remove is_declaration attr
    def __new__(cls, name, bases, namespace):
        klass = super(DeclaredMeta, cls).__new__(cls, name, bases, namespace)
        declared_types = getattr(klass, 'declared_types', ())
        declared_types = tuple(declared_types)
        marks_dict = OrderedDict()
        for key, obj in namespace.items():
            if not isinstance(obj, declared_types) and \
                    not klass.is_declaration(obj):
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
    
    def filter_declarations(self, declarations):
        return declarations
    
    def __init__(self, *args, **kw):
        declared_in = kw.pop('declared_in', None)
        if declared_in:
            self._declarations = declared_in._declarations
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
