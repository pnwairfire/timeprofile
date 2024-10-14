# timeprofile

This package provides a module for time profiling emissions output.

***This software is provided for research purposes only. It's output may
not accurately reflect observed data due to numerous reasons. Data are
provisional; use at own risk.***

## Python 2 and 3 Support

This package was originally developed to support python 2.7, but has since
been refactored to support 3.5. Attempts to support both 2.7 and 3.5 have
been made but are not guaranteed.

## Development

### Clone Repo

Via ssh:

    git clone git@github.com:pnwairfire/timeprofile.git

or http:

    git clone https://github.com/pnwairfire/timeprofile.git

### Install Dependencies

Run the following to install dependencies:

    pip install -r requirements.txt
    pip install -r requirements-test.txt
    pip install -r requirements-dev.txt

### Setup Environment

To import timeprofile in development, you'll have to add the repo root directory
to the search path.

## Running tests

Use pytest:

    pytest

You can also use the ```--collect-only``` option to see a list of all tests.

    pytest --collect-only

See [pytest](http://pytest.org/latest/getting-started.html#getstarted) for more information about

## Installing

### Installing With pip

TODO: ...Fill In...

First, install pip (with sudo if necessary):

    apt-get install python-pip
    pip install --upgrade pip

Then, to install, for example, v2.0.0, use the following (with sudo if necessary):

    pip install --extra-index https://pypi.airfire.org/simple timeprofile==2.0.0

If you get an error like

    AttributeError: 'NoneType' object has no attribute 'skip_requirements_regex

it means you need in upgrade pip.  One way to do so is with the following:

    pip install --upgrade pip

## Usage

A timeprofiler object is instantiated from each class with a start time, an end time, and class specific kwargs. e.g.

    import datetime
    from timeprofile.feps import FepsTimeProfiler
    from timeprofile.static import StaticTimeProfiler

    feps_profiler = FepsTimeProfiler(
        datetime.datetime(2015, 1, 20, 0, 0),
        datetime.datetime(2015, 1, 20, 2, 0)
    )
    static_profiler = StaticTimeProfiler(
        datetime.datetime(2015, 1, 20, 0, 0),
        datetime.datetime(2015, 1, 20, 2, 0)
    )

The houly fractions are then accessed like in the following:

    feps_profiler.hourly_fractions
    static_profiler.hourly_fractions

The hourly fractions are structured as follows:

    {
        'area_fraction': [0.5, 0.5],
        'flaming': [0.4999982946232187, 0.5000017053767812],
        'smoldering': [0.4999853212474072, 0.5000146787525928],
        'residual': [0.34884662785022885, 0.6511533721497711]
    }


A simple case is when the time window is a 24-hour period,
from midnight to midnight.  In this case, FEPS time profiler, with no
input other than start and end times, would yield the following:

    {
        'area_fraction': [
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3333333333333333,
            0.3333333333333333, 0.33333333333333337, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        ],
        'flaming': [
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.33333105948986946,
            0.3333333333178222, 0.33333333333333326, 2.2738434638226057e-06,
            1.551109229390636e-11, 1.0580938748774452e-16, 7.21781952450244e-22,
            4.923657524652319e-27, 3.3586879441595006e-32, 2.29113918865406e-37,
            1.562907560648659e-42, 1.066142142401966e-47, 7.272721026019621e-53,
            4.961108750765986e-58, 3.3842354118727117e-63
        ],
        'smoldering': [
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3333137610886173,
            0.33333333218411504, 0.3333333333332659, 1.9572244716002987e-05,
            1.1492182896695533e-09, 6.747834479257037e-14, 3.962108031933841e-18,
            2.326420439767974e-22, 1.365998104783779e-26, 8.020694756528947e-31,
            4.7094900170153494e-35, 2.765258733018484e-39, 1.6236696187713928e-43,
            9.533657734961823e-48, 5.597852466819759e-52
        ],
        'residual': [
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.051448039171003226,
            0.09603235783914513, 0.1346686499725634, 0.11670240696693489,
            0.10113305357000935, 0.08764081898749726, 0.0759485932804565,
            0.06581623594940489, 0.05703564381438533, 0.049426476892755915,
            0.04283245449074733, 0.03711814543615242, 0.03216618652841821,
            0.027874872077343852, 0.024156065023182394
        ]
    }


A more complicated scenario would be a time window of, say, 36 hours, starting at 6:00am on one day and going until 6:00pm the following day.  Time profiling would yield the following:

    {
        'area_fraction': [
            0.0, 0.0, 0.0, 0.3333333333333333, 0.3333333333333333,
            0.33333333333333337, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        ],

        'flaming': [
            0.0, 0.0, 0.0, 0.33333105948986946, 0.3333333333178222,
            0.33333333333333326, 2.2738434638226057e-06, 1.551109229390636e-11,
            1.0580938748774452e-16, 7.21781952450244e-22, 4.923657524652319e-27,
            3.3586879441595006e-32, 2.29113918865406e-37, 1.562907560648659e-42,
            1.066142142401966e-47, 7.272721026019621e-53, 4.961108750765986e-58,
            3.3842354118727117e-63, 2.3085664713971314e-68,
            1.5747956345359157e-73, 1.0742516281337596e-78, 7.328040129398227e-84,
            4.998844845258577e-89, 3.4099772034163633e-94, 2.326126312731716e-99,
            1.5867741336692376e-104, 1.0824227977219723e-109,
            7.383780011078057e-115, 5.036867974948155e-120,
            3.4359147968919804e-125, 2.343819720949262e-130,
            1.5988437458577015e-135, 1.090656120357656e-140,
            7.439943871660133e-146, 5.0751803231344345e-151,
            3.462049681644101e-156
        ],
        'smoldering': [
            0.0, 0.0, 0.0, 0.3333137610886173, 0.33333333218411504,
            0.3333333333332659, 1.9572244716002987e-05, 1.1492182896695533e-09,
            6.747834479257037e-14, 3.962108031933841e-18, 2.326420439767974e-22,
            1.365998104783779e-26, 8.020694756528947e-31, 4.7094900170153494e-35,
            2.765258733018484e-39, 1.6236696187713928e-43, 9.533657734961823e-48,
            5.597852466819759e-52, 3.2868761509409844e-56, 1.929946331322718e-60,
            1.1332014565622418e-64, 6.653788866111515e-69, 3.906887519285308e-73,
            2.293996758160961e-77, 1.3469599778535882e-81, 7.908909092765317e-86,
            4.6438531260076585e-90, 2.7267188942224726e-94, 1.601040284084463e-98,
            9.400785672085916e-103, 5.519834330903922e-107,
            3.241066449488041e-111, 1.9030483707065912e-115,
            1.1174078525360314e-119, 6.561053981226903e-124,
            3.852436623465138e-128
        ],
        'residual': [
            0.0, 0.0, 0.0, 0.04493321743817599, 0.08387186150175081,
            0.11761567260532799, 0.10192447977219064, 0.08832666044168927,
            0.07654293612504742, 0.06633128708076667, 0.05748198159792448,
            0.049813268426419595, 0.04316764388324648, 0.037408616966849474,
            0.032417906039934975, 0.028093009504878263, 0.024345100577099568,
            0.021097202918262496, 0.01828260965958067, 0.015843513344380375,
            0.013729818651027107, 0.011898113511354143, 0.010310777492933436,
            0.008935209132719325, 0.007743156352675472, 0.00671013620514235,
            0.005814932030399268, 0.005039157698803528, 0.004366879987704225,
            0.0037842913373279546, 0.0032794262645409267, 0.002841915610058338,
            0.0024627735717131145, 0.002134213149771912, 0.0018494862138263748,
            0.0016027449064773057
        ]
    }


Another complicated scenario would be a time window of, say, 2.75 hours, starting at 6:30am and going until 9:15pm the same day.  Time profiling would yield the following:

    {
        'area_fraction': [
            0.0, 0.4444444444444444, 0.4444444444444444, 0.11111111111111116
        ],
        'flaming': [
            0.0, 0.4444417495260068, 0.44444478129890846, 0.1111134691750847
        ],
        'smoldering': [
            0.0, 0.4444212482396549, 0.44444734320393753, 0.11113140855640749
        ],
        'residual': [
            0.0, 0.21123091541981814, 0.39428136005072595, 0.39448772452945596
        ]
    }

Note that there are four hourly fractions, since the time profile overlaps
with four hours of the day - the hours starting at 6, 7, 8, and 9.
