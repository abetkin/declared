# declared

Class based declarations.

----------

## Overview

**declared** a small (< 100 SLOC) python module aiming to solve one simple problem:
extracting from the class declaration instances of the specified class and forming an `OrderedDict`
out of them, not adding them to class namespace.

**Note:** For those who have used `django-rest-framework`: there you can define fields as attributes of `Serializer` class.
This package may be regarded as the generalized version of that.


Supports **"lazy" processing** of the declared marks. To use it, you just declare at least one "lazy" mark
and then call `.process_declared()` from the instance of your class or from the class itself.

-------

Warning: Only **Python 3** is supported yet.

----------

## Examples

The simplest one: let's extract all numbers.

    from declared import Mark, Declared

    class Int(Mark):
        collect_into = '_ints'
    Int.register(int)
    
    class MyAttrs(Declared, extract=Int):
        a = 1
        b = a + 1
        c = 'not an int'
    
`extract` keyword says marks are `Int` instances (`Mark` is default).          
`collect_into` specifies the attribute name we want to collect the marks into.
    
    >>> MyAttrs._ints
    OrderedDict([('a', 1), ('b', 2)])
    
    >>> MyAttrs.a
    AttributeError: type object 'MyAttrs' has no attribute 'a'
    
As you see, `int` instances were not added to class namespace.

-------

The second example deals with the declaration of the points of time:

    from time import strptime
    from declared import Mark

    class Time(Mark):

        collect_into = '_timepoints'

        def __init__(self, value):
            self.value = value

        def build(self, marks, owner):
            return strptime(self.value, '%H:%M')

And then use it:

    class DailyRoutine(Declared, extract=Time):
        breakfast = Time('9:00')
        lunch = Time('12:00')
    
    >>> DailyRoutine._timepoints
    OrderedDict([('breakfast', time.struct_time(...)), ('lunch', time.struct_time(...))])

Not that produced `struct_time` instances are extra useful, but it demonstrates that a mark can provide a build classmethod
(by default `.build()` method returns the mark itself). The passed arguments to `.build()` are:

* `owner`: The marks owner (`DailyRoutine` in our example).
           If the lazy processing is used and `.process_declared()` was called from the instance,
           then `owner` means that instance.
* `marks_dict`: A dict of all marks


Instead of inheriting from `Declared`, you can write `metaclass=DeclaredMeta`, it means the same.

---------

In `django-rest-framework` there is `serializers.SerializerMetaclass` used for the same purposes as `DeclaredMeta`:
it collects `serializers.Field` instances.

Let's imagine that serializers used `declared` instead:
    
    from rest_framework import serializers
    
    class field(Mark):
        collect_into = '_declared_fields'
        
        @classmethod
        def __subclasshook__(cls, C):
            if issubclass(C, serializers.Field):
                return True
            return NotImplemented
    
    class Serializer(Declared, extract=field):
        pass

Now you could not discriminate (by it's declaration-parsing capabilities)
between our `Serializer` and the original one, from the `rest_framework`).

    class Person(Serializer):
        name = serializers.CharField()
        age = serializers.IntegerField()

    >>> Person._declared_fields
    OrderedDict([('name', CharField()), ('age', IntegerField())])

---------

In the Examples section you [will find](examples.md#django-filters) similar approach used to declare `django` filters.
The role of fields there take [Q](https://docs.djangoproject.com/en/1.7/ref/models/queries/#django.db.models.Q) and
[QuerySet](https://docs.djangoproject.com/en/1.7/ref/models/querysets/#django.db.models.query.QuerySet) objects.
    
---------

Actually, our first "Daily Routine" example can be made [more interesting](examples.md#daily-routine).
Check out the Examples section.

----------------

## Lazy declarations

There are little information usually available at the time of class declaration. So
one time you probably will need lazy declarations. With `declared` you can do that,
providing a function that returns a mark or just a value, and decorating in with `@lazy`:

    class Greeting(Mark):
        collect_into = '_greetings'
        
        def __repr__(self):
            return self.text
    
    class Greetings(Declared, extract=Greeting):
        
        def __init__(self, name):
            self.name = name
        
        @lazy
        def in_english(owner):
            return Greeting(text='Hello, %s' % owner.name)
        
If `DeclaredMeta` finds at least one mark decorated with `@lazy`, it will not process marks. Instead,
it will add `process_declared` callable to the owner class. You can call `.process_declared()` either from class
or an instance - `owner` will be class or instance respectively.

    >>> greetings = Greetings('John')
    >>> greetings._greetings
    AttributeError: 'Greetings' object has no attribute '_greetings'
    >>> greetings.process_declared()
    >>> greetings._greetings
    OrderedDict([('in_english', Hello, John)])

-------

Another [example](examples.md#lazy-declaration) for lazy declarations you can find in the Examples section as a continuation to "Daily Routine".