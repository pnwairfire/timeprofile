__author__      = "Joel Dubowy"

#import copy
import datetime

from numpy.testing import assert_approx_equal
from py.test import raises

from timeprofile.feps import (
    FepsTimeProfiler, FireType, InvalidStartEndTimesError
)

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

    ## Invalid Cases

    def test_start_after_end(self):
        s = datetime.datetime(2015, 1, 1, 12)
        e = datetime.datetime(2015, 1, 1, 10)
        with raises(InvalidStartEndTimesError) as e_info:
            profiler = FepsTimeProfiler(s, e, fire_type=FireType.RX)
        # TODO: check e_info.valeu.args[0]

    def test_start_same_as_end(self):
        s = datetime.datetime(2015, 1, 1, 12)
        e = datetime.datetime(2015, 1, 1, 12)
        with raises(InvalidStartEndTimesError) as e_info:
            profiler = FepsTimeProfiler(s, e, fire_type=FireType.RX)
        # TODO: check e_info.valeu.args[0]

    def test_ignition_start_after_end(self):
        s = datetime.datetime(2015, 1, 1, 0)
        e = datetime.datetime(2015, 1, 1, 12)
        ig_s = datetime.datetime(2015, 1, 1, 12)
        ig_e = datetime.datetime(2015, 1, 1, 9)
        with raises(InvalidStartEndTimesError) as e_info:
            profiler = FepsTimeProfiler(s, e, local_ignition_start_time=ig_s,
                local_ignition_end_time=ig_e, fire_type=FireType.RX)
        # TODO: check e_info.valeu.args[0]

    def test_ignition_start_same_as_end(self):
        s = datetime.datetime(2015, 1, 1, 0)
        e = datetime.datetime(2015, 1, 1, 12)
        ig_s = datetime.datetime(2015, 1, 1, 12)
        ig_e = datetime.datetime(2015, 1, 1, 12)
        with raises(InvalidStartEndTimesError) as e_info:
            profiler = FepsTimeProfiler(s, e, local_ignition_start_time=ig_s,
                local_ignition_end_time=ig_e, fire_type=FireType.RX)
        # TODO: check e_info.valeu.args[0]

    def test_wf_not_yet_implemented(self):
        s = datetime.datetime(2015, 1, 1, 9)
        e = datetime.datetime(2015, 1, 1, 12)
        with raises(NotImplementedError) as e_info:
            profiler = FepsTimeProfiler(s, e, fire_type=FireType.WF)


    ## Valid Cases - Ignition not specified

    def test_9am_to_12pm_no_ig_times(self):
        s = datetime.datetime(2015, 1, 1, 9)
        e = datetime.datetime(2015, 1, 1, 12)
        profiler = FepsTimeProfiler(s, e, fire_type=FireType.RX)

        # TODO: check times
        # TDOD: add assert to check hourly fractions

    def test_930am_to_12pm_no_ig_times(self):
        s = datetime.datetime(2015, 1, 1, 9, 30)
        e = datetime.datetime(2015, 1, 1, 12)
        profiler = FepsTimeProfiler(s, e, fire_type=FireType.RX)

        # TODO: check times
        # TDOD: add assert to check hourly fractions

    def test_12am_to_12am_no_ig_times(self):
        s = datetime.datetime(2015, 1, 1, 0)
        e = datetime.datetime(2015, 1, 2, 0)
        profiler = FepsTimeProfiler(s, e, fire_type=FireType.RX)

        # TODO: check times
        # TDOD: add assert to check hourly fractions

    def test_12am_to_1030am_no_ig_times(self):
        s = datetime.datetime(2015, 1, 1, 0)
        e = datetime.datetime(2015, 1, 1, 10, 30)
        profiler = FepsTimeProfiler(s, e, fire_type=FireType.RX)

        # TODO: check times
        # TDOD: add assert to check hourly fractions

    def test_two_days_12am_to_12am_no_ig_times(self):
        s = datetime.datetime(2015, 1, 1, 0)
        e = datetime.datetime(2015, 1, 3, 0)
        profiler = FepsTimeProfiler(s, e, fire_type=FireType.RX)

        # TODO: check times
        # TDOD: add assert to check hourly fractions

    def test_12pm_to_12am_no_ig_times(self):
        s = datetime.datetime(2015, 1, 1, 12)
        e = datetime.datetime(2015, 1, 2, 0)
        profiler = FepsTimeProfiler(s, e, fire_type=FireType.RX)

        # TODO: check times
        # TDOD: add assert to check hourly fractions

    def test_12pm_to_12pm_no_ig_times(self):
        s = datetime.datetime(2015, 1, 1, 12)
        e = datetime.datetime(2015, 1, 2, 12)
        profiler = FepsTimeProfiler(s, e, fire_type=FireType.RX)

        # TODO: check times
        # TDOD: add assert to check hourly fractions


    ## Valid Cases - Ignition start & end specified

    def test_9am_to_12pm_same_ig_times(self):
        s = datetime.datetime(2015, 1, 1, 9)
        e = datetime.datetime(2015, 1, 1, 12)
        ig_s = datetime.datetime(2015, 1, 1, 9)
        ig_e = datetime.datetime(2015, 1, 1, 12)
        profiler = FepsTimeProfiler(s, e, local_ignition_start_time=ig_s,
            local_ignition_end_time=ig_e, fire_type=FireType.RX)

        # TODO: check times
        # TDOD: add assert to check hourly fractions

    def test_12am_to_12am_ig_10am_to_2pm(self):
        s = datetime.datetime(2015, 1, 1, 0)
        e = datetime.datetime(2015, 1, 2, 0)
        ig_s = datetime.datetime(2015, 1, 1, 10)
        ig_e = datetime.datetime(2015, 1, 1, 14)
        profiler = FepsTimeProfiler(s, e, local_ignition_start_time=ig_s,
            local_ignition_end_time=ig_e, fire_type=FireType.RX)

        # TODO: check times
        # TDOD: add assert to check hourly fractions


    def test_two_days_12am_to_12am_ig_10am_to_2pm(self):
        s = datetime.datetime(2015, 1, 1, 0)
        e = datetime.datetime(2015, 1, 3, 0)
        ig_s = datetime.datetime(2015, 1, 1, 10)
        ig_e = datetime.datetime(2015, 1, 1, 14)
        profiler = FepsTimeProfiler(s, e, local_ignition_start_time=ig_s,
            local_ignition_end_time=ig_e, fire_type=FireType.RX)

        # TODO: check times
        # TDOD: add assert to check hourly fractions

    def test_two_days_1230am_to_12am_ig_1030am_to_2pm(self):
        s = datetime.datetime(2015, 1, 1, 0, 30)
        e = datetime.datetime(2015, 1, 3, 0)
        ig_s = datetime.datetime(2015, 1, 1, 10)
        ig_e = datetime.datetime(2015, 1, 1, 14)
        profiler = FepsTimeProfiler(s, e, local_ignition_start_time=ig_s,
            local_ignition_end_time=ig_e, fire_type=FireType.RX)

        # TODO: check times
        # TDOD: add assert to check hourly fractions


    ## Valid Cases - Ignition only start specified

    # TDOO: implement


    ## Valid Cases - Ignition only end specified

    # TDOO: implement
