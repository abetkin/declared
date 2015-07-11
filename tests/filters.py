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
    
    is_declaration = True
    
    def __init__(self, obj):
        self.obj = obj
    
    def __call__(self, qs):
        if isinstance(self.obj, Q):
            return qs.filter(self.obj)
        assert callable(self.obj)
        return self.obj(qs)

from collections import OrderedDict

class ReducedFilters(DeclaredFilters):

    @property
    def queryset(self):
        filters = self.get_declarations()
        return reduce(self.operation, filters)


class qand(ReducedFilters):
    operation = operator.and_

class qor(ReducedFilters):
    operation = operator.or_


class CascadeFilter(DeclaredFilters):

    def evaluate_it(self, queryset):
        for name, filtr in self._declarations.items():
            filtered = filtr.evaluate(queryset)
            yield name, filtered
            queryset = filtered if isinstance(filtered, QuerySet) \
                                else filtered.queryset