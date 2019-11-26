__author__      = "Joel Dubowy"

import datetime

from py.test import raises

from timeprofile import (
    BaseTimeProfiler,
    InvalidStartEndTimesError
)

class TestBaseTimeProfiler_ValidationMethods(object):

    def test_validate_start_end_times(self, monkeypatch):
        profiler = BaseTimeProfiler()

        st = datetime.datetime(2015, 1, 1, 11)
        et = datetime.datetime(2015, 1, 1, 12)
        # start can't come after end
        with raises(InvalidStartEndTimesError) as e:
            profiler._validate_start_end_times(et, st)
        # start can't equal end
        with raises(InvalidStartEndTimesError) as e:
            profiler._validate_start_end_times(st, st)
        # proper order of dates shouldn't raise error
        profiler._validate_start_end_times(st, et)
