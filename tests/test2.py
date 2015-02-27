from time import strptime, struct_time
from declared import Mark, Declared, SkipMark

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


class time(Mark):

    collect_into = '_timepoints'

    def __init__(self, value):
        self.value = value

    @classmethod
    def build(cls, mark, marks, owner):
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

class DailyRoutine(Declared, extract=time):
    pass

class MyDailyRoutine(DailyRoutine):
    breakfast = '9:00'
    lunch = '12:00'
    dinner = '-1:33' # invalid data

from util import case

case.assertSequenceEqual(
    list(MyDailyRoutine._timepoints.keys()),
    ['breakfast', 'lunch'])
