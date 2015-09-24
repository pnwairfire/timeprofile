"""timeprofile.static

In this simple, static time-profiling model, no environmental conditions
(such as reltative humidity) are considered.
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

import datetime
from collections import defaultdict

from nested_dict import nested_dict

__all__ = [
    'StaticTimeProfiler',
    'InvalidDailyHourlyFractionsError',
    'InvalidStartEndTimesError',
    'InvalidEmissionsDataError'
]

class InvalidDailyHourlyFractionsError(ValueError):
    pass

class InvalidStartEndTimesError(ValueError):
    pass

class InvalidEmissionsDataError(ValueError):
    pass

class StaticTimeProfiler(object):

    PHASES = ['flaming', 'smoldering', 'residual']

    DEFAULT_DAILY_HOURLY_FRACTIONS = defaultdict(lambda: [
        0.005700, # 00:00 (local time)
        0.005700, # 01:00
        0.005700, # 02:00
        0.005700, # 03:00
        0.005700, # 04:00
        0.005700, # 05:00
        0.005700, # 06:00
        0.005700, # 07:00
        0.005700, # 08:00
        0.005700, # 09:00
        0.020000, # 10:00
        0.040000, # 11:00
        0.070000, # 12:00
        0.100000, # 13:00
        0.130000, # 14:00
        0.160000, # 15:00
        0.170000, # 16:00
        0.120000, # 17:00
        0.070000, # 18:00
        0.040000, # 19:00
        0.005700, # 20:00
        0.005700, # 21:00
        0.005700, # 22:00
        0.005700 # 23:00
    ])
    """DEFAULT_DAILY_HOURLY_FRACTIONS will return the same hourly fractions
    for 'flaming', 'smoldering' and 'residual'"""

    def __init__(self, local_start_time, local_end_time, daily_hourly_fractions=None): #, **options):
        """StaticTimeProfiler constructor

        kwargs:
         - daily_hourly_fractions - custom hourly fraction of daily emissions
        """
        self._validate_daily_hourly_fractions
        self.daily_hourly_fractions = (daily_hourly_fractions or
            self.DEFAULT_DAILY_HOURLY_FRACTIONS)

        self._validate_start_end_times(local_start_time, local_end_time)
        self.local_start_time = local_start_time
        self.local_end_time = local_end_time
        self.hourly_fractions = self._compute_hourly_fractions(
            local_start_time, local_end_time)

    def profile(self, emissions):
        """

        """
        self._validate_emissions(emissions, local_start_time, local_end_time)

        tpe = nested_dict()
        for category in emissions:
            for phase in emissions[category]:
                for species in emissions[category][phase]:
                    tpe[category][phase][species] = []
                    for val in emissions[category][phase][species]:
                        e = map(lambda x: x*val, self.hourly_fractions[phase])
                        tpe[category][phase][species].append(e)
        return tpe.to_dict()

    def _validate_daily_hourly_fractions(self, daily_hourly_fractions):
        """Raises an InvalidDailyHourlyFractionsError exception if validation
        fails.
        """
        if daily_hourly_fractions:
            for k in self.PHASES:
                if (len(daily_hourly_fractions.get(k, [])) != 24 or
                        abs(1 - sum(daily_hourly_fractions[k])) > 0.001):
                    raise InvalidDailyHourlyFractionsError(
                        "There must be 24 hourly fractions that sum to 1.00"
                        " for '{}' phases".format(', '.join(self.PHASES)))


    def _validate_start_end_times(self, local_start_time, local_end_time):
        if local_start_time > local_end_time:
            raise InvalidEmissionsDataError(
                "The fire's start time, {}, is later than its end time, {}".format(
                local_start_time.isoformat(), local_end_time.isoformat()))

    def _validate_emissions(self, emissions):
        # TODO: check emissions data
        pass

    ONE_HOUR = datetime.timedelta(hours=1)

    def _compute_hourly_fractions(self, local_start_time, local_end_time):
        """Determines what fraction of the fire's emissions occur in each
        calendar hour of the fire's duration.

        For example, if....

        Args:
         - emissions --
         - local_start_time --
         - local_end_time --
        """
        first_hour_offset = datetime.timedelta(
            minutes=local_start_time.minute, seconds=local_start_time.second)
        start_hour = local_start_time - first_hour_offset

        if local_end_time.time() == datetime.time(local_end_time.hour):
            # fire ended exactly on the hour
            end_hour = local_end_time - self.ONE_HOUR
            last_hour_offset = self.ONE_HOUR
        else:
            last_hour_offset = datetime.timedelta(
                minutes=local_end_time.minute, seconds=local_end_time.second)
            end_hour = local_end_time - first_hour_offset

        # TODO: if more efficient, iterate by phase within the while loop
        hourly_fractions = {}
        for p in self.PHASES:
            r = []
            d = start_hour
            while d <= end_hour:
                f = self.daily_hourly_fractions[d.hour]
                if d == start_hour:
                    f *= (3600 - first_hour_offset.seconds) / 3600
                elif d == end_hour:
                    f *= last_hour_offset.seconds / 3600
                r.append(f)
                d += self.ONE_HOUR

            # Normalize so that it all adds up to 1.0
            total = reduce(lambda x, y: x + y, r)
            hourly_fractions[p] = map(lambda x: x / total, r)
        return p
