import abc
from functools import reduce
import operator
from django.db.models.query import Q, QuerySet
from declared import DeclaredMeta, Declared


class DeclaredFilters(Declared):
    declared_types = Q,
    
    @classmethod
    def build_declaration(cls, obj):
        if isinstance(obj, Q):
            return afilter(obj)
        return obj


class afilter(object):
    
    is_declared = True
    
    def __init__(self, obj):
        self.obj = obj
    
    def process_declared(self, qs): # -> result
        if isinstance(self.obj, Q):
            return qs.filter(self.obj)
        assert callable(self.obj)
        return self.obj(qs)

from collections import OrderedDict

class ReducedFilters(DeclaredFilters):

    @classmethod
    def process_declared(cls, qs):
        self = cls()
        # with ipdb.launch_ipdb_on_exception():
        result = OrderedDict()
        for attr, mark in self._declarations.items():
            value_out = mark.process_declared(qs)
            result[attr] = value_out
        self.__dict__.update(result)
        self.filters = result
        return self # _odict

    @property
    def queryset(self):
        return reduce(self.operation, self.filters.values())


class qand(ReducedFilters):
    operation = operator.and_

class qor(ReducedFilters):
    operation = operator.or_


class CascadeFilter(DeclaredFilters):

    @classmethod
    def process_declared(cls, objects):
        self = cls()
        result = OrderedDict()
        for attr, mark in self._declarations.items():
            processed = mark.process_declared(objects)
            if isinstance(processed, QuerySet):
                objects = processed
            else:
                objects = processed.queryset
            result[attr] = processed
        self.__dict__.update(result)
        self.filters = result
        self.queryset = objects
        
        return self
