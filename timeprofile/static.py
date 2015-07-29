"""timeprofile.static

In this simple, static time-profiling model, no environmental conditions
(such as reltative humidity) are considered"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

import datetime

from nested_dict import nested_dict

class InvalidConsumptionDataError(ValueError):
    pass

class StaticTimeProfiler(object):

    DEFAULT_DEFAULT_HOURLY_FRACTIONS = []
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
    ]

    def __init__(self, daily_hourly_fractions=None, **options):
        """StaticTimeProfiler constructor

        kwargs:
         - daily_hourly_fractions - custom hourly fraction of daily emissions
        """
        self.daily_hourly_fractions = (daily_hourly_fractions or
            DEFAULT_DEFAULT_HOURLY_FRACTIONS)

    def profile(self, emissions, local_start_time, local_end_time):
        """

        """
        self._validate(emissions, local_start_time, local_end_time)

        hourly_percentages = self._compute_hourly_fractions(
            local_start_time, local_end_time)

        tpe = nested_dict()
        for category in emissions:
            for phase in emissions[category]:
                for species in emissions[category][phase]:
                    tpe[category][phase][species] = []
                    for val in emissions[category][phase]:
                        e = []
                        for p in
                        tpe[category][phase][species].append(e)
        return tpe.to_dict()

    def _validate(self, emissions, local_start_time, local_end_time):
        if local_start_time > local_end_time:
            # TODO: Use custom Exception
            raise ValueError("...")

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

        r = []
        d = start_hour
        while d <= end_hour:
            f = daily_hourly_fractions[d.hour]
            if d == start_hour:
                f *= (3600 - first_hour_offset.seconds) / 3600
            elif d == end_hour:
                f *= last_hour_offset.seconds / 3600
            r.append(f)

        # Normalize so that it all adds up to 1.0
        total = reduce(lambda x, y: x + y, r)
        r = map(lambda x: x / total, r)
        return r
