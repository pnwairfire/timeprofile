__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

#import copy
import datetime

from numpy.testing import assert_approx_equal
from py.test import raises

from timeprofile.static import StaticTimeProfiler

# def assert_approximately_equal(expected, actual):
#     # categories

#     assert set(expected.keys()) == set(actual.keys())
#     for c in expected.keys():
#         print '- %s' % (c)
#         # sub-categories
#         assert set(expected[c].keys()) == set(actual[c].keys())
#         for sc in expected[c].keys():
#             print ' - %s' % (sc)
#             # combustion phases
#             assert set(expected[c][sc].keys()) == set(actual[c][sc].keys())
#             for cp in expected[c][sc].keys():
#                 print '  - %s' % (cp)
#                 # chemical species
#                 assert set(expected[c][sc][cp].keys()) == set(actual[c][sc][cp].keys())
#                 for s in expected[c][sc][cp].keys():
#                     print '   - %s' % (s)
#                     # emissions values
#                     assert len(expected[c][sc][cp][s]) == len(actual[c][sc][cp][s])
#                     for i in xrange(len(expected[c][sc][cp][s])):
#                         print "expected[%s][%s][%s][%s][%s][%s] vs actual[%s][%s][%s][%s][%s][%s]" % (
#                             c,sc,cp,s,i,expected[c][sc][cp][s][i],
#                             c,sc,cp,s,i,actual[c][sc][cp][s][i])
#                         if expected[c][sc][cp][s][i] is None:
#                             assert None == actual[c][sc][cp][s][i]
#                         else:
#                             # first argument in assert_approx_equal is actual,
#                             # second is epected (it doesn't matter except that
#                             # error message will be misleading if order is reversed)
#                             assert_approx_equal(
#                                 actual[c][sc][cp][s][i],
#                                 expected[c][sc][cp][s][i],
#                                 significant=8  # arbitrarily chose 8
#                             )

def assert_arrays_are_approximately_equal(a, b):
    assert len(a) == len(b)
    for i in xrange(len(a)):
        assert_approx_equal(a[i], b[i], significant=3)# 8)  # arbitrarily chose 8

class TestStaticTimeProfiler(object):

    def test_validate(self):
        with raises(ValueError) as e:
            s = datetime.datetime(2015, 1, 1, 12)
            e = datetime.datetime(2015, 1, 1, 11)
            StaticTimeProfiler()._validate({}, s, e)

    DAILY_HOURLY_FRACTIONS = [
        0.005, 0.005, 0.01, 0.01, 0.01, 0.01,
        0.05, 0.05, 0.05, 0.05, 0.05, 0.05,
        0.10, 0.10, 0.05, 0.05, 0.05, 0.05,
        0.05, 0.05, 0.05, 0.05, 0.03, 0.02,
    ]

    def test_compute_hourly_fractions_one_day(self):
        s = datetime.datetime(2015, 1, 1, 0)
        e = datetime.datetime(2015, 1, 2, 0)
        r = StaticTimeProfiler()._compute_hourly_fractions(s, e)
        assert_arrays_are_approximately_equal(r,
            StaticTimeProfiler.DEFAULT_DAILY_HOURLY_FRACTIONS)

        stp = StaticTimeProfiler(self.DAILY_HOURLY_FRACTIONS)
        r = stp._compute_hourly_fractions(s, e)
        assert_arrays_are_approximately_equal(r,
            self.DAILY_HOURLY_FRACTIONS)

    def test_compute_hourly_fractions_two_days(self):
        s = datetime.datetime(2015, 1, 1, 0)
        e = datetime.datetime(2015, 1, 3, 0)
        r = StaticTimeProfiler()._compute_hourly_fractions(s, e)
        expected = 2* map(lambda x: x / 2,
            StaticTimeProfiler.DEFAULT_DAILY_HOURLY_FRACTIONS)
        assert_arrays_are_approximately_equal(r, expected)

        stp = StaticTimeProfiler(self.DAILY_HOURLY_FRACTIONS)
        r = stp._compute_hourly_fractions(s, e)
        expected = 2* map(lambda x: x / 2, self.DAILY_HOURLY_FRACTIONS)
        assert_arrays_are_approximately_equal(r, expected)

    def test_compute_hourly_fractions_partial_days(self):
        s = datetime.datetime(2015, 1, 1, 12, 20)
        e = datetime.datetime(2015, 1, 2, 16, 40)
        r = StaticTimeProfiler()._compute_hourly_fractions(s, e)
        # TODO: This is what is returned; verify manually that it is correct,
        # and if so, use it in an assert
        # [
        #     0.0,
        #     0.06411078343377354,
        #     0.08334401846390559,
        #     0.10257725349403765,
        #     0.108988331837415,
        #     0.07693294012052823,
        #     0.04487754840364148,
        #     0.025644313373509413,
        #     0.0036543146557250915,
        #     0.0036543146557250915,
        #     0.0036543146557250915,
        #     0.0036543146557250915,
        #     0.0036543146557250915,
        #     0.0036543146557250915,
        #     0.0036543146557250915,
        #     0.0036543146557250915,
        #     0.0036543146557250915,
        #     0.0036543146557250915,
        #     0.0036543146557250915,
        #     0.0036543146557250915,
        #     0.0036543146557250915,
        #     0.0036543146557250915,
        #     0.012822156686754706,
        #     0.025644313373509413,
        #     0.04487754840364148,
        #     0.06411078343377354,
        #     0.08334401846390559,
        #     0.10257725349403765,
        #     0.108988331837415
        # ]
        # TODO: add assert