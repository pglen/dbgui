## dev on v3.7.6

from datetime import datetime
from time import mktime, time


class Time:
    '''\
*Convenience class for easy format conversion*\n
Accepts time() float, datetime object, or SQL datetime str.\n
If no time arg is provided, object is initialized with time().\n
id kwarg can be used to keep track of objects.\n
Access formats as instance.t, instance.dt, or instance.sql.\
    '''

    f = '%Y-%m-%d %H:%M:%S'

    def __init__(self, *arg, id=None) -> None:
        self.id = id
        if len(arg) == 0:
            self.t = time()
            self.dt = self._dt
            self.sql = self._sql
        else:
            arg = arg[0]
            if isinstance(arg, float) or arg == None:
                if isinstance(arg, float):
                    self.t = arg
                else:
                    self.t = time()
                self.dt = self._dt
                self.sql = self._sql
            elif isinstance(arg, datetime):
                self.t = arg.timestamp()
                self.dt = arg
                self.sql = self._sql
            elif isinstance(arg, str):
                self.sql = arg
                if '.' not in arg:
                    self.dt = datetime.strptime(self.sql, Time.f)
                else:
                    normal, fract = arg.split('.')
                    py_t = datetime.strptime(normal, Time.f)
                    self.dt = py_t.replace(
                        microsecond=int(fract.ljust(6, '0')[:6]))
                self.t = self.dt.timestamp()

    @property
    def _dt(self) -> datetime:
        return datetime.fromtimestamp(self.t)

    @property
    def _sql(self) -> str:
        t = self.dt
        std = t.strftime(Time.f)
        fract = f'.{str(round(t.microsecond, -3))[:3]}'
        return std + fract

    def __str__(self) -> str:
        if self.id == None:
            return self.sql
        else:
            return f'Time obj "{self.id}": {self.sql}'


def test():
    def test_one(*arg):
        t = Time(*arg, id=type(*arg))
        print(t)
        print(t.t)
        print(t.dt)

    sql = '2020-01-22 15:30:33.433'
    time_float = 1579927395.3708763
    dt_obj = datetime.now()
    for datum in [sql, time_float, dt_obj, None]:
        test_one(datum)


if __name__ == '__main__':
    test()


