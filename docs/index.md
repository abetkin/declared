# declared

Class based declarations.

----------

## Overview

This is a **small** (< 100 SLOC) python module aiming to solve one simple problem:
taking the "special" attributes from the class declaration and forming an `OrderedDict`
out of them (or a couple of `OrderedDict`'s).

That special attributes are recognized by being `Mark` instances and therefore will be called marks.

Supports **"lazy" processing** of the declared marks. To use it, you just declare at least one "lazy" mark
and then call `.process_declared()` from the instance of your class or from the class itself.

Inspired by the declarations processing in the `django-rest-framework`.

---------

Warning: Only **Python 3** is supported yet.

----------

## Examples

Let's define a mark for a time point:

    from time import strptime
    from declared import Mark

    class Time(Mark):

        collect_into = '_timepoints'

        def __init__(self, value):
            self.value = value

        def build(self, marks, owner):
            return strptime(self.value, '%H:%M')

And then use it:

    from declared import DeclaredMeta

    class DailyRoutine(metaclass=DeclaredMeta):
        breakfast = Time('9:00')
        lunch = Time('12:00')
    
    >>> DailyRoutine._timepoints
    OrderedDict([('breakfast', time.struct_time(...)), ('lunch', time.struct_time(...))])

Not that produced `struct_time` instances are extra useful, but it demonstrates that a mark can provide a build method
(by default `.build()` method returns the mark itself). The passed arguments to `.build()` are:

* `marks`: A list of of all marks
* `owner`: The marks owner (`DailyRoutine` in our example).
           If the lazy processing is used and `.process_declared()` was called from the instance,
           then `owner` means that instance.

By default marks are collected into the `_declared_marks` attribute, but the `Time` class overrides it.
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
If we hadn't define it, `Field` instances would be processed as `Mark`, not `field`,
and collected into `_declared_marks`.
That's because though we have registered `Field` as a `field` subclass (with `abc`), we can't
access `field`'s attributes from it.
        
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

**Note:** Probably, supporting a custom attribute (specified with `collect_into`) to store the declared marks
is an unneeded complication. It may be taken away in future.

----------------

## Lazy declarations

There are little information usually available at the time of class declaration. So
one time you probably will need lazy declarations. With `declared` you can do that,
providing a function that returns a mark or just a value, and decorating in with `@declare()`:

    class Greeting(Mark):
        collect_into = '_greetings'
        
        def __repr__(self):
            return self.text
    
    class Greetings(Declared):
        
        def __init__(self, name):
            self.name = name
        
        @declare()
        def in_english(owner):
            return Greeting(text='Hello, %s' % owner.name)
        
If `DeclaredMeta` finds at least one mark declared in such way, it will not process marks. Instead,
it will add `.process_declared()` method to the owner class. Marks can be as lazy as you want: you will
call `.process_declared()` yourself:

    >>> greetings = Greetings('John')
    >>> greetings._greetings
    AttributeError: 'Greetings' object has no attribute '_greetings'
    >>> greetings.process_declared()
    >>> greetings._greetings
    OrderedDict([('in_english', Hello, John)])

`.process_declared()` is a regular method, so if you want to call it from class, not instance, you would do

```python
Klass.process_declared(Klass)
```

You can also specify the mark class with the first argument to the decorator: `@declare(Greeting)`. If that class defines a `.build()`
method, then the lazily returned value will be built with it. That could help solve the problem that we solved previously with
setting the `default_mark` attribute on the instance.

Example:

    class Greeting(Mark):
        collect_into = '_greetings'

        def build(mark, *args):
            if isinstance(mark, str):
                return Greeting(text=mark)
            return mark

    class Greetings(Declared):

        def __init__(self, name):
            self.name = name

        @declare(Greeting)
        def in_english(self):
            return 'Hello, %s' % self.name

Note that you don't even need to register `str` to be a subclass of Greeting.

-------

Another [example](examples.md#lazy-declaration) for lazy declarations you can find in the Examples section as a continuation to "Daily Routine".