# declared

Class based declaration.

----------

## Overview

This is a **small** (< 100 SLOC) python module aiming to solve one simple problem:
taking the "special" attributes from the class declaration and forming an `OrderedDict`
out of them (or a couple of `OrderedDict`'s).

That special attributes are recognized by being `Mark` instances and therefore will be called marks.

Supports **"lazy" processing** of the declared marks. To use it, you just declare at least one "lazy" mark
and then call `.process_declared()` from the instance of your class or from the class itself.

Is inspired by the declarations processing in the `django-rest-framework`.

---------

## Examples

Let's define a mark for time:

    from time import strptime
    from declared import Mark

    class Time(Mark):

        collect_into = '_time_marks'

        def __init__(self, value):
            self.value = value

        def build(self, marks, owner):
            return strptime(self.value, '%H:%M')

And then use it:

    from declared import DeclaredMeta

    class DailyRoutine(metaclass=DeclaredMeta):
        breakfast = Time('9:00')
        lunch = Time('12:00')
    
    >>> DailyRoutine._time_marks
    OrderedDict([('breakfast', time.struct_time(...)), ('lunch', time.struct_time(...))])

Not that produced `struct_time` instances are extra useful, it just demonstrates that a mark can be built
(by default `.build()` method returns the mark itself. The passed arguments to `.build()` are:

* `marks`: A list of of all marks
* `owner`: The marks owner (`DailyRoutine` in our example).
           If the lazy processing is used and `.process_declared()` was called from the instance,
           then owner means that instance.

By default marks are collected into the `_declared_marks` attribute, but `Time` class overrides it.
If we had other marks present with a differing value of `collect_into`, than we would get more than one
`OrderedDict`.
           
Instead of using `DeclaredMeta`, you can inherit class from `Declared`, it means the same.

---------

In `django-rest-framework` there is `serializers.SerializerMetaclass` used for the same purposes as `DeclaredMeta`:
it collects `serializers.Field` instances.

Let's imagine that serializers used `DeclaredMeta` instead:
    
    from rest_framework import serializers
    
    class field(Mark):
        collect_into = '_declared_fields'
        
        @classmethod
        def __subclasshook__(cls, C):            # yes, Mark inherits from ABC
            if issubclass(C, serializers.Field):
                return True
            return NotImplemented
    
    class Serializer(metaclass=DeclaredMeta):
        default_mark = field

Notice the `default_mark` attribute that we had to set on the owner class.
If we hadn't define it, `Field` instances would be processed as `Mark`'s not `field`,
and collected into `_declared_marks`.
That's because though we have registered `Field` as a `field` subclass, we can't
access `field`'s attributes from it.
        
Now you won't be able to discriminate (by it's declaration-parsing capabilities)
between our `Serializer` and the original one, from the `rest_framework`).

    class Person(Serializer):
        name = serializers.CharField()
        age = serializers.IntegerField()

    >>> Person._declared_fields
    OrderedDict([('name', CharField()), ('age', IntegerField())])
        


----------------

## Lazy declaration