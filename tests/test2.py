from time import strptime, struct_time
from declared import Mark, DeclaredMeta

class Time(Mark):

    collect_into = '_time_marks'

    def __init__(self, value):
        self.value = value

    def build(self, marks, owner):
        return strptime(self.value, '%H:%M')


class DailyRoutine(metaclass=DeclaredMeta):

    breakfast = Time('9:00')
    lunch = Time('12:00')

from util import case

case.assertIsInstance(DailyRoutine._time_marks['breakfast'], struct_time)
