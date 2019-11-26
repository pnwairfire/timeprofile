__author__      = "Joel Dubowy"

#import copy
import datetime

from numpy.testing import assert_approx_equal
from py.test import raises

from timeprofile.static import FepsTimeProfiler

def assert_approximately_equal(expected, actual):
    if isinstance(expected, dict) and isinstance(actual, dict):
        assert set(expected.keys()) == set(actual.keys())
        for k in expected:
            assert_approximately_equal(expected[k], actual[k])
    elif isinstance(expected, list) and isinstance(actual, list):
        assert len(expected) == len(actual)
        for i in range(len(expected)):
            assert_approximately_equal(expected[i], actual[i])
    elif isinstance(expected, float) and isinstance(actual, float):
        assert_approx_equal(actual, expected, significant=8)  # arbitrarily chose 8
    else:
        assert expected == actual

class TestFepsTimeProfiler_Rx(object):

    def test_three_hours(self):
        s = datetime.datetime(2015, 1, 1, 9, 0)
        e = datetime.datetime(2015, 1, 2, 12, 0)
        stp = FepsTimeProfiler(s, e)

        # TDOD: add assert to check hourly fractions
