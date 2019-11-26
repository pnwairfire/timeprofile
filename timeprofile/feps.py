"""timeprofile.feps

FEPS timeprofile, as described in
https://www.fs.fed.us/pnw/fera/feps/FEPS_users_guide.pdf
"""

class FireType(object):

    RX = 'rx'
    WF = 'wf'


class FepsTimeProfiler(BaseTimeProfiler):

    def __init__(self, local_ignition_start_time, local_ignition_end_time,
            fire_type=FireType.RX):
        self._validate_start_end_times(local_ignition_start_time,
            local_ignition_end_time)

        self._local_ignition_start_time = local_ignition_start_time
        self._local_ignition_end_time = local_ignition_end_time

        # TODO: implement WF equation
        if fire_type == FireType.WF:
            raise NotImplementedError(
                "FEPS timeprofile not yet implemented for fire type WF")

        return getattr(self, '_compute_' + fire_type)()

    ## Validation Methods

    def _validate_start_end_times(self, local_ignition_start_time,
            local_ignition_end_time):
        # Super makes sure start < end
        super()._validate_start_end_times(local_ignition_start_time, local_ignition_end_time)

        # TODO: Make sure start and end are on the hour (i.e. minutes = 0) ?
        # TODO: Make sure start and end don't span midnight ???


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
        """Computes the hourly flaming consumption based on equations (19) and (21)
        in the paper referenced above, which are as follows:

            area_i = area_j + (area_k - area_j) * ( (hour_i - hour_j) / (hour_k - hour_j) )
            consumption_rate_i = area_i - area_i-1

        Since we're assuming the entire fire takes places between local_ignition_start_time
        and local_ignition_end_time, and since we're assuming total area 1 (since we're
        only concerned with fractions per hour), we get

            area_i = (hour_i - hour_j) / (hour_k - hour_j)
        """
        areas = []
        num_hours = (self._local_ignition_end_time
            - self._local_ignition_end_time).hours
        for i in range(num_hours):
            a = (1 - )
            areas.append(a)
            hr += self.ONE_HOUR

        #area_i = area_j + (area_k - area_j) * ( hour_idx / num_hours)
        #consumption_rate_i = area_i - area_i-1

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