"""timeprofile.feps

FEPS timeprofile, as described in
https://www.fs.fed.us/pnw/fera/feps/FEPS_users_guide.pdf
(referenced, below, as Anderson et. al.)

Notes on modifications made to the equstions in Anderson et. al.:

 - The equations for consumption rate in Anderson et. al. use total consumption,
   which FepsTimeProfiler does not use.  Any consumption value is replaced by 1.
 - For computing smoldering adjustment, FepsTimeProfiler takes a single
   relative humidity value, rather than hourly values.
 - FepsTimeProfiler assumes the following defaults not specified in
   Anderson et. al.
    - relative humidity = 65
    - wind speed = 5
    - duff moisture content = 70
   if not specified.  It also uses wind speed, which it defaults to 5
 - Because of the decay portion of the smoldering functions, the tail
   end of the time profile graph can extend beyond the specified fire
   activity end time FepsTimeProfiler simply cuts the tail end.
   It's up to the user to specify a large enough activity window to avoid
   cutting off a significant portion of the graph (e.g. midnight to midnight
   for a 9am-12pm ignition).
"""

import datetime
import math

from . import BaseTimeProfiler, InvalidStartEndTimesError

class FireType(object):

    RX = 'rx'
    WF = 'wf'


class FepsTimeProfiler(BaseTimeProfiler):

    # TODO: do we need fire_type?  can be inferred as rx if ignition times
    #   are defined

    DEFAULT_RELATIVE_HUMIDITY = 65
    DEFAULT_WIND_SPEED = 5
    DEFAULT_DUFF_MOISTURE_CONTENT = 70

    def __init__(self, local_start_time, local_end_time,
            local_ignition_start_time=None, local_ignition_end_time=None,
            fire_type=FireType.RX, relative_humidity=None, wind_speed=None,
            duff_moisture_content=None):

        self._set_times(local_start_time, local_end_time,
            local_ignition_start_time, local_ignition_end_time, fire_type)

        self._relative_humidity = (relative_humidity
            if relative_humidity is not None else self.DEFAULT_RELATIVE_HUMIDITY)
        self._wind_speed = (wind_speed
            if wind_speed is not None else self.DEFAULT_WIND_SPEED)
        self._duff_moisture_content = (duff_moisture_content
            if duff_moisture_content is not None else self.DEFAULT_DUFF_MOISTURE_CONTENT)

        # TODO: implement WF equation
        if fire_type == FireType.WF:
            raise NotImplementedError(
                "FEPS timeprofile not yet implemented for fire type WF")

        getattr(self, '_compute_' + fire_type)()

    ## Initialization

    def _set_times(self, start, end, ig_start, ig_end, fire_type):
        # Makes sure start < end
        self._validate_start_end_times(start, end)
        self._start = start
        self._end = end

        # TODO: should auto-setting of self._ig_start and self._ig_end
        #  be different for WF vs Rx?

        # fill in local_ignition_start_time and/or local_ignition_end_time
        # if necessary
        if ig_start and ig_end:
            self._validate_start_end_times(ig_start, ig_end,
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
            self._ig_start = max(start_9am, start)
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
        sa = self._compute_smoldering_adjustment()
        area_fractions = self._compute_rx_area_fractions()
        self.hourly_fractions = {
            "area_fraction": area_fractions,
            "flaming": self._normalize(
                self._compute_rx_flaming(area_fractions)),
            "smoldering": self._normalize(
                self._compute_rx_short_term_smoldering(area_fractions, sa)),
            "residual": self._normalize(
                self._compute_rx_long_term_smoldering(area_fractions, sa))
        }

        # TODO: normalize to make sure each set adds up to one

    def _normalize(self, fractions):
        total = sum(fractions)
        return [e / total for e in fractions]

    U_b = 3
    RH_b = 60

    def _compute_smoldering_adjustment(self):
        # TODO: refactor class to input hourly relative humitidy?
        return (math.floor(math.pow((self._wind_speed / self.U_b), 0.5))
            * ((100 / self._relative_humidity) / self.RH_b))


    def _compute_rx_area_fractions(self):
        """Computes the hourly area consumption rate based on equations
        (19) and (21) in Anderson et. al., which are as follows:

            area_i = area_j + (area_k - area_j) * ( (hour_i - hour_j) / (hour_k - hour_j) )
            consumption_rate_i = area_i - area_i-1

        Since we're assuming the entire area is consumed between ignition start
        and ignition end, and since we're assuming total area 1 (since we're
        only concerned with fractions per hour), we get

            consumption_hour_i = 1 / hours_of_ignition

        Which basically means that the area consumption is divided evenly
        over the hours of ignition.

        We just have to fill in hours outside of the ignition window with zeros.

        Note: partial ignition hours are supported
        """
        hourly_fractions = []
        total_ig_seconds = (self._ig_start - self._ig_end).total_seconds()
        hr = datetime.datetime(self._start.year, self._start.month,
            self._start.day)
        while hr < self._end:
            hr_end = hr + self.ONE_HOUR
            overlap_start = max(hr, self._ig_start)
            overlap_end = min(hr_end, self._ig_end)
            overlap_seconds = max(0, (overlap_end - overlap_start).total_seconds())
            hourly_fractions.append(overlap_seconds / total_ig_seconds)
            hr += self.ONE_HOUR

        return hourly_fractions

    K_TFLAM1 = 4 / 3  # TODO: allow user to provide custom val
    K_TFLAM2 = 8  # TODO: allow user to provide custom val
    N_TFLAM = 0.5  # TODO: allow user to provide custom val
    B_f = 20  # TODO: allow user to provide custom val
    D_f = math.sqrt(1/B_f)
    TFLAM = K_TFLAM1 * K_TFLAM2 * math.pow(D_f, N_TFLAM) / 60
    DECAY_f = 1 / math.pow(math.e, (1/TFLAM))

    def _compute_rx_flaming(self, area_fractions):
        """Computes hourly flaming phase consumption, as defined by
        a modification of equation (27) in Anderson et. al.  The original
        equation is as follows:

            CR_f_i = AR_i * (Inv_f / 100) * C_f * (1 - Decay_f) + (CR_f_i-1 * Decay_f)

        Since this computes absolute consumption values as opposed to relative
        fractions, which is what we want, we can remove (Inv_f / 100) * C_f
        to get:

            CR_f_i = AR_i * (1 - Decay_f) + (CR_f_i-1 * Decay_f)

        Where:

            Decay_f = 1 / e^(1/TFLAM)
            TFLAM = K_TFLAM1 * K_TFLAM2 * (D_f)^N_TFLAM / 60
            D_f = (C_f / B_f)^(1/2)
            K_TFLAM1 = 4 / 3
            K_TFLAM2 = 8
            N_TFLAM = 0.5
            B_f = 20

        Again removing C_f, D_f becomse

            D_f = (1/B_f)^(1/2)

        so that DECAY_f, TFLAM, and D_f can be defined as constants, above.
        """
        flaming_fractions = []
        for i, a in enumerate(area_fractions):
            prev = flaming_fractions[i-1] if i > 0 else 0.0
            f = a * (1 - self.DECAY_f) + prev * self.DECAY_f
            flaming_fractions.append(f)
        return flaming_fractions


    K_EDR1 = 8 / 3  # TODO: allow user to provide custom val
    K_EDR2 = 8  # TODO: allow user to provide custom val
    N_EDR = 0.5  # TODO: allow user to provide custom val
    B_STS = 12  # TODO: allow user to provide custom val
    D_STS = 1 / B_STS
    EDR = K_EDR1 * K_EDR2 * math.pow(D_STS, N_EDR) / 60
    DECAY_STS = 1 / math.pow(math.e, (1/EDR))

    def _compute_rx_short_term_smoldering(self, area_fractions, sa):
        """Computes hourly smoldering (i.e. Short Term Smoldering, STS)
        phase consumption, as defined by a modification of equation (28)
        in Anderson et. al.  The original is as follows

            CR_STS_i = SA * AR_i * (Inv_STS / 100) * C_STS * (1 - Decay_s) + (CR_STS_i-1 * Decay_s)

        As with flaming, since this computes absolute consumption values as
        opposed to relative fractions, which is wwhat we actually want,
        we can remove (Inv_STS / 100) * C_STS.

            CR_STS_i = SA * AR_i  * (1 - Decay_s) + (CR_STS_i-1 * Decay_s)

        Where

            Decay_s = 1 / e^(1/EDR)
            EDR = K_EDR1 * K_EDR2 * (D_STS)^N_EDR / 60
            D_STS = C_STS / B_STS
            K_EDR1 = 8 / 3
            K_EDR2 = 8
            N_EDR = 0.5
            B_STS = 12
            SA = floor((u_fh/u_b)^0.5) * ((100 - RH_4-) / RH_b)
            u_fh = wind_speed
            u_b = 3
            RH_4- = relative humidity 4 hours before the current hour
            RH_b = 60


        Again removing C_STS, D_STS becomse

            D_STS = 1 / B_STS

        so that DECAY_STS, EDR, and D_STS can be defined as constants, above.
        """
        sts_fractions = []

        for i, a in enumerate(area_fractions):
            prev = sts_fractions[i-1] if i > 0 else 0.0
            s = sa * a * (1 - self.DECAY_STS) + (prev * self.DECAY_STS)
            sts_fractions.append(s)

        return sts_fractions

    K_LTI = 1  # TODO: allow user to provide custom val
    M_DBM = 130  # TODO: allow user to provide custom val
    K_RDR = 12  # TODO: allow user to provide custom val

    def _compute_rx_long_term_smoldering(self, area_fractions, sa):
        """Computes hourly residual (i.e. Long Term Smoldering, LTS)
        phase consumption, as defined by a modification of equation (29)
        in Anderson et. al.  The original is as follows

            CR_LTS_i = SA * AR_i * (Inv_STS / 100) * C_LTS * (1 - Decay_l) + (CR_LTS_i-1 * Decay_l)

        As with flaming and smoldering, since this computes absolute
        consumption values as opposed to relative fractions, which is what
        we actually want, we can remove C_LTS.  (Note that consumption
        is *not* used in computing INV_LTS)

            CR_LTS_i = SA * AR_i * (Inv_STS / 100) * (1 - Decay_l) + (CR_LTS_i-1 * Decay_l)

        Where

            Decay_l = 1 / e^(1/RDR)
            RDR = k_RDR * Inv_LTS / [(1 - e^(-1)) / 100]
            Inv_LTS = 100 / e^(k_LTI * (M_Duff/M_DBM))
            k_LTI = 1
            M_Duff = duff moisture content
            M_DBM = 130
            k_RDR = 12
        """
        lts_fractions = []

        inv_lts = 100 / math.pow(math.e, self.K_LTI * (
            self._duff_moisture_content / self.M_DBM))
        rdr = self.K_RDR * inv_lts / ((1 - math.pow(math.e,-1)) / 100)
        decay_l = 1 / math.pow(math.e, 1 / rdr)

        for i, a in enumerate(area_fractions):
            prev = lts_fractions[i-1] if i > 0 else 0.0
            s = sa * a * (inv_lts / 100) * (1 - decay_l) + (prev * decay_l)
            lts_fractions.append(s)

        return lts_fractions


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