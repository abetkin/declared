# Examples

The examples collection.

---

## Daily Routine

Let's make a more sophisticated class for daily routine. Here is what it will be able to do:

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
            
As you understand, it can add time intervals:

```python
>>> Time(1, 34) + '23:55'
1:29
```

Now we are going to define a class for time interval mark. We want it to understand strings as well:

    from declared import SkipMark

    class time(Mark):

        collect_into = '_timepoints'

        def __init__(self, value):
            self.value = value

        def build(mark, marks, owner):
            if isinstance(mark, str):
                try:
                    return Time.parse(mark)
                except ParseError:
                    raise SkipMark
            return Mark.parse(mark.value)

    time.register(str)

And specify the default class for marks, so that it would know what to do with those strings:

    class DailyRoutine(metaclass=DeclaredMeta):
        default_mark = time
        
Now we are done. We can write our daily routine classes and inherit it from `DailyRoutine`.

-----------------------