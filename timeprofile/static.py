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
    'InvalidHourlyFractionsError',
    'InvalidStartEndTimesError',
    'InvalidEmissionsDataError'
]

class InvalidHourlyFractionsError(ValueError):
    pass

class InvalidStartEndTimesError(ValueError):
    pass

class InvalidEmissionsDataError(ValueError):
    pass

class StaticTimeProfiler(object):

    # Include 'area_frac[tion]', and rename PHASES to something else?
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
        0.005800, # 09:00
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
        0.005800, # 20:00
        0.005700, # 21:00
        0.005700, # 22:00
        0.005700 # 23:00
    ])
    """DEFAULT_DAILY_HOURLY_FRACTIONS will return the same hourly fractions
    for 'flaming', 'smoldering' and 'residual'

    These hourly fractions were copied from the wrap_time_profile module in
    BlueSky Framework, and modified slightly.  The 09:00 and 20:00 were both
    increased from 0.0057 to 0.0058 so that the values add up to 1.00.  (The
    values in wrap_time_profile add up to 0.9998)
    """

    def __init__(self, local_start_time, local_end_time, hourly_fractions=None): #, **options):
        """StaticTimeProfiler constructor

        kwargs:
         - hourly_fractions - custom hourly fractions of emissions; can be
           specified for all hours from start to end times, or for a single 24
           hour day, to be repeated or truncated to fill the time window defined
           by local_start_time / local_end_time

        *Note*: If len(hourly_fractions) == 24, they are assumed to represent
           fractions from 00:00 through 23:00.  If the start/end define a 24 hour
           period that does *not* start at 00:00, be aware that the values
           in hourly_fractions will *not* be applied from index 0 through 23.
           Whenever len(hourly_fractions) == 24 (regardless of the start/end),
           the local hour of day is used as the index to hourly_fractions.
        """
        self.hourly_fractions = self._compute_hourly_fractions(
            local_start_time, local_end_time, hourly_fractions)

    ##
    ## Public interface
    ##

    def profile(self, emissions):
        """Computes the time profile emissions
        """
        self._validate_emissions(emissions)

        tpe = nested_dict()
        for category in emissions:
            for subcategory in emissions[category]:
                for phase in emissions[category][subcategory]:
                    # make sure phase isn't "total" (any other invalid phase)
                    if phase in self.hourly_fractions:
                        for species in emissions[category][subcategory][phase]:
                            tpe[category][subcategory][phase][species] = []
                            for val in emissions[category][subcategory][phase][species]:
                                e = map(lambda x: x*val, self.hourly_fractions[phase])
                                tpe[category][subcategory][phase][species].append(e)
        return tpe.to_dict()

    ##
    ## Validation Methods
    ##

    def _validate_start_end_times(self, local_start_time, local_end_time):
        """Raises an InvalidStartEndTimesError exception if times are invalid.
        """
        # TODO: other checks ?
        if local_start_time >= local_end_time:
            raise InvalidStartEndTimesError(
                "The fire's start time, {}, is not before its end time, {}".format(
                local_start_time.isoformat(), local_end_time.isoformat()))

    def _validate_hourly_fractions(self, num_hours, hourly_fractions):
        """Raises an InvalidHourlyFractionsError exception if validation
        fails.
        """
        if hourly_fractions:
            for k in self.PHASES:
                if (len(hourly_fractions.get(k, [])) not in (24, num_hours) or
                        abs(1 - sum(hourly_fractions[k])) > 0.001):
                    raise InvalidHourlyFractionsError(
                        "There must be 24 or {} hourly fractions that sum to 1.00"
                        " for each of the '{}' phases".format(
                        num_hours, ', '.join(self.PHASES)))

    def _validate_emissions(self, emissions):
        # TODO: check emissions data
        pass

    ##
    ## Computing Hourly Fractions
    ##

    ONE_HOUR = datetime.timedelta(hours=1)

    def _compute_hourly_fractions(self, local_start_time, local_end_time,
            hourly_fractions):
        """Determines what fraction of the fire's emissions occur in each
        calendar hour of the fire's duration.

        For example, if....

        Args:
         - emissions --
         - local_start_time --
         - local_end_time --
        """
        self._validate_start_end_times(local_start_time, local_end_time)

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

        # TODO: use math.ceil instead of int? (should have divided evenly, so prob not)
        num_hours = int((end_hour - start_hour).total_seconds() / 3600) + 1
        self._validate_hourly_fractions(num_hours, hourly_fractions)

        hourly_fractions = hourly_fractions or self.DEFAULT_DAILY_HOURLY_FRACTIONS

        # TODO: if more efficient, iterate by phase within the while loop
        new_hourly_fractions = {}
        for p in self.PHASES:
            num_hourly_fractions = len(hourly_fractions[p])
            r = []
            i = 0
            d = start_hour
            while d <= end_hour:
                idx = d.hour if num_hourly_fractions == 24 else i
                f = hourly_fractions[p][idx]
                if d == start_hour:
                    f *= (3600 - first_hour_offset.seconds) / 3600
                elif d == end_hour:
                    f *= last_hour_offset.seconds / 3600
                r.append(f)
                d += self.ONE_HOUR
                i += 1

            # Normalize so that it all adds up to 1.0
            total = reduce(lambda x, y: x + y, r)
            new_hourly_fractions[p] = map(lambda x: x / total, r)
        return new_hourly_fractions
