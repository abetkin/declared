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
                    and not getattr(obj, 'is_declared', None):
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
    
    @classmethod
    def instantiate(cls, *args, **kw):
        return cls(*args, **kw)
    





        # declarations = declarations_from._declarations
        # declarations = self._filter_declarations(declarations)
        # self._declarations = declarations
    
    def _filter_declarations(self, declarations):
        return declarations
    
    # def as_dict(self):
    #     raise NotImplementedError
    # 
    # def __repr__(self):
    #     return repr(self.as_dict())
    
    @classmethod
    def process_object(cls, obj, *args, **kwargs):
        inst = cls(declarations_from=obj)
        result = inst.process_declared(*args, **kwargs)
        obj.__dict__.update(result.as_dict())
        

class Instantiate(object):
    '''A mixin.
    '''
    
    is_declaration = True
    
    @classmethod
    def instantiate(cls, *args, **kw):
        return cls(*args, **kw)
    
    def __init__(self, *args, **kw):
        declarations_from = kw.pop('declarations_from')
    
    def process_declaration(self, current, processed, _all):

        qs = processed.values()[-1]
        # return super(GenericDeclared, self).process_mark(mark, processed, marks)
        # 
