# timeprofile

This package provides a module for time profiling emissions output.

## Development

### Clone Repo

Via ssh:

    git clone git@github.com:pnwairfire/timeprofile.git

or http:

    git clone https://github.com/pnwairfire/timeprofile.git

### Install Dependencies

Run the following to install dependencies:

    pip install --trusted-host pypi.smoke.airfire.org -r requirements.txt

Run the following to install packages required for development and testing:

    pip install -r requirements-test.txt
    pip install -r requirements-dev.txt

### Setup Environment

To import timeprofile in development, you'll have to add the repo root directory
to the search path.

## Running tests

Use pytest:

    py.test

You can also use the ```--collect-only``` option to see a list of all tests.

    py.test --collect-only

See [pytest](http://pytest.org/latest/getting-started.html#getstarted) for more information about

## Installing

### Installing With pip

TODO: ...Fill In...

First, install pip (with sudo if necessary):

    apt-get install python-pip
    pip install --upgrade pip

Then, to install, for example, v0.1.0, use the following (with sudo if necessary):

    pip install --trusted-host pypi.smoke.airfire.org -i http://pypi.smoke.airfire.org/simple timeprofile==v0.1.0

If you get an error like

    AttributeError: 'NoneType' object has no attribute 'skip_requirements_regex

it means you need in upgrade pip.  One way to do so is with the following:

    pip install --upgrade pip

## Usage

Let's say you start with the following, abbreviated set of emissions output

    {
        'ground fuels': {
            'basal accumulations': {
                'flaming': {
                    'CO': [3.3815120047017005e-05,
                        0.012923999999999995
                    ]
                },
                'residual': {
                    'PM10': [4.621500211796271e-05, 0.0003925152]
                },
                'smoldering': {
                    'NH3': [6.424985839975172e-06, 0.0007844288]
                }
            },
        },
        'summary': {
            'ground fuels': {
                'flaming': {
                    'CO': [3.3815120047017005e-05,
                        0.012923999999999995
                    ]
                },
                'residual': {
                    'PM10': [4.621500211796271e-05, 0.0003925152]
                },
                'smoldering': {
                    'NH3': [6.424985839975172e-06, 0.0007844288]
                }
            },
            'litter-lichen-moss': {
                'flaming': {
                    'CO': [0.17116545599999997,
                        0.07897999999999998
                    ]
                },
                'residual': {
                    'PM10': [0.0, 0.0]
                },
                'smoldering': {
                    'NH3': [0.0009033891328, 0.00341056]
                }
            },
            'total': {
                'flaming': {
                    'CO': [0.1795595846677937, 0.09980199999999997]
                },
                'residual': {
                    'PM10': [0.005759220127912722, 0.006672758399999999]
                },
                'smoldering': {
                    'NH3': [0.0015054969384185898, 0.004604256]
                },
                'total': {
                    'CO': [0.1795595846677937, 0.09980199999999997],
                    'NH3': [0.0015054969384185898, 0.004604256],
                    'PM10': [0.005759220127912722, 0.006672758399999999]
                }
            },
        }
    }

The simplest case is when the emissions output are from a 24-hour period,
from midnight to midnight.  In this case, time profiling would yield the
following:

    ...FILL IN...

A more complicated scenario would be if the emissions are from a period of, say, 36 hours, starting at 6:00am on day and going until 6:00pm the following day.  Time profiling would yield the following:

    ...FILL IN...
