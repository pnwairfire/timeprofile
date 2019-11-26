"""timeprofile.feps

FEPS timeprofile, as described in
https://www.fs.fed.us/pnw/fera/feps/FEPS_users_guide.pdf
"""

from . import BaseTimeProfiler, InvalidStartEndTimesError

class FireType(object):

    RX = 'rx'
    WF = 'wf'


class FepsTimeProfiler(BaseTimeProfiler):

    # TODO: do we need fire_type?  can be inferred as rx if ignition times
    #   are defined

    def __init__(self, local_start_time, local_end_time,
            local_ignition_start_time=None, local_ignition_end_time=None,
            fire_type=FireType.RX):

        self._set_times(local_start_time, local_end_time,
            local_ignition_start_time, local_ignition_end_time, fire_type)

        # TODO: implement WF equation
        if fire_type == FireType.WF:
            raise NotImplementedError(
                "FEPS timeprofile not yet implemented for fire type WF")

        return getattr(self, '_compute_' + fire_type)()

    ## Initialization

    def _set_times(self, start, end, ig_start, ig_end):
        # Makes sure start < end
        self._validate_start_end_times(start, end)
        self._start = start
        self._end = end

        # fill in local_ignition_start_time and/or local_ignition_end_time
        # if necessary
        if ig_start and ig_end:
            self._validate_start_end_times(start, end,
                time_qualifier="ignition")
            self._ig_start = ig_start
            self._ig_end = ig_end
        elif ig_start:
            self._ig_start = ig_start
            self._ig_end = ig_start + 3*self.ONE_HOUR
        elif ig_end:
            self._ig_start = ig_end - 3*self.ONE_HOUR
            self._ig_end = ig_end
        else:
            # set ig_start to 9am of start day if start is before 9am, else
            # set to start.  set ig_end to three hours after start.
            # then, shift and shrink window as necessary.  for eaxmple:
            #   - 12am start to 6am end -> 3am to 6am ignition
            #   - 8am start to 10am end -> 8am to 10 am end
            start_9am = datetime.datetime(start.year, start.month, start.day, 9)
            self._ig_start = max(start_9m, start)
            self._ig_end = self._ig_start + 3*self.ONE_HOUR

            # shift
            while (self._ig_end > self._end
                    and (self._ig_start - self.ONE_HOUR) >= self._start):
                self._ig_start -= self.ONE_HOUR
                self._ig_end -= self.ONE_HOUR

            # shrink
            self._ig_end  = min(self._ig_end, self._end)

    ## Rx

    def _compute_rx(self):
        # TODO: make sure start / end times are reasonable for rx?
        hourly_fractions = {
            "flaming": self._compute_rx_flaming(),
            "smoldering": self._compute_rx_smoldering()
        }
        hourly_fractions["residual"] = hourly_fractions["smoldering"] # TODO: ???
        return hourly_fractions

    def _compute_rx_flaming(self):
        """Computes the hourly flaming consumption rate based on equations
        (19) and (21) in the paper referenced above, which are as follows:

            area_i = area_j + (area_k - area_j) * ( (hour_i - hour_j) / (hour_k - hour_j) )
            consumption_rate_i = area_i - area_i-1

        Since we're assuming the entire area is consumed between ignition start
        and ignition end, and since we're assuming total area 1 (since we're
        only concerned with fractions per hour), we get

            consumption_hour_i = 1 / hours_of_ignition

        Which basically menas that the consumption (and by extension, emissions)
        is divided evenly over the hours of ignition.

        We just have to fill in hours outside of the ignition window with zeros.

        Note: partial ignition hours are supported
        """
        hourly_fractions = []
        total_ig_minutes = (self._ig_end - self._ig_end).minutes
        hr = self._start.to_date()
        while hr <= self._end:
            hr_end = hr + self.ONE_HOUR
            overlap_start = max(hr, self._ig_start)
            overlap_end = min(hr_end, self._ig_end)
            overlap_minutes = max(0, overlap_end - overlap_start)
            hourly_fractions += overlap_minutes / total_ig_minutes
            hr += self.ONE_HOUR

        return hourly_fractions

    def _compute_rx_smoldering(self):
        pass


"""
If I'm understanding things correctly, given equation (19)

    area_i = area_j + (area_k - area_j) * ( (hour_i - hour_j) / (hour_k - hour_j) )

For 9am-noon ignition time, we

    have hour_j == 9am
    hour_k == 12pm,
    area_j == 0
    area_k == total_area

which means (given total_area=1),


    area_i = area_j + (1 - area_j) * ( (hour_i - hour_j) / (3)


assigned to the active area for the day.  Then, given equation (12)

consumption_rate_i = area_i - area_i-1
"""