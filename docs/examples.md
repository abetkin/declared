# Examples

The examples collection.

---

## Daily Routine

Let's make a more sophisticated class for daily routine. Here is what it finally will be able to do:

    class MyDailyRoutine(DailyRoutine):
        breakfast = '9:00'
        lunch = '12:00'
        dinner = '-1:33'     # invalid data

    >>> MyDailyRoutine._timepoints
    OrderedDict([('breakfast', 9:0), ('lunch', 12:0)])

Let's start with writing a custom class for a time interval (with a modulo of a day):

    class ParseError(Exception):
        pass

    class Time:
        def __init__(self, hour, min):
            self.hour = hour
            self.min = min

        @classmethod
        def parse(cls, value):
            try:
                value = strptime(value, '%H:%M')
            except ValueError:
                raise ParseError(value)
            return cls(value.tm_hour, value.tm_min)

        def __repr__(self):
            return '%s:%s' % (self.hour, self.min)

        def __add__(self, other):
            if isinstance(other, str):
                try:
                    other = self.parse(other)
                except ParseError:
                    return NotImplemented
            elif not isinstance(other, Time):
                return NotImplemented
            min = self.min + other.min
            hour, min = min // 60, min % 60
            hour = (self.hour + other.hour + hour) % 24
            return self.__class__(hour, min)
            
As you understand, you can add time intervals:

```python
>>> Time(1, 34) + '23:55'
1:29
```

Then we are going to define a class for the respective mark. We want it to understand strings and `Time`
instances as well:

    from declared import SkipMark

    class time(Mark):
        collect_into = '_timepoints'

        def __init__(self, value):
            self.value = value

        def build(mark, marks, owner):
            if isinstance(mark, Time):
                return mark
            if isinstance(mark, str):
                try:
                    return Time.parse(mark)
                except ParseError:
                    raise SkipMark
            return Time.parse(mark.value)

    time.register(str)
    time.register(Time)

Then we will specify the default class for marks, so that it would know what to do with those strings:

    class DailyRoutine(metaclass=DeclaredMeta):
        default_mark = time
        
Now we are done. We can write our daily routine classes and inherit it from `DailyRoutine`.

-----------------------

## Lazy declaration

Let's try to write a daily routine with "floating" time of getting up. Here is how
we can do it using lazy declarations:

    from declared import Declared, declare

    class MyDailyRoutine(Declared):
        
        def __init__(self, get_up):
            if isinstance(get_up, str):
                get_up = Time.parse(get_up)
            self.get_up = get_up
        
        @declare(time)
        def breakfast(self):
            return self.get_up + '0:30'
        
        @declare(time)
        def lunch(self):
            return self.get_up + '3:30'
            
    >>> routine = MyDailyRoutine('8:30')
    >>> routine.process_declared()
    >>> routine._timepoints
    OrderedDict([('breakfast', 9:0), ('lunch', 12:0)])

------

## Django filters

In this example we will aggregate (declaratively) filters from
[Q](https://docs.djangoproject.com/en/1.7/ref/models/queries/#django.db.models.Q) and
[QuerySet](https://docs.djangoproject.com/en/1.7/ref/models/querysets/#django.db.models.query.QuerySet) objects.

Let's aggree that an object can be considered a filter, if it defines a `filter` callable, that takes iterable as a parameter
(usually, a queryset)
and returns iterable. The `Q` objects doesn't define such an interface, also, we probably would want to change it's `repr()`
behavior. Let's write a wrapper:

    class qobj:
        def __init__(self, qobj):
            self.qobj = qobj

        def filter(self, queryset):
            return queryset.filter(self.qobj)

        def __repr__(self):
            pairs = ['%s=%s' % item for item in self.qobj.children]
            return 'Q: %s' % ', '.join(pairs)

It's string representation got better:
            
    from django.db.models.query import Q, QuerySet

    >>> Q(key='value')
    <django.db.models.query_utils.Q at 0x7f5771937400>
    >>> qobj(Q(key='value'))
    Q: key=value

Then we define the filter mark class:

    from declared import Mark, Declared

    class qsfilter(Mark):
        collect_into = '_declared_filters'

        func = None
        
        def __init__(self, description, func=None):
            self._description = description
            self.func = func
        
        def __repr__(self):
            return self._description
        
        def __call__(self, func):
            self.func = func
            return self

        def filter(self, queryset):
            return self.func(queryset)

        def build(mark, *args):
            if isinstance(mark, Q):
                return qobj(mark)
            return mark

    qsfilter.register(Q)

Here is how we can declare a container with filters with it:

    from declare import Declared

    class Filter(Declared):
        default_mark = qsfilter
    
        @qsfilter('take the first element')
        def take_first(queryset):
            return queryset[0]
        
        text = Q(question_text__icontains='some_text')
    
    >>> filters = Filters._declared_filters
    >>> filters
    OrderedDict([('take_first', take the first element), ('text', Q: question_text__icontains=some_text)])
    >>> filters['take_first'].filter(Question.objects.all())
    <Question: Question object>

`Question` is a django model taken from the official [tutorial](https://docs.djangoproject.com/en/1.7/intro/tutorial01/#creating-models).

That was similar to what we've done before and not very interesting. Now let's try to aggregate filters.
For example, here is what can be done for combination with OR & AND operations:

    class Filter(qor):
    
        filter1 = qsfilter(..)
        filter2 = qsfilter(..)
        q1 = Q(..)
    
        class Nested(qand):
            filter1 = Q(..)
            filter4 = qsfilter(..)
            # ...

`Nested` will combine `filter3` and `filter4` with AND operation. `Filter` will combine `filter1`, `filter2`, `q1` and `Nested` with OR.
The nesting depth isn't limited. Looks pretty nice, doesn't it?

Also I think we will need a cascading filter: the one that will just apply filters to queryset one after another.

    class filters_sequence(CascadeFilter):
        filter1 = qsfilter(..)
        filter2 = Q(..)
        # ...

For the filter nesting to work we need `qor`, `qand` and `CascadeFilter` to be filters themselves.
But they are classes...

Don't worry, we have metaclasses at our service:

    from declared import DeclaredMeta

    @qsfilter.register
    class FiltersDeclaredMeta(DeclaredMeta, abc.ABCMeta):
        def __repr__(cls):
            return ', '.join(cls._declared_filters.keys())

    class DeclaredFilters(metaclass=FiltersDeclaredMeta):
        default_mark = qsfilter
        
        @classmethod
        def filter(cls):
            raise NotImplementedError()

Now, since `FiltersDeclaredMeta` is registered as `qsfilter`, `DeclaredFilters` will be considered an instance of `qsfilter`.
As you can see, `DeclaredFilters` defines `.filter()` callable.

Let's write the implementations:

    class ReducedFilters(DeclaredFilters):
        @classmethod
        def filter(cls, queryset):
            filters = [f.filter(queryset)
                       for f in cls._declared_filters.values()]
            if filters:
                return reduce(cls.operation, filters)
            return queryset

    import operator

    class qand(ReducedFilters):
        operation = operator.and_
        
    class qor(ReducedFilters):
        operation = operator.or_
        
    class CascadeFilter(DeclaredFilters):
        @classmethod
        def filter(cls, objects=None):
            if objects is None:
                objects = cls.objects
            for f in cls._declared_filters.values():
                objects = f.filter(objects)
            return objects

That's all. Try it yourself.