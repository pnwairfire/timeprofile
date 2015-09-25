__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

#import copy
import datetime

from numpy.testing import assert_approx_equal
from py.test import raises

from timeprofile.static import (
    StaticTimeProfiler,
    InvalidStartEndTimesError,
    InvalidHourlyFractionsError
)

def assert_approximately_equal(expected, actual):
    if isinstance(expected, dict) and isinstance(actual, dict):
        assert set(expected.keys()) == set(actual.keys())
        for k in expected:
            assert_approximately_equal(expected[k], actual[k])
    elif isinstance(expected, list) and isinstance(actual, list):
        assert len(expected) == len(actual)
        for i in xrange(len(expected)):
            assert_approximately_equal(expected[i], actual[i])
    elif isinstance(expected, float) and isinstance(actual, float):
        assert_approx_equal(actual, expected, significant=8)  # arbitrarily chose 8
    else:
        assert expected == actual

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

class TestStaticTimeProfiler_ValidationMethods(object):

    def _dummy_profiler(self, monkeypatch):
        monkeypatch.setattr(StaticTimeProfiler, "_compute_hourly_fractions",
            lambda *args: None)
        return StaticTimeProfiler(None, None)

    def test_validate_start_end_times(self, monkeypatch):
        profiler = self._dummy_profiler(monkeypatch)

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

    # TODO: add test for _validate_hourly_fractions
    # TODO: add test for _validate_emissions

class TestStaticTimeProfiler_DefaultHourlyFractions(object):


    def test_one_day(self):
        # First make sure daily fractions are computed correctly
        st = datetime.datetime(2015, 1, 1, 0)
        et = datetime.datetime(2015, 1, 2, 0)
        stp = StaticTimeProfiler(st, et)
        #assert set(stp.PHASES) == set(stp.hourly_fractions.keys())
        expected_hourly_fractions = {
            p: stp.DEFAULT_DAILY_HOURLY_FRACTIONS[p] for p in stp.PHASES
        }
        assert_approximately_equal(expected_hourly_fractions, stp.hourly_fractions)

        # Now, test computation of profiled emissions
        # TODO: ....

    def test_two_days(self):
        # First make sure daily fractions are computed correctly
        st = datetime.datetime(2015, 1, 1, 0)
        et = datetime.datetime(2015, 1, 3, 0)
        stp = StaticTimeProfiler(st, et)
        #assert set(stp.PHASES) == set(stp.hourly_fractions.keys())
        expected_hourly_fractions = {
            p: 2 * map( lambda e: e / 2.0, stp.DEFAULT_DAILY_HOURLY_FRACTIONS[p])
                for p in stp.PHASES
        }
        assert_approximately_equal(expected_hourly_fractions, stp.hourly_fractions)

        # Now, test computation of profiled emissions
        # TODO: ....

    def test_partial_days(self):
        # First make sure daily fractions are computed correctly
        # TODO: ...

        # Now, test computation of profiled emissions
        # TODO: ...
        pass


class TestStaticTimeProfiler_CustomDailyHourlyFractions(object):

    DAILY_HOURLY_FRACTIONS = {
        'flaming': [
            0.005, 0.005, 0.01, 0.01, 0.01, 0.01,
            0.05, 0.05, 0.05, 0.05, 0.05, 0.05,
            0.10, 0.10, 0.05, 0.05, 0.05, 0.05,
            0.05, 0.05, 0.05, 0.05, 0.03, 0.02,
        ],
        'residual': [  # shifted 6 hrs
            0.05, 0.05, 0.05, 0.05, 0.03, 0.02,
            0.005, 0.005, 0.01, 0.01, 0.01, 0.01,
            0.05, 0.05, 0.05, 0.05, 0.05, 0.05,
            0.10, 0.10, 0.05, 0.05, 0.05, 0.05,
        ],
        'smoldering': [  # shifted another 6 hrss
            0.10, 0.10, 0.05, 0.05, 0.05, 0.05,
            0.05, 0.05, 0.05, 0.05, 0.03, 0.02,
            0.005, 0.005, 0.01, 0.01, 0.01, 0.01,
            0.05, 0.05, 0.05, 0.05, 0.05, 0.05,
        ]
    }

    def test_one_day(self):
        st = datetime.datetime(2015, 1, 1, 0)
        et = datetime.datetime(2015, 1, 2, 0)
        stp = StaticTimeProfiler(st, et, hourly_fractions=self.DAILY_HOURLY_FRACTIONS)
        #assert set(stp.PHASES) == set(stp.hourly_fractions.keys())
        expected_hourly_fractions = {
            p: self.DAILY_HOURLY_FRACTIONS[p] for p in stp.PHASES
        }
        assert_approximately_equal(expected_hourly_fractions, stp.hourly_fractions)

        # Now, test computation of profiled emissions
        # TODO: ....

    def test_two_days(self):
        st = datetime.datetime(2015, 1, 1, 0)
        et = datetime.datetime(2015, 1, 3, 0)
        stp = StaticTimeProfiler(st, et, hourly_fractions=self.DAILY_HOURLY_FRACTIONS)

        # expected = 2* map(lambda x: x / 2,
        #     StaticTimeProfiler.DEFAULT_DAILY_HOURLY_FRACTIONS)
        # assert_approximately_equal(r, expected)

        # stp = StaticTimeProfiler(self.DAILY_HOURLY_FRACTIONS)
        # r = stp._compute_hourly_fractions(s, e)
        # expected = 2* map(lambda x: x / 2, self.DAILY_HOURLY_FRACTIONS)
        # assert_approximately_equal(r, expected)

        pass

    def test_partial_days(self):
        # s = datetime.datetime(2015, 1, 1, 12, 20)
        # e = datetime.datetime(2015, 1, 2, 16, 40)
        # stp = StaticTimeProfiler(self.DAILY_HOURLY_FRACTIONS)
        # r = stp._compute_hourly_fractions(s, e)
        # print r
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

        pass

class TestStaticTimeProfiler_CustomHourlyFractions(object):

    # 48 hours worth of hourly fractions
    HOURLY_FRACTIONS = {
        'flaming': [
            0.005, 0.005, 0.01, 0.01, 0.01, 0.01,
            0.05, 0.05, 0.05, 0.05, 0.05, 0.05,
            0.05, 0.10, 0.05, 0.05, 0.05, 0.05,
            0.05, 0.05, 0.05, 0.05, 0.03, 0.02,
            0.02, 0.02, 0.01, 0.00, 0.00, 0.00,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        ],
        'residual': [  # shifted 6 hrs
            0.05, 0.05, 0.05, 0.05, 0.03, 0.02,
            0.005, 0.005, 0.01, 0.01, 0.01, 0.01,
            0.05, 0.05, 0.05, 0.05, 0.05, 0.05,
            0.05, 0.05, 0.05, 0.05, 0.05, 0.05,
            0.05, 0.05, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        ],
        'smoldering': [  # shifted another 6 hrss
            0.10, 0.10, 0.05, 0.05, 0.05, 0.05,
            0.05, 0.05, 0.05, 0.05, 0.03, 0.02,
            0.005, 0.005, 0.01, 0.01, 0.01, 0.01,
            0.05, 0.05, 0.05, 0.05, 0.05, 0.05,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        ]
    }

    def test_one_day(self):
        st = datetime.datetime(2015, 1, 1, 0)
        et = datetime.datetime(2015, 1, 2, 0)
        with raises(InvalidHourlyFractionsError) as e:
            stp = StaticTimeProfiler(st, et, hourly_fractions=self.HOURLY_FRACTIONS)

    def test_two_days(self):
        st = datetime.datetime(2015, 1, 1, 0)
        et = datetime.datetime(2015, 1, 3, 0)
        stp = StaticTimeProfiler(st, et, hourly_fractions=self.HOURLY_FRACTIONS)
        expected_hourly_fractions = {
            p: self.HOURLY_FRACTIONS[p] for p in stp.PHASES
        }
        assert_approximately_equal(expected_hourly_fractions, stp.hourly_fractions)

        # Now, test computation of profiled emissions
        # TODO: ...

    def test_three_days(self):
        st = datetime.datetime(2015, 1, 1, 0)
        et = datetime.datetime(2015, 1, 4, 0)
        with raises(InvalidHourlyFractionsError) as e:
            stp = StaticTimeProfiler(st, et, hourly_fractions=self.HOURLY_FRACTIONS)
