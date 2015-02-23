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

Then we are going to define a class for the respective mark. We want it to understand strings as well:

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

And specify the default class for marks, so that it would know what to do with those strings:

    class DailyRoutine(metaclass=DeclaredMeta):
        default_mark = time
        
Now we are done. We can write our daily routine classes and inherit it from `DailyRoutine`.

-----------------------

## Lazy declaration

Let's try to write a daily routine with floating time of getting up. Here is what
it will look like using lazy declarations:

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
