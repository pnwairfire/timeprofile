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


TODO: Refactor FepsTimeProfiler to optionally accept as input all fields
  (total consumption, duff consumption, hourly relative humidity, etc)
  mentioned in the equations in Anderson et. al.
"""

import datetime
import math

from . import BaseTimeProfiler, InvalidStartEndTimesError

__all__ = [
    'FireType', 'MoistureCategoryFactors', 'FepsTimeProfiler'
]


class FireType(object):

    RX = 'rx'
    WF = 'wf'

    VALID_FIRE_TYPES = (RX, WF)


class MoistureCategoryFactors(object):

    _FACTORS = {
        "verydry": {'canopy': 0.33, 'shrub': 0.25, 'grass': 0.125, 'duff': 0.33},
        "dry": {'canopy': 0.5, 'shrub': 0.33, 'grass': 0.25, 'duff': 0.5},
        "moderate": {'canopy': 1, 'shrub': 0.5, 'grass': 1, 'duff': 1},
        "moist": {'canopy': 2, 'shrub': 1, 'grass': 2, 'duff': 2},
        "wet": {'canopy': 4, 'shrub': 2, 'grass': 4, 'duff': 4},
        "verywet": {'canopy': 5, 'shrub': 4, 'grass': 5, 'duff': 5 }
    }

    def __init__(self, moisture_category):
        self._factors = self._get(self._FACTORS, moisture_category, 'moisture')

    def get(self, fuel_category):
        return self._get(self._factors, fuel_category, 'fuel')
    __call__ = get

    def _get(self, d, key, label):
        k = key and key.lower()

        if k not in d:
            raise ValueError(
                "Invalid {} category: {}".format(label, key))

        return d[k]


class FepsTimeProfiler(BaseTimeProfiler):

    ## Constants

    # for smoldiering adjustment
    U_b = 3  # TODO: allow user to provide custom val
    RH_b = 60  # TODO: allow user to provide custom val

    # for computing flaming phase consumption
    K_CAG = 0.5  # TODO: allow user to provide custom val
    K_CBG = 0.2  # TODO: allow user to provide custom val

    # for flaming fractions
    K_AGI = 1  # TODO: allow user to provide custom val
    C_TI = 10  # TODO: allow user to provide custom val
    K_TFLAM1 = 4 / 3  # TODO: allow user to provide custom val
    K_TFLAM2 = 8  # TODO: allow user to provide custom val
    N_TFLAM = 0.5  # TODO: allow user to provide custom val
    B_f = 20  # TODO: allow user to provide custom val
    D_f = math.sqrt(1/B_f)
    TFLAM = K_TFLAM1 * K_TFLAM2 * math.pow(D_f, N_TFLAM) / 60
    DECAY_f = 1 / math.pow(math.e, (1/TFLAM))


    DEFAULT_RELATIVE_HUMIDITY = 65
    DEFAULT_WIND_SPEED = 5
    DEFAULT_DUFF_MOISTURE_CONTENT = 70


    # TODO: do we need fire_type?  can be inferred as rx if ignition times
    #   are defined

    def __init__(self, local_start_time, local_end_time,
            total_above_ground_consumption,
            total_below_ground_consumption,
            local_ignition_start_time=None, local_ignition_end_time=None,
            fire_type=FireType.RX, relative_humidity=None, wind_speed=None,
            duff_moisture_content=None):

        self._set_times(local_start_time, local_end_time,
            local_ignition_start_time, local_ignition_end_time)

        self._set_fire_type(fire_type)

        self._total_above_ground_consumption = total_above_ground_consumption
        self._total_below_ground_consumption = total_below_ground_consumption
        self._total_consumption = (self._total_above_ground_consumption +
            self._total_below_ground_consumption)

        self._relative_humidity = (relative_humidity
            if relative_humidity is not None else self.DEFAULT_RELATIVE_HUMIDITY)
        self._wind_speed = (wind_speed
            if wind_speed is not None else self.DEFAULT_WIND_SPEED)
        self._duff_moisture_content = (duff_moisture_content
            if duff_moisture_content is not None else self.DEFAULT_DUFF_MOISTURE_CONTENT)

        # fire type only comes into play for computing area fractions
        self._compute_area_fractions()
        self._compute_flaming_phase_involvement()
        self._compute_flaming_phase_consumption()
        self._compute_smoldering_adjustment()
        self._compute_hourly_fractions()


    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def ignition_start(self):
        return self._ig_start

    @property
    def ignition_end(self):
        return self._ig_end

    @property
    def hourly_fractions(self):
        return self._hourly_fractions


    ## Initialization

    def _set_times(self, start, end, ig_start, ig_end):
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

    def _set_fire_type(self, fire_type):
        fire_type = fire_type.lower()

        if fire_type not in FireType.VALID_FIRE_TYPES:
            raise ValueError("Invalid fire type: '{}'.  Valid: '{}')".format(fire_type,
                "', '".join(FireType.VALID_FIRE_TYPES)))

        self._fire_type = fire_type

    ## Computations

    def _compute_flaming_phase_involvement(self):
        self._inv_f = 100 * (1 - self.K_AGI * math.pow(
            math.e, -self._total_above_ground_consumption / self.C_TI))

    def _compute_flaming_phase_consumption(self):
        """Computes flaming phase consumption, C_f

        where

            C_f = k_CAG * C_AG + k_CBG * C_BG
            k_CAG (Above ground flaming phase consumption coefficient) = 0.5
            k_CBG (Below ground flaming phase consumption coefficient) = 0.2
        """
        self._c_f = (self.K_CAG * self._total_above_ground_consumption +
            self.K_CBG * self._total_below_ground_consumption)


    def _compute_smoldering_adjustment(self):
        # TODO: refactor class to input hourly relative humitidy?
        self._smoldering_adjustment = (
            math.floor(math.pow((self._wind_speed / self.U_b), 0.5))
            * ((100 / self._relative_humidity) / self.RH_b))

    def _compute_area_fractions(self):
        """Computes the hourly area consumption rate based on equations
        (19), (20), and (21) in Anderson et. al.  Equation (19) and (20)
        compute cumulative area at each hour for rx and wf, respectively,
        and (21) then computes the per-hour area.

            area_i = area_j + (area_k - area_j) * ((hour_i - hour_j) / (hour_k - hour_j))
            area_i = area_j + (area_k - area_j) * ((hour_i - hour_j)^2 / (hour_k - hour_j)^2)
            consumption_rate_i = area_i - area_i-1

        Since we're assuming the entire area is consumed between ignition start
        and ignition end, and since we're assuming total area 1 (since we're
        only concerned with fractions per hour as opposed to absolute area
        values), (19) and (20) become

            area_i = (hour_i - hour_j) / (hour_k - hour_j)
            area_i = (hour_i - hour_j)^2 / (hour_k - hour_j)^2

        Where area_i is inclusive of the hour starting at hour 1
        (e.g. if ignition starts is at 9am, area_9am is
        hour_10am - hour_9am == 1h; if ignition starts is at 9:30am,
        area_9am is hour_10am - hour_9:30am == 30m)

        For Rx, this basically means that the area consumption is divided
        evenly over the hours of ignition for.  For wf, the growth is
        exponential.

        We just have to fill in hours outside of the ignition window with zeros.

        Note: partial ignition hours are supported
        """
        cumulative_area = []
        total_ig_seconds = (self._ig_end - self._ig_start).total_seconds()
        hr = datetime.datetime(self._start.year, self._start.month,
            self._start.day)
        final_hr = self._end.date()
        cumulative_seconds = 0
        while hr < self._end:
            hr_end = hr + self.ONE_HOUR
            overlap_start = max(hr, self._ig_start)
            overlap_end = min(hr_end, self._ig_end)
            overlap_seconds = max(0, (overlap_end - overlap_start).total_seconds())
            cumulative_seconds += overlap_seconds
            if self._fire_type == FireType.RX:
                cumulative_area.append(cumulative_seconds / total_ig_seconds)
            else:
                cumulative_area.append(
                    math.pow(cumulative_seconds, 2) / math.pow(total_ig_seconds, 2))
            hr += self.ONE_HOUR

        self._area_fractions = []
        num_hours = len(cumulative_area)
        for i in range(num_hours):
            prev_val = cumulative_area[i-1] if i > 0 else 0.0
            a = cumulative_area[i] - prev_val
            self._area_fractions.append(a)

    def _compute_hourly_fractions(self):
        # TODO: make sure start / end times are reasonable for rx?
        self._hourly_fractions = {
            "area_fraction": self._area_fractions,
            "flaming": self._normalize(self._compute_flaming()),
            "smoldering": self._normalize(self._compute_short_term_smoldering()),
            "residual": self._normalize(self._compute_long_term_smoldering())
        }

        # TODO: normalize to make sure each set adds up to one

    def _normalize(self, fractions):
        total = sum(fractions)
        return [e / total for e in fractions]


    def _compute_flaming(self):
        """Computes hourly flaming phase consumption, as defined by
        a modification of equation (27) in Anderson et. al.  The original
        equation is as follows:

            CR_f_i = AR_i * (Inv_f / 100) * C_f * (1 - Decay_f) + (CR_f_i-1 * Decay_f)

        Where:

            Inv_f = 100 * (1 - k_AGI * e^(-C_AG / C_TI))
            k_AGI (Flame involvement sensitivity coefficient) = 1
            C_AG = total above ground consumption
            C_TI (Consumption threshold for total flame involvement) = 10
            C_f = Flaming phase consumption (see _compute_flaming_phase_consumption)
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

        # TODO: come up with appropriate name for the following variable
        temp = (self._inv_f / 100) * self._c_f * (1 - self.DECAY_f)

        for i, a in enumerate(self._area_fractions):
            prev = flaming_fractions[i-1] if i > 0 else 0.0
            f = a * temp + prev * self.DECAY_f
            flaming_fractions.append(f)

        return flaming_fractions


    K_EDR1 = 8 / 3  # TODO: allow user to provide custom val
    K_EDR2 = 8  # TODO: allow user to provide custom val
    N_EDR = 0.5  # TODO: allow user to provide custom val
    B_STS = 12  # TODO: allow user to provide custom val
    D_STS = 1 / B_STS
    EDR = K_EDR1 * K_EDR2 * math.pow(D_STS, N_EDR) / 60
    DECAY_STS = 1 / math.pow(math.e, (1/EDR))

    def _compute_short_term_smoldering(self):
        """Computes hourly smoldering (i.e. Short Term Smoldering, STS)
        phase consumption, as defined by a modification of equation (28)
        in Anderson et. al.  The original is as follows

            CR_STS_i = SA * AR_i * (Inv_STS / 100) * C_STS * (1 - Decay_s) + (CR_STS_i-1 * Decay_s)

        Where

            Inv_STS = Inv_f
            C_STS = min(C_f, C_total - C_f)
            C_f = Flaming phase consumption (see _compute_flaming_phase_consumption)
            C_total = total_consumption
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

        # TODO: come up with appropriate name for the following variable
        c_sts = min(self._c_f, self._total_consumption - self._c_f)
        temp = self._smoldering_adjustment * (self._inv_f / 100) * c_sts * (1 - self.DECAY_STS)

        for i, a in enumerate(self._area_fractions):
            prev = sts_fractions[i-1] if i > 0 else 0.0
            s = temp * a + (prev * self.DECAY_STS)
            sts_fractions.append(s)

        return sts_fractions

    K_LTI = 1  # TODO: allow user to provide custom val
    M_DBM = 130  # TODO: allow user to provide custom val
    K_RDR = 12  # TODO: allow user to provide custom val

    def _compute_long_term_smoldering(self):
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
        # TODO: come up with appropriate name for the following variable
        temp = self._smoldering_adjustment * (inv_lts / 100) * (1 - decay_l)

        for i, a in enumerate(self._area_fractions):
            prev = lts_fractions[i-1] if i > 0 else 0.0
            s = temp * a + (prev * decay_l)
            lts_fractions.append(s)

        return lts_fractions
