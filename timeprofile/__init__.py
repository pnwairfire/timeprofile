__author__      = "Joel Dubowy"

__version_info__ = (1,0,0)
__version__ = '.'.join([str(n) for n in __version_info__])



class BaseTimeProfiler(object):

    ONE_HOUR = datetime.timedelta(hours=1)
    FIELDS = ['area_fraction', 'flaming', 'smoldering', 'residual']

    def _validate_start_end_times(self, local_start_time, local_end_time):
        """Raises an InvalidStartEndTimesError exception if times are invalid.
        """
        # TODO: other checks ?
        if local_start_time >= local_end_time:
            raise InvalidStartEndTimesError(
                "The fire's start time, {}, is not before its end time, {}".format(
                local_start_time.isoformat(), local_end_time.isoformat()))

